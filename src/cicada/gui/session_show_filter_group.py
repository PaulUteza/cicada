import sys
from qtpy.QtWidgets import *
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt
import os
from pynwb import NWBHDF5IO
from functools import partial
from cicada.preprocessing.utils import sort_by_param, group_by_param
import cicada.preprocessing.utils as utils
import yaml
import datetime
from itertools import islice
from cicada.gui.cicada_analysis_tree_gui import AnalysisTreeApp
from random import randint


# TODO : Quand des éléments à sort ont des None, les griser

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.createActions()
        self.createMenus()
        self.labels = []
        self.setWindowTitle("CICADA")
        screenGeometry = QApplication.desktop().screenGeometry()
        # making sure the window is not bigger than the dimension of the screen
        width_window = min(959, screenGeometry.width())
        height_window = min(650, screenGeometry.height())
        self.resize(width_window, height_window)
        self.param_list = []
        self.param_group_list = []
        self.grouped = False
        self.sorted = False
        # contains the data, if nwb format will contains instance of Nwb class
        # the key is the identifier of the data file, value is the instance
        self.data_dict = dict()
        # self.setStyleSheet(
        #     "#menuWidget { "
        #     " border-image: url(\"cicada/gui/icons/rc/cicada_background.jpg\") 0 0 0 0 stretch stretch;"
        #     "}")
        # self.setStyleSheet(
        #     "#menuWidget { "
        #     " background-image: url(\"cicada/gui/icons/rc/cicada_background.jpg\"); background-position: center;"
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


    def load_data_from_config(self):
        """
        Check if the last dir opened is saved in config and load it automatically
        :return:
        """
        config_file_name = "cicada/config/config.yaml"
        if os.path.isfile(config_file_name):
            with open(config_file_name, 'r') as stream:
                config_dict = yaml.safe_load(stream)
        if (config_dict is not None) and config_dict.get("dir_name"):
            self.load_data_from_dir(dir_name=config_dict["dir_name"])

    def open(self):
        self.labels = []
        self.grouped_labels = []
        options = QFileDialog.Options()
        dir_name = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.load_data_from_dir(dir_name=dir_name)

    def load_data_from_dir(self, dir_name):
        """
        Load data from a dir
        :param dir_name:
        :return:
        """
        # TODO: deal with the different format
        # TODO: decide if we should add those nwb to the ones already opened (if that's the case)
        #  or erase the ones present and replace them by the new one.
        #  probably best to have 2 options on the menu open new, and something like add data
        self.labels = []
        file_names = []
        self.nwb_path_list = []
        # look for filenames in the first directory, if we don't break, it will go through all directories
        for (dirpath, dirnames, local_filenames) in os.walk(dir_name):
            file_names.extend(local_filenames)
            break
        for file_name in file_names:
            if file_name.endswith(".nwb"):
                self.nwb_path_list.append(os.path.join(dir_name, file_name))
                io = NWBHDF5IO(os.path.join(dir_name, file_name), 'r')
                nwb_file = io.read()
                self.data_dict[nwb_file.identifier] = nwb_file
                self.labels.append(nwb_file.identifier)
            elif file_name.endswith(".yaml") or file_name.endswith(".yml"):
                self.yaml_path = os.path.join(dir_name, file_name)
                with open(os.path.join(dir_name, file_name), 'r') as stream:
                    self.data = yaml.safe_load(stream)
                self.grouped = True
                self.grouped_labels = []
                for value in self.data.values():
                    nwb_file_list = []
                    for file in value:
                        print(self.nwb_path_list)
                        self.nwb_path_list.append(os.path.join(dir_name, file))
                        io = NWBHDF5IO(os.path.join(dir_name, file), 'r')
                        nwb_file = io.read()
                        self.data_dict[nwb_file.identifier] = nwb_file
                        nwb_file_list.append(nwb_file.identifier)
                    self.grouped_labels.append(nwb_file_list)
                self.showGroupMenu.setEnabled(True)
                self.populate_menu()
        # self.openWindow()
        # checking there is at least one data file loaded
        if len(self.data_dict) > 0:
            self.musketeers_widget.session_widget.populate(self.labels)
            self.sortMenu.setEnabled(True)
            self.groupMenu.setEnabled(True)
            # then we save the last location opened in the yaml file in config
            self.save_last_data_location(dir_name=dir_name)

    def save_last_data_location(self, dir_name):
        # TODO think about where to keep the config yaml file
        config_file_name = "cicada/config/config.yaml"
        config_dict = None
        if os.path.isfile(config_file_name):
            with open(config_file_name, 'r') as stream:
                config_dict = yaml.load(stream, Loader=yaml.FullLoader)
        if config_dict is None:
            config_dict = dict()
        config_dict["dir_name"] = dir_name
        with open(config_file_name, 'w') as outfile:
            yaml.dump(config_dict, outfile, default_flow_style=False)

    def populate_menu(self):
        counter =0
        if len(self.data.keys()) > 10:
            populate_data_keys = list(islice(self.data, 10))
        else:
            populate_data_keys = list(self.data)
        for group_name in populate_data_keys:
            print(group_name)
            counter +=1
            exec('self.groupAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupAct' + str(counter) + '.triggered.connect(partial(self.load_group, group_name))')
            self.showGroupMenu.addAction(eval('self.groupAct' + str(counter)))

    def load_group(self, group_name):
        self.sorted = False
        self.grouped = False
        self.nwb_path_list = self.data.get(group_name)
        self.labels = []
        for path in self.nwb_path_list:
            io = NWBHDF5IO(path, 'r')
            nwb_file = io.read()
            self.labels.append(nwb_file.identifier)
        if self.session_widget.exists:
            print("ok")
            self.session_widget.populate(self.labels)
        else:
            self.openWindow()

    def createMenus(self):

        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        # self.fileMenu.addAction(self.showSessionAct)
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.viewMenu = QMenu("&View", self)


        self.sortMenu = QMenu("Sort by",self.viewMenu, enabled=False)
        self.groupMenu = QMenu("Group by", self.viewMenu, enabled=False)

        self.showGroupMenu = QMenu("Load Group", self.fileMenu, enabled=False)
        self.fileMenu.addMenu(self.showGroupMenu)
        self.viewMenu.addMenu(self.groupMenu)
        self.viewMenu.addMenu(self.sortMenu)

        # Add filters to "Sort by"
        self.ageSort = QCheckBox("&Age", self.sortMenu)
        self.ageSortAct = QWidgetAction(self.sortMenu)
        self.ageSortAct.setDefaultWidget(self.ageSort)
        self.sortMenu.addAction(self.ageSortAct)
        self.ageSort.stateChanged.connect(partial(self.on_sort,"age"))

        self.sexSort = QCheckBox("&Sex", self.sortMenu)
        self.sexSortAct = QWidgetAction(self.sortMenu)
        self.sexSortAct.setDefaultWidget(self.sexSort)
        self.sortMenu.addAction(self.sexSortAct)
        self.sexSort.stateChanged.connect(partial(self.on_sort,"sex"))

        self.genotypeSort = QCheckBox("&Genotype", self.sortMenu)
        self.genotypeSortAct = QWidgetAction(self.sortMenu)
        self.genotypeSortAct.setDefaultWidget(self.genotypeSort)
        self.sortMenu.addAction(self.genotypeSortAct)
        self.genotypeSort.stateChanged.connect(partial(self.on_sort,"genotype"))

        self.speciesSort = QCheckBox("&Species", self.sortMenu)
        self.speciesSortAct = QWidgetAction(self.sortMenu)
        self.speciesSortAct.setDefaultWidget(self.speciesSort)
        self.sortMenu.addAction(self.speciesSortAct)
        self.speciesSort.stateChanged.connect(partial(self.on_sort,"species"))

        self.subjectIDSort = QCheckBox("&Subject ID", self.sortMenu)
        self.subjectIDSortAct = QWidgetAction(self.sortMenu)
        self.subjectIDSortAct.setDefaultWidget(self.subjectIDSort)
        self.sortMenu.addAction(self.subjectIDSortAct)
        self.subjectIDSort.stateChanged.connect(partial(self.on_sort,"subject_id"))

        self.weightSort = QCheckBox("&Weight", self.sortMenu)
        self.weightSortAct = QWidgetAction(self.sortMenu)
        self.weightSortAct.setDefaultWidget(self.weightSort)
        self.sortMenu.addAction(self.weightSortAct)
        self.weightSort.stateChanged.connect(partial(self.on_sort,"weight"))

        self.birthSort = QCheckBox("&Birth", self.sortMenu)
        self.birthSortAct = QWidgetAction(self.sortMenu)
        self.birthSortAct.setDefaultWidget(self.birthSort)
        self.sortMenu.addAction(self.birthSortAct)
        self.birthSort.stateChanged.connect(partial(self.on_sort,"birth"))

        self.sortMenu.addSeparator()

        self.fluorescenceSort = QCheckBox("&Has fluorescence", self.sortMenu)
        self.fluorescenceSortAct = QWidgetAction(self.sortMenu)
        self.fluorescenceSortAct.setDefaultWidget(self.fluorescenceSort)
        self.sortMenu.addAction(self.fluorescenceSortAct)
        self.fluorescenceSort.stateChanged.connect(partial(self.on_sort,"fluorescence"))

        self.imagesegSort = QCheckBox("&Has image segmentation", self.sortMenu)
        self.imagesegSortAct = QWidgetAction(self.sortMenu)
        self.imagesegSortAct.setDefaultWidget(self.imagesegSort)
        self.sortMenu.addAction(self.imagesegSortAct)
        self.imagesegSort.stateChanged.connect(partial(self.on_sort,"imagesegmentation"))

        self.rasterSort = QCheckBox("&Has rasterplot", self.sortMenu)
        self.rasterSortAct = QWidgetAction(self.sortMenu)
        self.rasterSortAct.setDefaultWidget(self.rasterSort)
        self.sortMenu.addAction(self.rasterSortAct)
        self.rasterSort.stateChanged.connect(partial(self.on_sort,"raster"))

        # Add filters to "Group by"
        self.ageGroupAct = QAction("Age", self, checkable=True)
        self.groupMenu.addAction(self.ageGroupAct)
        self.ageGroupAct.triggered.connect(partial(self.uncheck_all_group, "age"))
        self.ageGroupAct.triggered.connect(partial(self.on_group, "age"))

        self.sexGroupAct = QAction("Sex", self, checkable=True)
        self.groupMenu.addAction(self.sexGroupAct)
        self.sexGroupAct.triggered.connect(partial(self.uncheck_all_group, "sex"))
        self.sexGroupAct.triggered.connect(partial(self.on_group, "sex"))

        self.genotypeGroupAct = QAction("Genotype", self, checkable=True)
        self.groupMenu.addAction(self.genotypeGroupAct)
        self.genotypeGroupAct.triggered.connect(partial(self.uncheck_all_group, "genotype"))
        self.genotypeGroupAct.triggered.connect(partial(self.on_group, "genotype"))

        self.speciesGroupAct = QAction("Species", self, checkable=True)
        self.groupMenu.addAction(self.speciesGroupAct)
        self.speciesGroupAct.triggered.connect(partial(self.uncheck_all_group, "species"))
        self.speciesGroupAct.triggered.connect(partial(self.on_group, "species"))

        self.subjectIDGroupAct = QAction("Subject ID", self, checkable=True)
        self.groupMenu.addAction(self.subjectIDGroupAct)
        self.subjectIDGroupAct.triggered.connect(partial(self.uncheck_all_group, "subjectID"))
        self.subjectIDGroupAct.triggered.connect(partial(self.on_group, "subject_id"))

        self.weightGroupAct = QAction("Weight", self, checkable=True)
        self.groupMenu.addAction(self.weightGroupAct)
        self.weightGroupAct.triggered.connect(partial(self.uncheck_all_group, "weight"))
        self.weightGroupAct.triggered.connect(partial(self.on_group, "weight"))

        self.birthGroupAct = QAction("Birth", self, checkable=True)
        self.groupMenu.addAction(self.birthGroupAct)
        self.birthGroupAct.triggered.connect(partial(self.uncheck_all_group, "birth"))
        self.birthGroupAct.triggered.connect(partial(self.on_group, "birth"))

        self.groupMenu.addSeparator()

        self.fluorescenceGroupAct = QAction("Has fluorescence", self, checkable=True)
        self.groupMenu.addAction(self.fluorescenceGroupAct)
        self.fluorescenceGroupAct.triggered.connect(partial(self.uncheck_all_group, "fluorescence"))
        self.fluorescenceGroupAct.triggered.connect(partial(self.on_group, "fluorescence"))

        self.imagesegGroupAct = QAction("Has image segmentation", self, checkable=True)
        self.groupMenu.addAction(self.imagesegGroupAct)
        self.imagesegGroupAct.triggered.connect(partial(self.uncheck_all_group, "imageseg"))
        self.imagesegGroupAct.triggered.connect(partial(self.on_group, "imagesegmentation"))

        self.rasterGroupAct = QAction("Has raster", self, checkable=True)
        self.groupMenu.addAction(self.rasterGroupAct)
        self.rasterGroupAct.triggered.connect(partial(self.uncheck_all_group, "raster"))
        self.rasterGroupAct.triggered.connect(partial(self.on_group, "raster"))

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def createActions(self):

        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)
        # self.showSessionAct = QAction("&Show session", self, triggered=self.openWindow)
        self.showGroupAct = QAction("&Show all groups", self)


    def uncheck_all_sort(self):
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

    def uncheck_all_group(self, param=''):
        self.param_group_list = []
        param_value_list = ['age', 'sex', 'species', 'raster', 'genotype', 'subjectID', 'weight', 'birth', 'fluorescence',
                'imageseg', 'raster']
        for value in param_value_list:
            if value is not param:
                eval('self.' + value +'GroupAct.setChecked(False)')


    def on_group(self, param, state):
        if state > 0:
            self.uncheck_all_sort()
            self.sorted = False
            if param not in self.param_group_list:
                self.param_group_list.append(param)
        else:
            if param in self.param_group_list:
                if len(self.param_group_list) == 1:
                    self.param_group_list = []
                else:
                    self.param_group_list.remove(param)
        self.grouped_labels, param_group_list = utils.group_by_param(self.nwb_path_list, self.param_group_list)
        print(self.grouped_labels)
        self.dict_group = dict()
        for i in range(len(self.grouped_labels)):
            self.dict_group.update({param_group_list[i]: self.grouped_labels[i]})
        self.grouped = True
        self.musketeers_widget.session_widget.form_group(self.grouped_labels, param_group_list)

    def on_sort(self, param, state):
        if state > 0:
            self.grouped = False
            self.uncheck_all_group()
            if param not in self.param_list:
                self.param_list.append(param)
        else:
            if param in self.param_list:
                if len(self.param_list) == 1:
                    self.param_list = []
                else:
                    self.param_list.remove(param)
        self.sorted_labels = utils.sort_by_param(self.nwb_path_list, self.param_list)
        self.sorted = True
        self.musketeers_widget.session_widget.populate(self.sorted_labels)

    def about(self):
        QMessageBox.about(self, "About CICADA","Lorem Ipsum")


    def openWindow(self):
        # self.showSessionAct.setEnabled(False)
        self.musketeers_widget = MusketeersWidget(parent=self)
        self.setCentralWidget(self.musketeers_widget)

class SessionsListWidget(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)
        self.special_background_on = False

    def keyPressEvent(self, event):
        available_background = ["michou_BG.jpg", "michou_BG2.jpg"]
        if event.key() == QtCore.Qt.Key_M:
            if self.special_background_on:
                self.setStyleSheet(
                    "background-image:url(\"\"); background-position: center;")
                self.special_background_on = False
            else:
                pic_index = randint(0, len(available_background) - 1)
                self.setStyleSheet(
                    f"background-image:url(\"cicada/gui/icons/rc/{available_background[pic_index]}\"); "
                    f"background-position: center; "
                    f"background-repeat:no-repeat;")
                self.special_background_on = True


class SessionsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.exists = True
        self.setWindowTitle('Sessions :')
        self.resize(500, 500)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.layout = QVBoxLayout()
        self.q_list = SessionsListWidget()
        self.parent = parent
        self.q_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.layout.addWidget(self.q_list)
        self.items = []
        if self.parent.grouped:
            self.form_group(self.parent.grouped_labels)
        elif self.parent.sorted:
            self.populate(self.parent.sorted_labels)
        else:
            self.populate(self.parent.labels)
        self.q_list.itemSelectionChanged.connect(self.on_change)
        self.create_group = QPushButton("Create groups", self)
        self.create_group.clicked.connect(self.save_group)
        self.run_analysis_button = QPushButton("Push me and then just touch me", self)
        self.run_analysis_button.clicked.connect(self.send_data_to_analysis_tree)
        self.layout.addWidget(self.run_analysis_button)
        self.layout.addWidget(self.create_group)
        self.setLayout(self.layout)
        self.analysis_tree = None

    def on_change(self):
        self.items = [item.text() for item in self.q_list.selectedItems()]

    def get_items(self):
        return [data for key, data in self.parent.data_dict.items() if key in self.items]

    def send_data_to_analysis_tree(self):
        data_to_analyse = self.get_items()
        # TODO: deal with the fact the data might not be in nwb format
        self.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def populate(self, labels):
        self.q_list.clear()
        self.q_list.insertItems(0, labels)

    def form_group(self, labels, param=["-"]):
        print(labels)
        self.q_list.clear()
        while len(param) < len(labels):
            param.append("-")
        for group in labels:
            item = QListWidgetItem()  # delimiter
            if param[0] is None:
                param[0] = "-"
            item.setText('--------------------------' + str(param.pop(0)) + '---------------------------')
            item.setFlags(QtCore.Qt.NoItemFlags)  # item should not be selectable
            self.q_list.addItem(item)
            for file in group:
                print(file)
                item = QListWidgetItem()
                item.setText(str(file))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.q_list.addItem(item)

    def save_group(self):
        self.nameBox = QDialog(self)
        self.nameBoxLayout = QVBoxLayout(self.nameBox)
        # self.nameBox.resize(50,200)
        self.nameBox.setWindowTitle("Save your group as")
        self.save_name = QLineEdit(self.nameBox)
        self.save_name.setText("Group_" + str(datetime.date.today()))
        self.saveButton = QPushButton('Save')
        self.nameBoxLayout.addWidget(self.save_name)
        self.nameBoxLayout.addWidget(self.saveButton)
        self.nameBox.show()
        self.saveButton.clicked.connect(self.save_group_names)
        self.saveButton.clicked.connect(self.nameBox.close)

    def save_group_names(self):
        name = self.save_name.text()
        group_to_save = []
        if self.q_list.selectedItems():
            print("Selected")
            for item in self.get_items():
                for path in self.parent.nwb_path_list:
                    if path.endswith(item + ".nwb"):
                        group_to_save.append(path)
            self.parent.data.update({name: group_to_save})
        elif self.parent.grouped:
            counter = 0
            print("Grouped :", self.parent.grouped_labels)
            for group in self.parent.grouped_labels:
                counter +=1

                group_to_save = []
                for item in group:
                    for path in self.parent.nwb_path_list:
                        if path.endswith(item + ".nwb"):
                            group_to_save.append(path)

                try:
                    print('try ',self.parent.dict_group)
                    for key, value in self.parent.dict_group.items():
                        print(value,group)
                        if value == group:
                            if key:
                                id_group = key
                            else:
                                id_group = str(counter)
                except AttributeError:
                    print("Except")
                    id_group = str(counter)
                print(name,id_group)
                self.parent.data.update({str(name + '_' + id_group): group_to_save})
        else:
            print("Sorted")
            for item in self.parent.labels:
                for path in self.parent.nwb_path_list:
                    if path.endswith(item + ".nwb"):
                        group_to_save.append(path)
            self.parent.data.update({name: group_to_save})
        with open(self.parent.yaml_path, 'w') as stream:
            yaml.dump(self.parent.data, stream, default_flow_style=True)

    def closeEvent(self, QCloseEvent):
        self.exists = False
        self.parent.showSessionAct.setEnabled(True)
        self.parent.sortMenu.setEnabled(False)
        self.parent.groupMenu.setEnabled(False)


class MusketeersWidget(QWidget):
    """
    Gather in a layout the 3 main sub-windows composing the gui: displaying the subject sessions,
    the analysis tree and the parameters for the analysis.
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.layout = QHBoxLayout()
        self.session_widget = SessionsWidget(parent)
        self.layout.addWidget(self.session_widget)
        analysis_tree_app = AnalysisTreeApp()
        self.session_widget.analysis_tree = analysis_tree_app
        self.layout.addWidget(analysis_tree_app)
        self.setLayout(self.layout)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    cicada = MainWindow()
    cicada.show()
    sys.exit(app.exec_())
