
from qtpy.QtCore import QDateTime, Qt, QTimer
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QMainWindow, QMessageBox, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)


import random

import datetime

class InputParam:

    def __init__(self):

        self.input_test = [{'name': 'age', 'type': int, 'range': [0, 100], 'doc': 'the age of the subject', 'default': 0},
                           {'name': 'description', 'type': str, 'doc': 'a description of the subject', 'default': None},
                           {'name': 'brothers and sisters', 'type': int, 'range': [0, 5], 'doc': 'size of mouse brotherhood', 'default': None},
                           {'name': 'sex', 'type': str, 'choices': ['M', 'F'], 'multiple_choices': False, 'doc': 'the sex of the subject', 'default': None},
                           {'name': 'analyses to do', 'type': str, 'choices': ['rasterplot', 'fluorescence', 'eye_tracking', 'bonus'], 'multiple_choices': True, 'doc': 'a unique identifier for the subject', 'default': None},
                           {'name': 'weight', 'type': float, 'doc': 'the weight of the subject', 'default': None},
                           {'name': 'date_of_birth', 'type': datetime, 'default': None,
                            'doc': 'datetime of date of birth. May be supplied instead of age.'}]


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.param_section = ParamSection()

        self.setWindowTitle("蝉 : パラメータ")
        #QMainWindow.setWindowState(self, Qt.WindowMaximized)
        self.resize(300, 400)
        self.setupMenus()

        self.setCentralWidget(self.param_section)

    def setupMenus(self):
        fileMenu = self.menuBar().addMenu("&File")

        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")

        exitAction = fileMenu.addAction("E&xit")
        exitAction.setShortcut("Ctrl+Q")

        exitAction.triggered.connect(QApplication.instance().quit)

class ParamSection(QWidget):

    def __init__(self, parent=None):
        super(ParamSection, self).__init__(parent)

        tesuto = InputParam()
        test_param = tesuto.input_test

        self.layout = QVBoxLayout()

        for param in test_param:

            widget_type = self.get_widget_type(param)

            if widget_type == "SpinBox":
                widget_to_add = self.create_spinbox(param)
            elif widget_type == "LineEdit":
                widget_to_add = self.create_lineedit(param)
            elif widget_type == "ComboBox":
                widget_to_add = self.create_combobox(param)
            elif widget_type == "GroupBox":
                widget_to_add = self.create_groupbox(param)
            elif widget_type == "RadioButton":
                widget_to_add = self.create_radiobutton(param)
            elif widget_type == "DateTimeEdit":
                widget_to_add = self.create_datetimeedit(param)
            elif widget_type == "Slider":
                widget_to_add = self.create_slider(param)
            else:
                widget_to_add = self.create_textedit(param)

            self.layout.addWidget(QLabel(param['name']))
            self.layout.addWidget(widget_to_add)

        self.button1 = QPushButton("大丈夫")
        self.button2 = QPushButton(" キャンセル ")

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        self.button1.clicked.connect(self.load_parameters)
        self.button2.clicked.connect(QApplication.instance().quit)


    def get_widget_type(self, param):

        param_keys = param.keys()

        if 'type' not in param_keys:
            raise KeyError("'type' not defined for this parameter !")

        param_type = param["type"]

        if param_type == str:
            if "choices" in param_keys and "multiple_choices" in param_keys:
                if param["multiple_choices"] == True:
                    return "GroupBox"
                else:
                    return "ComboBox"
            else:
                return "LineEdit"

        elif param_type == int:
            if "range" in param_keys:
                if param["range"][1] - param["range"][0] <= 20:
                    # Work well with integer when there is not to much value choices
                    return "Slider"
                else:
                    return "SpinBox"
            else:
                return "LineEdit"

        elif param_type == float:
            return "LineEdit"
        elif param_type == datetime:
            return "DateTimeEdit"
        else:
            return "LineEdit"


    def create_spinbox(self, param):
        min = param["range"][0]
        max = param["range"][1]
        default = round((max-min)/2)
        if "default" in param.keys():
            if param["default"] != None:
                default = int(param["default"])
        spinBox = QSpinBox()
        spinBox.setValue(default)
        spinBox.setRange(min, max)

        return(spinBox)

    def create_lineedit(self, param):
        default = ""
        if "default" in param.keys():
            if param["default"] != None:
                default = str(param["default"])
        return QLineEdit(default)

    def create_combobox(self, param):
        combobox = QComboBox()
        for choice in param["choices"]:
            combobox.addItem(str(choice))
        return combobox

    def create_groupbox(self, param):
        groupBox = QGroupBox()
        groupBox.setFlat(True)
        vbox = QVBoxLayout()
        for choice in param["choices"]:
            checkBox = QCheckBox("&" + str(choice))
            vbox.addWidget(checkBox)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def create_datetimeedit(self, param):
        return QLineEdit("datetime.datetime(YYYY, MM, DD)")


    def create_slider(self, param):
        min = param["range"][0]
        max = param["range"][1]

        default = round((max - min) / 2)
        if "default" in param.keys():
            if param["default"] != None:
                default = int(param["default"])

        sliderGroup = QWidget()

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setRange(min, max)
        slider.setValue(default)

        valueSpinBox = QSpinBox()
        valueSpinBox.setValue(default)
        valueSpinBox.setRange(min, max)

        valueSpinBox.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(valueSpinBox.setValue)

        hbox = QHBoxLayout()
        hbox.addWidget(slider)
        hbox.addWidget(valueSpinBox)
        hbox.addStretch(1)
        sliderGroup.setLayout(hbox)

        return sliderGroup

    def load_parameters(self):
        ret = QMessageBox.warning(self, "蝉 : パラメータ",
                                  "蝉は一般的に茶色で、\n"
                                  "体の長さは5〜9センチです。\n"
                                  "非常に緑の植物に定住すること\n"
                                  "を好む緑のセミもあります。",
                                  QMessageBox.Cancel)
        QApplication.instance().quit


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    set_param = MainWindow()
    set_param.show()
    sys.exit(app.exec_())
