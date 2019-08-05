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
from random import randint


# TODO : Quand des éléments à sort ont des None, les griser

class SessionsListWidget(QListWidget):

    def __init__(self, session_widget):
        QListWidget.__init__(self)
        self.special_background_on = False
        self.session_widget = session_widget

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


class SessionsWidget(QWidget):

    def __init__(self, parent=None):
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
        self.q_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.toAnalysisButton = QPushButton()
        self.toAnalysisButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/cicada_arrow.svg'))
        self.toAnalysisButton.setStyleSheet('border: none; background-color: none;')
        self.toAnalysisButton.clicked.connect(self.send_data_to_analysis_tree)
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
        self.hlayout2.addWidget(self.toAnalysisButton)
        self.setLayout(self.hlayout2)
        self.analysis_tree = None

    def sort_menu(self):
        self.sortButton = QToolButton()
        self.sortButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/sort.svg'))
        self.sortButton.setPopupMode(QToolButton.InstantPopup)
        self.sortButton.setMenu(self.parent.sortMenu)
        self.hlayout.addWidget(self.sortButton)

    def group_menu(self):
        self.groupButton = QToolButton()
        self.groupButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/group.svg'))
        self.groupButton.setPopupMode(QToolButton.InstantPopup)
        self.groupButton.setMenu(self.parent.groupMenu)
        self.hlayout.addWidget(self.groupButton)

    def more_menu(self):
        self.otherActionsButton = QToolButton()
        self.otherActionsButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/more2.svg'))
        self.otherActionsButton.setStyleSheet('QToolButton::menu-indicator { width: 0px; height: 0px;};')
        self.otherActionsButton.setStyleSheet('border: none;')
        self.otherActionsButton.setPopupMode(QToolButton.InstantPopup)
        self.otherActionsMenu = QMenu()
        self.otherActionsButton.setMenu(self.otherActionsMenu)
        self.removeAct = QAction('Remove selected')
        self.removeAct.triggered.connect(self.remove_data)
        self.createGroupAct = QAction("Create groups")
        self.createGroupAct.triggered.connect(self.save_group)
        self.otherActionsMenu.addAction(self.removeAct)
        self.otherActionsMenu.addAction(self.createGroupAct)
        self.hlayout.addWidget(self.otherActionsButton)
        self.layout.addLayout(self.hlayout)
        self.hlayout2 = QHBoxLayout()

    def check_menu(self):

        self.selectButton = QToolButton()
        self.selectButton.setIcon(QtGui.QIcon('cicada/gui/icons/svg/checkbox.svg'))
        self.selectButton.setStyleSheet('border: none;')
        self.selectButton.setPopupMode(QToolButton.InstantPopup)
        self.selectMenu = QMenu()
        self.selectButton.setMenu(self.selectMenu)
        self.selectAllAct = QAction('All')
        self.selectAllAct.triggered.connect(self.select_all)
        self.unselectAllAct = QAction('None')
        self.unselectAllAct.triggered.connect(self.unselect_all)
        self.unselectSelectedAct = QAction('Uncheck selected')
        self.unselectSelectedAct.triggered.connect(self.unselect_selected)
        self.selectSelectedAct = QAction('Check selected')
        self.selectSelectedAct.triggered.connect(self.select_selected)
        self.selectMenu.addAction(self.selectAllAct)
        self.selectMenu.addAction(self.unselectAllAct)
        self.selectMenu.addAction(self.unselectSelectedAct)
        self.selectMenu.addAction(self.selectSelectedAct)
        self.hlayout.addWidget(self.selectButton)

    def remove_data(self):
        selected_items = self.q_list.selectedItems()
        for item in selected_items:
            item = item.text()
            for file in self.parent.nwb_path_list:
                print(file)
                if item in file:
                    self.parent.nwb_path_list.remove(file)
            if self.parent.grouped:
                for label in self.parent.grouped_labels:
                    if item in label:
                        self.parent.grouped_labels.remove(label)
            if self.parent.sorted:
                for label in self.parent.sorted_labels:
                    if item in label:
                        self.parent.sorted_labels.remove(label)
            for label in self.parent.labels:
                if item in label:
                    self.parent.labels.remove(label)
        self.populate(self.parent.labels)
        if not self.parent.labels:
            self.parent.groupMenu.setEnabled(False)
            self.parent.sortMenu.setEnabled(False)

    def unselect_all(self):
        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def unselect_selected(self):
        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def select_all(self):
        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)

    def select_selected(self):
        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)



    def on_change(self):
        self.items = [item.text() for item in self.q_list.selectedItems()]

    def get_items(self):
        return [item for item in self.items]

    def get_data_to_analyse(self):
        checked_items = []
        for index in range(self.q_list.count()):
            if self.q_list.item(index).checkState() == 2:
                checked_items.append(self.q_list.item(index).text())
        return [data for key, data in self.parent.data_dict.items() if key in checked_items]

    def send_data_to_analysis_tree(self):
        data_to_analyse = self.get_data_to_analyse()
        # TODO: deal with the fact the data might not be in nwb format
        if data_to_analyse:
            self.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def populate(self, labels):
        self.q_list.clear()
        for file in labels:
            item = QListWidgetItem()
            item.setCheckState(QtCore.Qt.Checked)
            item.setText(str(file))
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            self.q_list.addItem(item)
        # self.q_list.insertItems(0, labels)

    def form_group(self, labels, param=["-"]):
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
                item.setCheckState(QtCore.Qt.Checked)
                item.setText(str(file))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                self.q_list.addItem(item)

    def update_text_filter(self, param_group=''):
        if self.parent.grouped:
            self.textLabel.setText(f'Grouped by : {param_group}')
        elif self.parent.sorted:
            param_list = ', '.join(self.parent.param_list)
            self.textLabel.setText(f'Sorted by : {param_list}')

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
        group_yaml_file = "cicada/config/group.yaml"
        name = self.save_name.text()
        group_to_save = []
        if self.q_list.selectedItems():
            for item in self.get_items():
                for path in self.parent.nwb_path_list:
                    if path.endswith(item + ".nwb"):
                        group_to_save.append(path)
            if self.parent.group_data:
                self.parent.group_data.update({name: group_to_save})
            else:
                self.parent.group_data = {name: group_to_save}
        elif self.parent.grouped:
            counter = 0
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
                    id_group = str(counter)
                print(name,id_group)
                if self.parent.group_data:
                    self.parent.group_data.update({str(name + '_' + id_group): group_to_save})
                else:
                    self.parent.group_data = {str(name + '_' + id_group): group_to_save}
        else:
            for item in self.parent.labels:
                for path in self.parent.nwb_path_list:
                    if path.endswith(item + ".nwb"):
                        group_to_save.append(path)
            if self.parent.group_data:
                self.parent.group_data.update({name: group_to_save})
            else:
                self.parent.group_data = {name: group_to_save}
        with open(group_yaml_file, 'w') as stream:
            yaml.dump(self.parent.group_data, stream, default_flow_style=False)
        self.parent.load_group_from_config()



