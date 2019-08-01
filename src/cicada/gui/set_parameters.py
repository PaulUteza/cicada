
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                            QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox, QVBoxLayout, QWidget)

import datetime


# input_test contains different types of parameters, just to check if it works
class InputParam:

    def __init__(self):

        self.input_test = [{'name': 'age', 'type': int, 'range': [0, 100], 'doc': 'the age of the subject',
                            'default': 0},
                           {'name': 'description', 'type': str, 'doc': 'a description of the subject',
                            'default': None},
                           {'name': 'brothers and sisters', 'type': int, 'range': [0, 5],
                            'doc': 'size of mouse brotherhood', 'default': None},
                           {'name': 'sex', 'type': str, 'choices': ['M', 'F'], 'multiple_choices': False,
                            'doc': 'the sex of the subject', 'default': None},
                           {'name': 'weight', 'type': float, 'doc': 'the weight of the subject', 'default': None},
                           {'name': 'date_of_birth', 'type': datetime, 'default': None,
                            'doc': 'datetime of date of birth. May be supplied instead of age.'},
                           {'name': 'is_alive', 'type': bool, 'doc': 'if the subject is alive', 'default': None},
                           {'name': 'is_grey', 'type': bool, 'doc': 'if the subject is grey', 'default': None},
                           {'name': 'nwb_already_exist', 'type': bool, 'doc': 'if a nwb file already exists',
                            'default': None}]


# Mother Class
class WidgetForParam:

    param_already_got = []

    def __init__(self):
        self.all_params = InputParam().input_test
        self.param_inputs = []
        self.param_output = {'name': '', 'type': None, 'value': None}

        self.keys_to_check = ['name', 'type', 'default']
        self.conditions = []

        self.param = None
        self.widget = None
        self.widget_group = None
        self.default = None

        # Example :
        # self.conditions = [lambda param : param['type'] == int,
        #                    lambda param : param['max'] - param['min'] <= 20]

    def set_param(self, param):
        self.param = param
        if 'name' in param.keys() and 'type' in param.keys():
            self.param_output['name'] = self.param['name']
            self.param_output['type'] = str(self.param['type']).split("'")[1]

    def check_param(self, param, assert_error=False):
        for key in self.keys_to_check:
            if key not in param.keys():
                if assert_error:
                    raise KeyError(f"key not found : {key} !")
                return False
        return True

    def check_conditions(self, param):
        for cond in self.conditions:
            if not cond(param):
                return False
        return True

    def get_param_input(self):
        for param in self.all_params:
            if self.check_param(param) and param not in WidgetForParam.param_already_got:
                if self.check_conditions(param):
                    self.param_inputs.append(param)
                    WidgetForParam.param_already_got.append(param)
        return self.param_inputs

    def change_param(self, value):
        self.param_output['value'] = value
        print(self.param_output)

    def create_widget(self):
        pass

    def connect_widget(self):
        pass

    def add_widget_to_layout(self, layout):
        if self.param['type'] != bool:
            layout.addWidget(QLabel(self.param['name'] + " :"))
        if self.widget_group:
            layout.addWidget(self.widget_group)
        else:
            layout.addWidget(self.widget)


class ParamSpinBox(WidgetForParam):

    def __init__(self):
        super().__init__()
        self.keys_to_check.extend(['range'])
        self.conditions.extend([lambda param_x: param_x['type'] == int,
                                lambda param_x: param_x["range"][1] - param_x["range"][0] > 20])

    def create_widget(self):
        self.check_param(self.param, assert_error=True)

        self.default = self.param['range'][0]
        if not self.param['default']:
            self.default = self.param['default']

        self.widget = QSpinBox()
        self.widget.setValue(self.default)
        self.widget.setRange(self.param['range'][0], self.param['range'][1])

    def connect_widget(self):
        self.widget.valueChanged.connect(lambda value: self.change_param(value))


class ParamLineEdit(WidgetForParam):
    def __init__(self):
        super().__init__()

    def create_widget(self):
        self.check_param(self.param, assert_error=True)

        self.default = ""
        if self.param['default']:
            self.default = str(self.param["default"])

        self.widget_group = QWidget()

        self.widget = QLineEdit(self.default)
        h_box = QHBoxLayout()
        h_box.addWidget(self.widget)
        h_box.addWidget(QLabel("(" + str(self.param['type']).split("'")[1] + ")"))
        h_box.addStretch(1)
        self.widget_group.setLayout(h_box)

    def connect_widget(self):
        self.widget.textChanged.connect(lambda value: self.change_param(value))


class ParamComboBox(WidgetForParam):

    def __init__(self):
        super().__init__()

        self.keys_to_check.extend(['choices'])
        self.conditions.extend([lambda param_x: param_x['type'] == str])

    def create_widget(self):
        self.check_param(self.param, assert_error=True)
        self.widget = QComboBox()
        for choice in self.param["choices"]:
            self.widget.addItem(str(choice))

    def connect_widget(self):
        self.widget.currentTextChanged.connect(lambda value: self.change_param(value))


class ParamDateTime(WidgetForParam):

    def __init__(self):
        super().__init__()

        self.conditions.extend([lambda param_x: param_x['type'] == datetime])

    def create_widget(self):
        self.check_param(self.param, assert_error=True)
        self.widget = QLineEdit("datetime.datetime(YYYY, MM, DD)")

    def connect_widget(self):
        self.widget.textChanged.connect(lambda value: self.change_param(value))


class ParamSlider(WidgetForParam):

    def __init__(self):
        super().__init__()

        self.keys_to_check.extend(['range'])
        self.conditions.extend([lambda param_x: param_x['type'] == int,
                                lambda param_x: param_x["range"][1] - param_x["range"][0] <= 20])

    def create_widget(self):
        self.check_param(self.param, assert_error=True)

        self.default = self.param['range'][0]
        if self.param['default']:
            self.default = self.param['default']
        self.widget_group = QWidget()
        slider = QSlider(Qt.Horizontal)

        slider.setValue(self.default)
        slider.setRange(self.param['range'][0], self.param['range'][1])

        self.widget = QSpinBox()
        self.widget.setValue(self.default)
        self.widget.setRange(self.param['range'][0], self.param['range'][1])

        self.widget.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(self.widget.setValue)

        h_box = QHBoxLayout()
        h_box.addWidget(slider)
        h_box.addWidget(self.widget)
        h_box.addStretch(1)
        self.widget_group.setLayout(h_box)

    def connect_widget(self):
        self.widget.valueChanged.connect(lambda value: self.change_param(value))


class ParamCheckBox(WidgetForParam):

    def __init__(self):
        super().__init__()

        self.conditions.extend([lambda param_x: param_x['type'] == bool])

    def create_widget(self):
        self.check_param(self.param, assert_error=True)
        self.widget = QCheckBox("&" + self.param["name"])

    def connect_widget(self):
        self.widget.stateChanged.connect(lambda value: self.change_param(value))


# Not really useful here, just for test
class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.param_section = ParamSection()

        self.setWindowTitle("蝉 : パラメータ")
        # QMainWindow.setWindowState(self, Qt.WindowMaximized)
        self.resize(300, 500)
        self.setup_menus()

        self.setCentralWidget(self.param_section)

    def setup_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        exit_action = file_menu.addAction("E&xit")

        exit_action.triggered.connect(QApplication.instance().quit)


# Here is the interesting part !
class ParamSection(QWidget):

    def __init__(self, parent=None):
        super(ParamSection, self).__init__(parent)

        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.resize(300, 500)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.layout.addWidget(QLabel("Parameters :"))

        # Be careful of the order of classes : put more selective classes at first !
        all_widgets_type = [ParamSpinBox(), ParamComboBox(), ParamCheckBox(), ParamSlider(),
                            ParamDateTime(), ParamLineEdit()]
        param_input_by_type = [WidgetType.get_param_input() for WidgetType in all_widgets_type]

        all_widgets = []

        for idx_widget_type, widget_type in enumerate(param_input_by_type):
            for param in widget_type:
                widget = all_widgets_type[idx_widget_type]
                widget.set_param(param)
                widget.create_widget()
                widget.connect_widget()
                widget.add_widget_to_layout(self.layout)
                all_widgets.append(widget)

        # Button to continue / cancel, not ready for the moment
        self.button1 = QPushButton("大丈夫")
        self.button2 = QPushButton(" キャンセル ")

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addStretch(1)
        self.setLayout(self.main_layout)

        self.button1.clicked.connect(self.load_parameters)
        self.button2.clicked.connect(QApplication.instance().quit)

    # Will be used at the end to start the analysis, but not done yet !
    def load_parameters(self):
        QMessageBox.warning(self, "蝉 : パラメータ",
                            "蝉は一般的に茶色で、\n"
                            "体の長さは5〜9センチです。\n"
                            "非常に緑の植物に定住すること\n"
                            "を好む緑のセミもあります。",
                            QMessageBox.Cancel)
        QApplication.instance().quit()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    set_param = MainWindow()
    set_param.show()
    sys.exit(app.exec_())
