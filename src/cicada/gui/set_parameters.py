
from qtpy.QtCore import QDateTime, Qt, QTimer
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QMainWindow, QMessageBox, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)


import random

import datetime

# input_test contains different types of parameters, just to check if it works
class InputParam:

    def __init__(self):

        self.input_test = [{'name': 'age', 'type': int, 'range': [0, 100], 'doc': 'the age of the subject', 'default': 0},
                           {'name': 'description', 'type': str, 'doc': 'a description of the subject', 'default': None},
                           {'name': 'brothers and sisters', 'type': int, 'range': [0, 5], 'doc': 'size of mouse brotherhood', 'default': None},
                           {'name': 'sex', 'type': str, 'choices': ['M', 'F'], 'multiple_choices': False, 'doc': 'the sex of the subject', 'default': None},
                           {'name': 'analyses to do', 'type': str, 'choices': ['rasterplot', 'fluorescence', 'eye_tracking', 'bonus'], 'multiple_choices': True, 'doc': 'a unique identifier for the subject', 'default': None},
                           {'name': 'weight', 'type': float, 'doc': 'the weight of the subject', 'default': None},
                           {'name': 'date_of_birth', 'type': datetime, 'default': None,
                            'doc': 'datetime of date of birth. May be supplied instead of age.'},
                           {'name': 'is_alive', 'type': bool, 'doc': 'if the subject is alive', 'default': None},
                           {'name': 'is_grey', 'type': bool, 'doc': 'if the subject is grey', 'default': None},
                           {'name': 'nwb_already_exist', 'type': bool, 'doc': 'if a nwb file already exists', 'default': None}]


# Not really usefull here, just for test
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


# Here is the interesting part !
class ParamSection(QWidget):

    def __init__(self, parent=None):
        super(ParamSection, self).__init__(parent)

        # Got input paramers
        input_example = InputParam()
        test_param = input_example.input_test

        # To add widgets vertically
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Parameters :"))


        # =================== Output ================
        # A dictionnary which contains all values of parameters from the GUI !
        self.output = {}
        # ===========================================

        # The goal here is to determine the best type of widget to add corresponding to each parameter.
        # Then it add the good widget with parameter options
        for param in test_param:

            # Function to find the best type of widget
            widget_type = self.get_widget_type(param)

            # Widget construction
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
            elif widget_type == "CheckBox":
                widget_to_add = self.create_checkbox(param)
            else:
                widget_to_add = self.create_textedit(param)

            # Add widget and label (description)
            if param['type'] != bool:
                self.layout.addWidget(QLabel(param['name']))
            self.layout.addWidget(widget_to_add)

        # Button to continue / cancel, not ready for the moment
        self.button1 = QPushButton("大丈夫")
        self.button2 = QPushButton(" キャンセル ")

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        self.button1.clicked.connect(self.load_parameters)
        self.button2.clicked.connect(QApplication.instance().quit)

    # This function is needed to connect each widget to the corresponding parameter.
    # It just change the parameter value to the one given in the GUI
    def change_param(self, name, bidule):
        self.output[name] = bidule
        print(self.output[name])

    # Function to find the best type of widget
    # All could be done with only LineEdit widget but this is not beautiful and not convenient ...
    def get_widget_type(self, param):

        param_keys = param.keys()

        if 'type' not in param_keys:
            raise KeyError("'type' not defined for this parameter !")

        param_type = param["type"]

        if param_type == str:
            if "choices" in param_keys and "multiple_choices" in param_keys:
                if param["multiple_choices"] == True:
                    # You can select multiple options
                    return "GroupBox"
                else:
                    # You can select only one option
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
        elif param_type == bool:
            return 'CheckBox'
        else:
            return "LineEdit"


    # One function for each type of widget to create ! (with parameter options)
    # It also connects the created widget to the output parameter
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

        self.output.update({param['name']: param['default']})
        spinBox.valueChanged.connect(lambda value: self.change_param(param['name'], value))

        return(spinBox)

    def create_lineedit(self, param):
        group = QWidget()

        default = ""
        if "default" in param.keys():
            if param["default"] != None:
                default = str(param["default"])

        widget = QLineEdit(default)
        hbox = QHBoxLayout()
        hbox.addWidget(widget)
        hbox.addWidget(QLabel("(" + str(param['type']).split("'")[1] + ")"))
        hbox.addStretch(1)
        group.setLayout(hbox)

        self.output.update({param['name']: param['default']})
        widget.textChanged.connect(lambda value: self.change_param(param['name'], value))

        return group

    def create_combobox(self, param):
        combobox = QComboBox()
        for choice in param["choices"]:
            combobox.addItem(str(choice))

        self.output.update({param['name']: param['default']})
        combobox.currentTextChanged.connect(lambda value: self.change_param(param['name'], value))

        return combobox

    def create_groupbox(self, param):

        # TODO : get data from groupbox !

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

        widget = QLineEdit("datetime.datetime(YYYY, MM, DD)")

        self.output.update({param['name']: param['default']})
        widget.textChanged.connect(lambda value: self.change_param(param['name'], value))

        return widget

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

        self.output.update({param['name']: param['default']})
        valueSpinBox.valueChanged.connect(lambda value: self.change_param(param['name'], value))

        return sliderGroup

    def create_checkbox(self, param):

        widget = QCheckBox("&" + param["name"])

        self.output.update({param['name']: param['default']})
        widget.stateChanged.connect(lambda value: self.change_param(param['name'], value))

        return widget

    # Will be used at the end to start the analysis, but not done yet !
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
