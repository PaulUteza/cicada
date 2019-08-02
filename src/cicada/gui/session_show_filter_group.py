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
        return [item for item in self.items]

    def get_data_to_analyse(self):
        return [data for key, data in self.parent.data_dict.items() if key in self.items]

    def send_data_to_analysis_tree(self):
        data_to_analyse = self.get_data_to_analyse()
        # TODO: deal with the fact the data might not be in nwb format
        self.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def populate(self, labels):
        self.q_list.clear()
        self.q_list.insertItems(0, labels)

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



if __name__ == "__main__":

    app = QApplication(sys.argv)
    cicada = CicadaMainWindow()
    cicada.show()
    sys.exit(app.exec_())
