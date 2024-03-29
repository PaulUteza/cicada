from qtpy.QtWidgets import *
from qtpy import QtGui
from qtpy import QtCore
import os
from copy import deepcopy
from pynwb import NWBHDF5IO
import sys
from functools import partial
import cicada.preprocessing.utils as utils
import yaml
from cicada.gui.cicada_analysis_tree_gui import AnalysisTreeApp
from cicada.gui.cicada_analysis_overview import AnalysisOverview
from cicada.gui.cicada_analysis_parameters_gui import AnalysisPackage
from cicada.gui.session_show_filter_group import SessionsWidget


class CicadaMainWindow(QMainWindow):
    """Main window of the GUI"""
    def __init__(self):
        super().__init__()
        self.createActions()
        self.createMenus()
        self.object_created = []
        self.to_close = []
        self.labels = []
        self.setWindowTitle("CICADA")

        screenGeometry = QApplication.desktop().screenGeometry()
        # making sure the window is not bigger than the dimension of the screen
        width_window = min(1400, screenGeometry.width())
        height_window = min(640, screenGeometry.height())
        self.resize(width_window, height_window)
        self.param_list = []
        self.param_group_list = []
        self.grouped = False
        self.sorted = False
        self.nwb_path_list = dict()
        # contains the data, if nwb format will contains instance of Nwb class
        # the key is the identifier of the data file, value is the instance
        self.data_dict = dict()
        # self.setStyleSheet(
        #     "#menuWidget { "
        #     " border-image: url(\"cicada/gui/icons/rc/cicada_background.jpg\") 0 0 0 0 stretch stretch;"
        #     "}")
        # self.setStyleSheet(
        #     "#menuWidget { "
        #     " background-image: url(\"cicada/gui/icons/rc/neurons_stock_footage.jpg\"); background-position: center;"
        #     "}")
        self.menuWidget().setStyleSheet(
            "background-image:url(\"cicada/gui/icons/rc/sky_night.jpeg\"); background-position: center;")
        # first we check if there is a last known location opened, then we load those files again:
        #TODO: in the future, save the data displayed in the gui, that might come from different dir
        # self.yaml_path = os.path.join(dir_name, file_name)
        # with open(os.path.join(dir_name, file_name), 'r') as stream:
        #     self.data = yaml.safe_load(stream)

        self.openWindow()
        self.load_data_from_config()


    def load_group_from_config(self):
        """Load groups from a YAML file in the config folder"""

        group_file_name = "cicada/config/group.yaml"
        if os.path.isfile(group_file_name):
            self.group_data = dict()
            with open(group_file_name, 'r') as stream:
                self.group_data = yaml.safe_load(stream)
            self.all_groups = deepcopy(self.group_data)
            if self.group_data:
                keys_to_del = []
                for key, value in self.group_data.items():
                    missing_file = False
                    for file in value:
                        if file not in self.nwb_path_list.values():
                            missing_file = True
                    if missing_file:
                        keys_to_del.append(key)
                for key in keys_to_del:
                    self.group_data.pop(key)
            self.grouped_labels = []
            if self.group_data:
                self.grouped = True
                for value in self.group_data.values():
                    nwb_file_list = []
                    for file in value:
                        io = NWBHDF5IO(file, 'r')
                        nwb_file = io.read()
                        self.data_dict[nwb_file.identifier] = nwb_file
                        nwb_file_list.append(nwb_file.identifier)
                    self.grouped_labels.append(nwb_file_list)
                self.showGroupMenu.setEnabled(True)
                self.addGroupDataMenu.setEnabled(True)
                self.populate_menu()
            else:
                self.showGroupMenu.setEnabled(False)
                self.addGroupDataMenu.setEnabled(False)
                self.showGroupMenu.clear()
                self.addGroupDataMenu.clear()


    def load_data_from_config(self):
        """Check if the last dir opened is saved in config and load it automatically"""

        config_file_name = "cicada/config/config.yaml"
        config_dict = None
        self.labels = []
        self.to_add_labels = []
        if os.path.isfile(config_file_name):
            with open(config_file_name, 'r') as stream:
                config_dict = yaml.safe_load(stream)
                print(f"config_dict {config_dict}")
        if (config_dict is not None) and config_dict.get("dir_name"):
            self.load_data_from_dir(dir_name=config_dict["dir_name"], method='clear')


    def open_new_dataset(self):
        """Open a directory"""

        self.labels = []
        self.to_add_labels = []
        self.nwb_path_list = dict()
        self.grouped_labels = []
        QFileDialog.Options()
        dir_name = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.load_data_from_dir(dir_name=dir_name, method='clear')

    def add_data(self):
        """Open a directory"""

        self.to_add_labels = []
        QFileDialog.Options()
        dir_name = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.load_data_from_dir(dir_name=dir_name, method='add')


    def load_data_from_dir(self, dir_name, method):
        """
        Load data (currently only NWB) from selected directory

        Args:
            dir_name (str): Path to data
            method (str): String to choose whether to add data to the existing dataset or open a new one,
             takes two values : 'add' or 'clear'

        """

        # TODO: deal with the different format
        # TODO: decide if we should add those nwb to the ones already opened (if that's the case)
        #  or erase the ones present and replace them by the new one.
        #  probably best to have 2 options on the menu open new, and something like add data
        file_names = []
        # look for filenames in the first directory, if we don't break, it will go through all directories
        for (dirpath, dirnames, local_filenames) in os.walk(dir_name):
            file_names.extend(local_filenames)
            break
        for file_name in file_names:
            if file_name.endswith(".nwb"):
                io = NWBHDF5IO(os.path.join(dir_name, file_name), 'r')
                nwb_file = io.read()
                self.data_dict[nwb_file.identifier] = nwb_file
                self.nwb_path_list[nwb_file.identifier] = os.path.join(dir_name, file_name)
                self.to_add_labels.append(nwb_file.identifier)
        self.labels = self.labels + self.to_add_labels
        # checking there is at least one data file loaded
        if len(self.data_dict) > 0:
            if method == 'clear':
                self.musketeers_widget.session_widget.populate(self.labels, method)
                self.load_group_from_config()
            else:
                self.musketeers_widget.session_widget.populate(self.to_add_labels, method)
            self.sortMenu.setEnabled(True)
            self.groupMenu.setEnabled(True)
            # then we save the last location opened in the yaml file in config
            self.save_last_data_location(dir_name=dir_name)

    def save_last_data_location(self, dir_name):
        """
        Keep path to last data directory selected in a YAML in config

        Args:
            dir_name (str): Path to data to be saved

        """
        # TODO think about where to keep the config yaml file
        config_file_name = "cicada/config/config.yaml"
        config_dict = None
        if os.path.isfile(config_file_name):
            with open(config_file_name, 'r') as stream:
                config_dict = yaml.safe_load(stream)
        if config_dict is None:
            config_dict = dict()
        config_dict["dir_name"] = dir_name
        with open(config_file_name, 'w') as outfile:
            yaml.dump(config_dict, outfile, default_flow_style=False)

    def populate_menu(self):
        """Populate the menu to load groups"""
        # TODO : Performance issue ?
        self.showGroupMenu.clear()
        self.addGroupDataMenu.clear()
        counter = 0
        for group_name in self.group_data.keys():
            counter +=1
            exec('self.groupAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupAct' + str(counter) + '.triggered.connect(partial(self.load_group, group_name))')
            exec('self.groupAddAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupAddAct' + str(counter) + '.triggered.connect(partial(self.add_group_data, group_name))')
            self.showGroupMenu.addAction(eval('self.groupAct' + str(counter)))
            self.addGroupDataMenu.addAction(eval('self.groupAddAct' + str(counter)))

    def load_group(self, group_name):
        """
        Load a group of saved sessions, it will clear the current session list

        Args:
            group_name (str) : Name of the group saved in YAML

        """
        self.sorted = False
        self.grouped = False
        self.nwb_path_list = dict()
        self.labels = []
        for path_list in {group_name: self.all_groups.get(group_name)}.values():
            for path in path_list:
                io = NWBHDF5IO(path, 'r')
                nwb_file = io.read()
                self.labels.append(nwb_file.identifier)
                self.nwb_path_list.update({nwb_file.identifier: path})
        self.musketeers_widget.session_widget.populate(self.labels)
        self.musketeers_widget.session_widget.update_text_filter()
        self.groupMenu.setEnabled(True)
        self.sortMenu.setEnabled(True)

    def add_group_data(self, group_name):
        """
        Add a group of saved sessions to the current list of session

        Args:
            group_name (str) : Name of the group saved in YAML

        """
        self.sorted = False
        self.grouped = False
        self.labels_to_add = []
        for path in self.all_groups.get(group_name):
            io = NWBHDF5IO(path, 'r')
            nwb_file = io.read()
            # self.labels.append(nwb_file.identifier)
            self.nwb_path_list.update({nwb_file.identifier: path})
            self.labels_to_add.append(nwb_file.identifier)
        self.musketeers_widget.session_widget.populate(self.labels_to_add, 'add')
        self.musketeers_widget.session_widget.update_text_filter()
        self.groupMenu.setEnabled(True)
        self.sortMenu.setEnabled(True)


    def createMenus(self):
        """Create menu bar and put some menu in it"""

        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.addAct)
        self.fileMenu.addSeparator()
        # self.fileMenu.addAction(self.showSessionAct)
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.viewMenu = QMenu("&View", self)

        self.sortMenu = QMenu("Sort by", self.viewMenu, enabled=False)
        self.groupMenu = QMenu("Group by", self.viewMenu, enabled=False)

        self.showGroupMenu = QMenu("Load Group", self.fileMenu, enabled=False)
        self.addGroupDataMenu = QMenu('Add Group', self.fileMenu, enabled=False)
        self.fileMenu.addMenu(self.showGroupMenu)
        self.fileMenu.addMenu(self.addGroupDataMenu)
        self.fileMenu.addAction(self.seeAllGroupAct)
        self.viewMenu.addMenu(self.groupMenu)
        self.viewMenu.addMenu(self.sortMenu)

        # Add filters to "Sort by"
        self.create_sort_menu()
        self.sortMenu.addAction(self.ageSortAct)
        self.sortMenu.addAction(self.sexSortAct)
        self.sortMenu.addAction(self.genotypeSortAct)
        self.sortMenu.addAction(self.speciesSortAct)
        self.sortMenu.addAction(self.subjectIDSortAct)
        self.sortMenu.addAction(self.weightSortAct)
        self.sortMenu.addAction(self.birthSortAct)
        self.sortMenu.addSeparator()

        self.sortMenu.addAction(self.fluorescenceSortAct)
        self.sortMenu.addAction(self.imagesegSortAct)
        self.sortMenu.addAction(self.rasterSortAct)

        # Add filters to "Group by"
        self.create_group_menu()
        self.groupMenu.addAction(self.ageGroupAct)
        self.groupMenu.addAction(self.sexGroupAct)
        self.groupMenu.addAction(self.genotypeGroupAct)
        self.groupMenu.addAction(self.speciesGroupAct)
        self.groupMenu.addAction(self.subjectIDGroupAct)
        self.groupMenu.addAction(self.weightGroupAct)
        self.groupMenu.addAction(self.birthGroupAct)

        self.groupMenu.addSeparator()

        self.groupMenu.addAction(self.fluorescenceGroupAct)
        self.groupMenu.addAction(self.imagesegGroupAct)
        self.groupMenu.addAction(self.rasterGroupAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def create_group_menu(self):
        """Create group menu"""

        self.ageGroupAct = QAction("Age", self, checkable=True)
        self.ageGroupAct.triggered.connect(partial(self.uncheck_group, "age"))
        self.ageGroupAct.triggered.connect(partial(self.on_group, "age"))

        self.sexGroupAct = QAction("Sex", self, checkable=True)
        self.sexGroupAct.triggered.connect(partial(self.uncheck_group, "sex"))
        self.sexGroupAct.triggered.connect(partial(self.on_group, "sex"))

        self.genotypeGroupAct = QAction("Genotype", self, checkable=True)
        self.genotypeGroupAct.triggered.connect(partial(self.uncheck_group, "genotype"))
        self.genotypeGroupAct.triggered.connect(partial(self.on_group, "genotype"))

        self.speciesGroupAct = QAction("Species", self, checkable=True)
        self.speciesGroupAct.triggered.connect(partial(self.uncheck_group, "species"))
        self.speciesGroupAct.triggered.connect(partial(self.on_group, "species"))

        self.subjectIDGroupAct = QAction("Subject ID", self, checkable=True)
        self.subjectIDGroupAct.triggered.connect(partial(self.uncheck_group, "subjectID"))
        self.subjectIDGroupAct.triggered.connect(partial(self.on_group, "subject_id"))

        self.weightGroupAct = QAction("Weight", self, checkable=True)
        self.weightGroupAct.triggered.connect(partial(self.uncheck_group, "weight"))
        self.weightGroupAct.triggered.connect(partial(self.on_group, "weight"))

        self.birthGroupAct = QAction("Birth", self, checkable=True)
        self.birthGroupAct.triggered.connect(partial(self.uncheck_group, "birth"))
        self.birthGroupAct.triggered.connect(partial(self.on_group, "birth"))

        self.fluorescenceGroupAct = QAction("Has fluorescence", self, checkable=True)
        self.fluorescenceGroupAct.triggered.connect(partial(self.uncheck_group, "fluorescence"))
        self.fluorescenceGroupAct.triggered.connect(partial(self.on_group, "fluorescence"))

        self.imagesegGroupAct = QAction("Has image segmentation", self, checkable=True)
        self.imagesegGroupAct.triggered.connect(partial(self.uncheck_group, "imageseg"))
        self.imagesegGroupAct.triggered.connect(partial(self.on_group, "imagesegmentation"))

        self.rasterGroupAct = QAction("Has raster", self, checkable=True)
        self.rasterGroupAct.triggered.connect(partial(self.uncheck_group, "raster"))
        self.rasterGroupAct.triggered.connect(partial(self.on_group, "raster"))


    def create_sort_menu(self):
        """Create sort menu"""

        self.ageSort = QCheckBox("&Age", self.sortMenu)
        self.ageSortAct = QWidgetAction(self.sortMenu)
        self.ageSortAct.setDefaultWidget(self.ageSort)
        self.ageSort.stateChanged.connect(partial(self.on_sort,"age"))

        self.sexSort = QCheckBox("&Sex", self.sortMenu)
        self.sexSortAct = QWidgetAction(self.sortMenu)
        self.sexSortAct.setDefaultWidget(self.sexSort)
        self.sexSort.stateChanged.connect(partial(self.on_sort,"sex"))

        self.genotypeSort = QCheckBox("&Genotype", self.sortMenu)
        self.genotypeSortAct = QWidgetAction(self.sortMenu)
        self.genotypeSortAct.setDefaultWidget(self.genotypeSort)
        self.genotypeSort.stateChanged.connect(partial(self.on_sort,"genotype"))

        self.speciesSort = QCheckBox("&Species", self.sortMenu)
        self.speciesSortAct = QWidgetAction(self.sortMenu)
        self.speciesSortAct.setDefaultWidget(self.speciesSort)
        self.speciesSort.stateChanged.connect(partial(self.on_sort,"species"))

        self.subjectIDSort = QCheckBox("&Subject ID", self.sortMenu)
        self.subjectIDSortAct = QWidgetAction(self.sortMenu)
        self.subjectIDSortAct.setDefaultWidget(self.subjectIDSort)
        self.subjectIDSort.stateChanged.connect(partial(self.on_sort,"subject_id"))

        self.weightSort = QCheckBox("&Weight", self.sortMenu)
        self.weightSortAct = QWidgetAction(self.sortMenu)
        self.weightSortAct.setDefaultWidget(self.weightSort)
        self.weightSort.stateChanged.connect(partial(self.on_sort,"weight"))

        self.birthSort = QCheckBox("&Birth", self.sortMenu)
        self.birthSortAct = QWidgetAction(self.sortMenu)
        self.birthSortAct.setDefaultWidget(self.birthSort)
        self.birthSort.stateChanged.connect(partial(self.on_sort,"birth"))


        self.fluorescenceSort = QCheckBox("&Has fluorescence", self.sortMenu)
        self.fluorescenceSortAct = QWidgetAction(self.sortMenu)
        self.fluorescenceSortAct.setDefaultWidget(self.fluorescenceSort)
        self.fluorescenceSort.stateChanged.connect(partial(self.on_sort,"fluorescence"))

        self.imagesegSort = QCheckBox("&Has image segmentation", self.sortMenu)
        self.imagesegSortAct = QWidgetAction(self.sortMenu)
        self.imagesegSortAct.setDefaultWidget(self.imagesegSort)
        self.imagesegSort.stateChanged.connect(partial(self.on_sort,"imagesegmentation"))

        self.rasterSort = QCheckBox("&Has rasterplot", self.sortMenu)
        self.rasterSortAct = QWidgetAction(self.sortMenu)
        self.rasterSortAct.setDefaultWidget(self.rasterSort)
        self.rasterSort.stateChanged.connect(partial(self.on_sort,"raster"))


    def createActions(self):
        """Create some QAction"""

        self.openAct = QAction("&Open new dataset...", self, shortcut="Ctrl+O", triggered=self.open_new_dataset)
        self.addAct = QAction("&Add data to current dataset...", self, shortcut="Ctrl+P", triggered=self.add_data)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.exitAct.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)
        # self.showSessionAct = QAction("&Show session", self, triggered=self.openWindow)
        self.showGroupAct = QAction("&Show all groups", self)
        self.seeAllGroupAct = QAction('&See all groups', self, triggered=self.see_all_groups)


    def see_all_groups(self):
        """Display a widget with all existing groups"""
        self.all_group_window = AllGroups(self)
        self.all_group_window.show()
        self.object_created.append(self.all_group_window)

    def uncheck_all_sort(self):
        """Uncheck all checkboxes in sort menu"""

        self.param_list = []
        self.ageSort.setChecked(False)
        self.sexSort.setChecked(False)
        self.speciesSort.setChecked(False)
        self.genotypeSort.setChecked(False)
        self.subjectIDSort.setChecked(False)
        self.weightSort.setChecked(False)
        self.birthSort.setChecked(False)
        self.fluorescenceSort.setChecked(False)
        self.imagesegSort.setChecked(False)
        self.rasterSort.setChecked(False)

    def uncheck_group(self, param=''):
        """
        Uncheck group menu parameter

        Args:
            param (str): Parameter name to uncheck

        """
        self.param_group_list = []
        param_value_list = ['age', 'sex', 'species', 'raster', 'genotype', 'subjectID', 'weight', 'birth', 'fluorescence',
                'imageseg', 'raster']
        for value in param_value_list:
            if value is not param:
                eval('self.' + value +'GroupAct.setChecked(False)')


    def on_group(self, param, state):
        """
        Give group list and parameters value to populate QListWidget

        Args:
            param (str): Parameter to group by
            state (int): State of the checkbox

        """
        self.grouped = True
        if state > 0:  # From unchecked to checked
            self.sorted = False
            self.uncheck_all_sort()
            self.musketeers_widget.session_widget.update_text_filter(param)
            if param not in self.param_group_list:
                self.param_group_list.append(param)
            self.grouped_labels, param_group_list = utils.group_by_param(self.nwb_path_list.values(), self.param_group_list)
            self.dict_group = dict()
            for i in range(len(self.grouped_labels)):
                self.dict_group.update({param_group_list[i]: self.grouped_labels[i]})
            self.musketeers_widget.session_widget.form_group(self.grouped_labels, param_group_list)
        else:  # From checked to unchecked
            if param in self.param_group_list:
                if len(self.param_group_list) == 1:
                    self.param_group_list = []
                else:
                    self.param_group_list.remove(param)
            self.grouped = False
            self.musketeers_widget.session_widget.update_text_filter()
            self.musketeers_widget.session_widget.populate(self.labels)

    def on_sort(self, param, state):
        """
        Give sorted list to populate QListWidget
        Args:
            param (str): Parameter to sort by
            state (int): State of the checkbox

        """
        if state > 0:  # From unchecked to checked
            self.grouped = False
            self.uncheck_group()
            if param not in self.param_list:
                self.param_list.append(param)
        else:  # From checked to unchecked
            if param in self.param_list:
                if len(self.param_list) == 1:
                    self.param_list = []
                else:
                    self.param_list.remove(param)
        self.sorted_labels = utils.sort_by_param(self.nwb_path_list.values(), self.param_list)
        if self.param_list:
            self.sorted = True
        else:
            self.sorted = False
        self.musketeers_widget.session_widget.update_text_filter()
        self.musketeers_widget.session_widget.populate(self.sorted_labels)

    def about(self):
        """Small about QMessageBox for the project"""
        QMessageBox.about(self, "About CICADA", "Always compassionately illuminate the one yogi.")


    def openWindow(self):
        """Open all widgets in a CentralWidget and call some menus that needed those widgets"""
        # self.showSessionAct.setEnabled(False)
        self.musketeers_widget = MusketeersWidget(parent=self)
        self.setCentralWidget(self.musketeers_widget)
        self.saveGroupMenu = QAction('Save Group', self.fileMenu)
        self.fileMenu.addAction(self.saveGroupMenu)
        self.saveGroupMenu.triggered.connect(self.musketeers_widget.session_widget.save_group)

    def closeEvent(self, event):
        """
        Close all analysises windows on main window close
        (uses Garbage Collector to get a list of them and close them, might be a better and faster way)
        """

        self.object_created = utils.flatten(self.object_created)
        copied_list = self.object_created.copy()
        for obj in copied_list:
            if isinstance(obj, AnalysisPackage):
                obj.close()
            else:
                obj.close()
                self.to_close.remove(obj)
                self.object_created.remove(obj)

        if self.object_created:
            event.ignore()
        else:
            self.close()


class AllGroups(QWidget):
    """Class containing the widget used to display all created group found"""
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.setWindowTitle("See all groups")
        self.group_list = QListWidget(self)
        self.populate_list()
        self.group_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.group_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.group_list.customContextMenuRequested.connect(self.showContextMenu)
        self.group_list.doubleClicked.connect(self.double_click_event)
        self.layout.addWidget(self.group_list)
        self.hlayout = QHBoxLayout()
        self.load_button = QPushButton('Load group')
        self.load_button.clicked.connect(self.load_group)
        self.add_button = QPushButton('Add group')
        self.add_button.clicked.connect(self.add_group)
        self.hlayout.addWidget(self.load_button)
        self.hlayout.addWidget(self.add_button)
        self.layout.addLayout(self.hlayout)
        self.setLayout(self.layout)

    def populate_list(self):
        """Populate the list containing all existing groups"""
        counter = 0
        for group_name in self.parent.all_groups.keys():
            counter += 1
            exec('self.groupItem' + str(counter) + ' = QListWidgetItem()')
            eval('self.groupItem' + str(counter) + '.setText("' + group_name + '")')
            self.group_list.addItem(eval('self.groupItem' + str(counter)))

    def double_click_event(self, clicked_item):
        """
        Get item which was double clicked and call the function to load the group

        Args:
            clicked_item (QModelIndex): Qt index which correspond to the clicked index
        """
        item = self.group_list.item(clicked_item.row())
        self.parent.load_group(item.text())

    def add_group(self):
        """Add all selected groups to the current session list"""
        items = self.group_list.selectedItems()
        for item in items:
            self.parent.add_group_data(item.text())

    def load_group(self):
        """Load all selected groups in the session list (clear the existing sessions from the list)"""
        items = self.group_list.selectedItems()
        counter = 0
        for item in items:
            if counter == 0:
                self.parent.load_group(item.text())
            else:
                self.parent.add_group_data(item.text())
            counter += 1

    def showContextMenu(self, pos):
        """
        Display a context menu at the cursor position. Allow the user to add or load the group at the given position.

        Args:
            pos (QPoint): Coordinate of the cursor


        """
        self.global_pos = self.mapToGlobal(pos)
        self.context_menu = QMenu()
        self.context_menuAct = QAction("Load group", self, triggered=self.load_group)
        self.context_menuAct.setIcon(QtGui.QIcon('cicada/gui/icons/svg/question-mark.svg'))
        self.context_menu.addAction(self.context_menuAct)
        self.context_menuAct = QAction("Add group", self, triggered=self.load_group)
        self.context_menuAct.setIcon(QtGui.QIcon('cicada/gui/icons/svg/question-mark.svg'))
        self.context_menu.addAction(self.context_menuAct)
        self.context_menu.exec(self.global_pos)

class MusketeersWidget(QWidget):
    """
    Gather in a layout the 3 main sub-windows composing the gui: displaying the subject sessions,
    the analysis tree and an overview of the running analysis
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        to_analysis_button = QPushButton()
        to_analysis_button.setProperty("cicada", "True")

        self.session_widget = SessionsWidget(parent=parent, to_analysis_button=to_analysis_button)
        self.layout.addWidget(self.session_widget)

        self.layout.addWidget(to_analysis_button)

        to_parameters_button = QPushButton()
        to_parameters_button.setProperty("cicada", "True")

        analysis_tree_app = AnalysisTreeApp(parent=parent, to_parameters_button=to_parameters_button)

        self.session_widget.analysis_tree = analysis_tree_app
        self.layout.addWidget(analysis_tree_app)

        self.layout.addWidget(to_parameters_button)

        # analysis_param_widget = AnalysisParametersApp()
        analysis_overview_widget = AnalysisOverview(parent)
        analysis_tree_app.analysis_overview = analysis_overview_widget
        self.layout.addWidget(analysis_overview_widget)
        # analysis_tree_app.arguments_section_widget = analysis_param_widget
        # useful to empty the arguments section when we click on the to_analysis_button
        # self.session_widget.arguments_section_widget = analysis_param_widget
        self.session_widget.analysis_overview_widget = analysis_overview_widget
        self.setLayout(self.layout)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    cicada = CicadaMainWindow()
    cicada.show()
    sys.exit(app.exec_())
