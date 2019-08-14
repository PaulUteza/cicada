import sys
from qtpy.QtWidgets import *
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt
import os
from pynwb import NWBHDF5IO
from functools import partial
from cicada.preprocessing.utils import sort_by_param, group_by_param
import cicada.preprocessing.utils as utils
from cicada.gui.metadata_widget import MetaDataWidget
import yaml
import datetime
from random import randint


class SessionsListWidget(QListWidget):

    def __init__(self, session_widget):
        QListWidget.__init__(self)
        self.special_background_on = False
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.session_widget = session_widget
        self.arguments_section_widget = None

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
        elif event.key() == QtCore.Qt.Key_Return:
            data_to_analyse = self.session_widget.get_data_to_analyse()
            self.session_widget.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def showContextMenu(self, pos):
        self.global_pos = self.mapToGlobal(pos)
        self.context_menu = QMenu()
        self.context_menuAct = QAction("Show info", self, triggered=self.show_info)
        self.context_menuAct.setIcon(QtGui.QIcon('cicada/gui/icons/svg/question-mark.svg'))
        self.context_menu.addAction(self.context_menuAct)
        self.context_menu.exec(self.global_pos)

    def show_info(self):
        item_list = self.selectedItems()
        for item in item_list:
            exec('self.' + item.text() + '_metadata = '
                                         'MetaDataWidget(self.session_widget.parent.nwb_path_list.get(item.text()),'
                                         ' "nwb")')
            self.session_widget.parent.object_created.append(eval('self.' + item.text() + '_metadata'))

class SessionsWidget(QWidget):

    def __init__(self, parent=None, to_analysis_button=None):

        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.check_menu()
        self.sort_menu()
        self.group_menu()
        self.textLabel = QLabel()
        self.textLabel.setTextInteractionFlags(Qt.NoTextInteraction)
        self.hlayout.addWidget(self.textLabel)
        self.more_menu()

        self.q_list = SessionsListWidget(session_widget=self)
        self.q_list.doubleClicked.connect(self.double_click_event)
        self.q_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # connecting the button that will fill the analysis tree
        # TODO: see to deactivate until the tree is loaded
        if to_analysis_button:
            to_analysis_button.clicked.connect(self.send_data_to_analysis_tree)

        self.layout.addWidget(self.q_list)
        self.items = []
        if self.parent.grouped:
            self.form_group(self.parent.grouped_labels)
        elif self.parent.sorted:
            self.populate(self.parent.sorted_labels)
        else:
            self.populate(self.parent.labels)
        self.q_list.itemSelectionChanged.connect(self.on_change)
        self.hlayout2.addLayout(self.layout)
        self.setLayout(self.hlayout2)
        self.analysis_tree = None

    def double_click_event(self, clicked_item):
        """
        Handle double click on item in QListWidget.
        Check or uncheck an item or a group on double click.

        Args:
            clicked_item: Double clicked item

        Returns:

        """
        flags = clicked_item.flags()
        if flags & 1:  # Item is selectable, meaning it is a session
            if self.q_list.item(clicked_item.row()).checkState():
                self.q_list.item(clicked_item.row()).setCheckState(QtCore.Qt.Unchecked)
            else:
                self.q_list.item(clicked_item.row()).setCheckState(QtCore.Qt.Checked)
        else:  # Item is not selectable, meaning it is a separator
            row_index = clicked_item.row() + 1
            item_is_selectable = True
            while item_is_selectable:
                if self.q_list.item(row_index).checkState():
                    self.q_list.item(row_index).setCheckState(QtCore.Qt.Unchecked)
                else:
                    self.q_list.item(row_index).setCheckState(QtCore.Qt.Checked)
                try:
                    if not self.q_list.item(row_index + 1).flags() & 1:
                        item_is_selectable = False
                    row_index += 1
                except AttributeError:
                    item_is_selectable = False

    def sort_menu(self):
        """Create sort menu"""

        self.sortButton = QToolButton()
        self.sortButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/sort.svg'))
        self.sortButton.setPopupMode(QToolButton.InstantPopup)
        self.sortButton.setMenu(self.parent.sortMenu)
        self.hlayout.addWidget(self.sortButton)

    def group_menu(self):
        """Create group menu"""

        self.groupButton = QToolButton()
        self.groupButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/group.svg'))
        self.groupButton.setPopupMode(QToolButton.InstantPopup)
        self.groupButton.setMenu(self.parent.groupMenu)
        self.hlayout.addWidget(self.groupButton)

    def more_menu(self):
        """Create more menu"""

        self.otherActionsButton = QToolButton()
        self.otherActionsButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/more2.svg'))
        self.otherActionsButton.setStyleSheet('border: none;')
        self.otherActionsButton.setPopupMode(QToolButton.InstantPopup)
        self.otherActionsMenu = QMenu()
        self.otherActionsButton.setMenu(self.otherActionsMenu)
        self.removeAct = QAction('Remove selected', shortcut='Delete')
        self.removeAct.triggered.connect(self.remove_data)
        self.createGroupAct = QAction("Create groups")
        self.createGroupAct.triggered.connect(self.save_group)
        self.otherActionsMenu.addMenu(self.parent.showGroupMenu)
        self.otherActionsMenu.addMenu(self.parent.addGroupDataMenu)
        self.otherActionsMenu.addAction(self.removeAct)
        self.otherActionsMenu.addAction(self.createGroupAct)
        self.hlayout.addWidget(self.otherActionsButton)
        self.layout.addLayout(self.hlayout)
        self.hlayout2 = QHBoxLayout()

    def check_menu(self):
        """Create menu to check or uncheck all/none/selected items"""

        self.selectButton = QToolButton()
        self.selectButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/checkbox.svg'))
        self.selectButton.setStyleSheet('border: none;')
        self.selectButton.setPopupMode(QToolButton.InstantPopup)
        self.selectMenu = QMenu()
        self.selectButton.setMenu(self.selectMenu)
        self.selectAllAct = QAction('All')
        self.selectAllAct.triggered.connect(self.check_all)
        self.unselectAllAct = QAction('None')
        self.unselectAllAct.triggered.connect(self.uncheck_all)
        self.unselectSelectedAct = QAction('Uncheck selected')
        self.unselectSelectedAct.triggered.connect(self.uncheck_selected)
        self.selectSelectedAct = QAction('Check selected')
        self.selectSelectedAct.triggered.connect(self.check_selected)
        self.selectMenu.addAction(self.selectAllAct)
        self.selectMenu.addAction(self.unselectAllAct)
        self.selectMenu.addAction(self.unselectSelectedAct)
        self.selectMenu.addAction(self.selectSelectedAct)
        self.hlayout.addWidget(self.selectButton)

    def remove_data(self):
        """Remove selected item(s) from QListWidget"""

        selected_items = self.q_list.selectedItems()
        for item in selected_items:
            item = item.text()
            if self.parent.grouped:
                for label in self.parent.grouped_labels:
                    if item in label:
                        self.parent.grouped_labels.remove(label)
                        try:
                            del self.parent.nwb_path_list[item]
                        except KeyError:
                            continue
                        list_item_to_remove = self.q_list.findItems(item, Qt.MatchExactly)
                        try:
                            for item_to_remove in list_item_to_remove:
                                self.q_list.takeItem(self.q_list.row(item_to_remove))
                        except IndexError:
                            pass
            if self.parent.sorted:
                for label in self.parent.sorted_labels:
                    if item in label:
                        self.parent.sorted_labels.remove(label)
                        try:
                            del self.parent.nwb_path_list[item]
                        except KeyError:
                            continue
                        list_item_to_remove = self.q_list.findItems(item, Qt.MatchExactly)
                        try:
                            for item_to_remove in list_item_to_remove:
                                self.q_list.takeItem(self.q_list.row(item_to_remove))
                        except IndexError:
                            pass
            for label in self.parent.labels:
                if item in label:
                    self.parent.labels.remove(label)
                    try:
                        del self.parent.nwb_path_list[item]
                    except KeyError:
                        continue
                    list_item_to_remove = self.q_list.findItems(item, Qt.MatchExactly)
                    try:
                        for item_to_remove in list_item_to_remove:
                            self.q_list.takeItem(self.q_list.row(item_to_remove))
                    except IndexError:
                        pass
        if not self.parent.labels:
            self.parent.groupMenu.setEnabled(False)
            self.parent.sortMenu.setEnabled(False)
        self.parent.load_group_from_config()

    def uncheck_all(self):
        """Uncheck all items"""

        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def uncheck_selected(self):
        """Uncheck selected item(s)"""

        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def check_all(self):
        """Check all items"""

        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)

    def check_selected(self):
        """Check selected item(s)"""

        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)

    def on_change(self):
        """Handle change in selection"""

        self.items = [item.text() for item in self.q_list.selectedItems()]

    def get_items(self):
        """
        Returns list of items
        Returns:
            list of items

        """

        return [item for item in self.items]

    def get_data_to_analyse(self):
        """Get data to analyse"""

        checked_items = []
        for index in range(self.q_list.count()):
            if self.q_list.item(index).checkState() == 2:
                checked_items.append(self.q_list.item(index).text())
        return [data for key, data in self.parent.data_dict.items() if key in checked_items]

    def send_data_to_analysis_tree(self):
        """Send data to the analysis tree function"""
        # we erase the widgets in the parameters section
        # self.arguments_section_widget.tabula_rasa()
        data_to_analyse = self.get_data_to_analyse()
        # TODO: deal with the fact the data might not be in nwb format
        if data_to_analyse:
            self.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")


    def populate(self, labels, method='clear'):
        """
        Populate the QListWidget with sessions labels

        Args:
            labels (list): Sessions identifiers
            method (str): In case we don't want to clear the QListWidget

        """
        if method == 'clear':
            self.q_list.clear()
        if method == 'add':
            for label in labels:
                if label not in self.parent.labels:
                    self.parent.labels.append(label)
            self.parent.load_group_from_config()
        items = []
        if self.q_list.count() != 0:
            for file in labels:
                for index in range(self.q_list.count()):
                    items.append(self.q_list.item(index).text())
                if file not in items:
                    item = QListWidgetItem()
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setText(str(file))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                    self.q_list.addItem(item)
        else:
            for file in labels:
                item = QListWidgetItem()
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setText(str(file))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                self.q_list.addItem(item)

    def form_group(self, labels, param=["-"]):
        """
        Form group of items and display their group name

        Args:
            labels (list): Session identifiers
            param (str): Parameter used to create the groups

        """

        self.q_list.clear()
        while len(param) < len(labels):
            param.append("-")
        for group in labels:
            item = QListWidgetItem()  # delimiter
            if param[0] is None:
                param[0] = "None"
            item.setText('--------------------------' + str(param.pop(0)) + '---------------------------')
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)  # item should not be selectable
            self.q_list.addItem(item)
            for file in group:
                item = QListWidgetItem()
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setText(str(file))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                self.q_list.addItem(item)

    def update_text_filter(self, param_group=''):
        """
        Update the QLabel to display the sort/group state

        Args:
            param_group: Parameter used to form group

        """
        if self.parent.grouped:
            self.textLabel.setText(f'Grouped by : {param_group}')
        elif self.parent.sorted:
            param_list = ', '.join(self.parent.param_list)
            self.textLabel.setText(f'Sorted by : {param_list}')
        else:
            self.textLabel.setText('')

    def save_group(self):
        """Save sessions in a group"""

        self.nameBox = QDialog(self)
        self.nameBoxLayout = QVBoxLayout(self.nameBox)
        self.nameBox.setWindowTitle("Save your group as")
        self.save_name = QLineEdit(self.nameBox)
        self.save_name.setText("Group_" + str(datetime.date.today()))
        self.saveButton = QPushButton('Save as')
        self.nameBoxLayout.addWidget(self.save_name)
        self.nameBoxLayout.addWidget(self.saveButton)
        self.nameBox.show()
        self.saveButton.clicked.connect(self.save_group_names)
        self.saveButton.clicked.connect(self.nameBox.close)

    def save_group_names(self):
        """Save group in a YAML with a certain name"""

        group_yaml_file = "cicada/config/group.yaml"
        name = self.save_name.text()
        group_to_save = []
        checked_items = []
        for index in range(self.q_list.count()):
            if self.q_list.item(index).checkState() == 2:
                checked_items.append(self.q_list.item(index).text())
        for item in checked_items:
            for path in self.parent.nwb_path_list.values():
                if path.endswith(item + ".nwb"):
                    group_to_save.append(path)
        if self.parent.all_groups:
            self.parent.all_groups.update({name: group_to_save})
        else:
            self.parent.all_groups = {name: group_to_save}
        with open(group_yaml_file, 'w') as stream:
            yaml.dump(self.parent.all_groups, stream, default_flow_style=False)
        self.parent.load_group_from_config()

