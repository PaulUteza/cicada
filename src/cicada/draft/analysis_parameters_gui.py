
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                            QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox, QVBoxLayout, QWidget)
from qtpy import QtCore

import datetime
from abc import ABC, abstractmethod
from random import randint


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
class WidgetForParam(ABC):

    # It is used to be sure that a parameter won't be loaded by two different widgets
    param_already_got = []
    # ALL_PARAMS = InputParam().input_test  # list of all params

    def __init__(self):
        self.param_inputs = []
        self.param_output = {'name': '', 'type': None, 'value': None}

        self.keys_to_check = ['name', 'type', 'default']  # mandatory fields !
        self.conditions = []  # all conditions required by the widget to get a parameter
        # Example :
        # self.conditions = [lambda param : param['type'] == int,
        #                    lambda param : param['max'] - param['min'] <= 20]

        self.param = None
        self.widget = None
        self.widget_group = None
        self.default = None

    # To set the parameter associated to the widget, and build the corresponding param_output
    def set_param(self, param):
        self.param = param
        if 'name' in param.keys() and 'type' in param.keys():
            self.param_output['name'] = self.param['name']
            self.param_output['type'] = str(self.param['type']).split("'")[1]

    # Check if a parameter has all the required fields (keys), can assert an error or not
    def check_param(self, param, assert_error=False):
        for key in self.keys_to_check:
            if key not in param.keys():
                if assert_error:
                    raise KeyError(f"key not found : {key} !")
                return False
        return True

    # Check if a parameter is corresponding to the widget
    def check_conditions(self, param):
        for cond in self.conditions:
            if not cond(param):
                return False
        return True

    # Get all parameters which corresponds to the widget. Don't get them already got by other widgets
    def get_param_input(self, all_params):
        """

        :param all_params: list of dict
        :return:
        """

        for param in all_params:
            if self.check_param(param) and param not in WidgetForParam.param_already_got:
                if self.check_conditions(param):
                    self.param_inputs.append(param)
                    WidgetForParam.param_already_got.append(param)
        return self.param_inputs

    # Make output value corresponding to what the user have done in the GUI
    def change_param(self, value):
        self.param_output['value'] = value
        print(self.param_output)

    #  Add widget to the GUI
    def add_widget_to_layout(self, layout):
        if self.param['type'] != bool:
            q_label = QLabel(self.param['name'] + " :")
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            layout.addWidget(q_label)
        if self.widget_group:
            layout.addWidget(self.widget_group)
        else:
            layout.addWidget(self.widget)

    @abstractmethod
    def create_widget(self):
        pass

    @abstractmethod
    def connect_widget(self):
        pass


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

        self.setWindowTitle("CICADA Parameters")
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

        self.special_background_on = False
        self.cicada_analysis = None

        # Add the scroll bar
        # ==============================
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scrollAreaWidgetContents = QWidget()
        # self.scrollAreaWidgetContents.resize(300, 500)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        # ==============================

        # self.layout.addWidget(QLabel("Parameters :"))
        #
        # # Be careful of the order of classes : put more selective classes at first !
        # all_widgets_type = [ParamSpinBox(), ParamComboBox(), ParamCheckBox(), ParamSlider(),
        #                     ParamDateTime(), ParamLineEdit()]
        # param_input_by_type = [WidgetType.get_param_input() for WidgetType in all_widgets_type]
        #
        # all_widgets = []
        #
        # for idx_widget_type, widget_type in enumerate(param_input_by_type):
        #     for param in widget_type:
        #         widget = all_widgets_type[idx_widget_type]
        #         widget.set_param(param)
        #         widget.create_widget()
        #         widget.connect_widget()
        #         widget.add_widget_to_layout(self.layout)
        #         all_widgets.append(widget)
        #
        # # Button to continue / cancel, not ready for the moment
        # self.button1 = QPushButton("大丈夫")
        # self.button2 = QPushButton(" キャンセル ")
        #
        # self.layout.addWidget(self.button1)
        # self.layout.addWidget(self.button2)
        # self.layout.addStretch(1)
        self.setLayout(self.main_layout)

        # self.button1.clicked.connect(self.load_parameters)
        # self.button2.clicked.connect(QApplication.instance().quit)

    def create_widgets(self, cicada_analysis):
        """

        :param all_params: list of dict
        :return:
        """
        self.cicada_analysis = cicada_analysis
        all_params = cicada_analysis.get_params_for_gui()
        if all_params is None:
            all_params = []

        self.scrollAreaWidgetContents = QWidget()
        # self.scrollAreaWidgetContents.resize(300, 500)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        # ==============================

        label_param = QLabel("Parameters :")
        label_param.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        label_param.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.layout.addWidget(label_param)

        # Be careful of the order of classes : put more selective classes at first !
        all_widgets_type = [ParamSpinBox(), ParamComboBox(), ParamCheckBox(), ParamSlider(),
                            ParamDateTime(), ParamLineEdit()]
        param_input_by_type = [WidgetType.get_param_input(all_params=all_params) for WidgetType in all_widgets_type]

        all_widgets = []

        for idx_widget_type, widget_type in enumerate(param_input_by_type):
            for param in widget_type:
                widget = all_widgets_type[idx_widget_type]
                # if hasattr(widget, "setWindowFlags"):
                widget.set_param(param)
                widget.create_widget()
                widget.connect_widget()
                widget.add_widget_to_layout(self.layout)
                widget.widget.setStyleSheet(
                    "background-color:transparent")
                # widget.widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                # widget.widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                all_widgets.append(widget)

        # # Button to continue / cancel, not ready for the moment
        self.button1 = QPushButton("大丈夫")
        self.button1.setStyleSheet(
            "background-color:transparent")
        self.button1.clicked.connect(self.launch_analysis)
        self.layout.addWidget(self.button1)
        # self.layout.addWidget(self.button2)
        self.layout.addStretch(1)

    def launch_analysis(self):
        """
        Launch analysis, passing the right parameters to the function analysis
        :return:
        """
        # TODO: Add params to the run_analysis
        kwargs = dict()
        self.cicada_analysis.run_analysis(**kwargs)

    def keyPressEvent(self, event):
        available_background = ["black_widow.png", "captain_marvel.png", "iron_man.png", "hulk.png"]
        if event.key() == QtCore.Qt.Key_A:
            if self.special_background_on:
                self.scrollAreaWidgetContents.setStyleSheet(
                    ".QWidget{background-image:url(\"\"); background-position: center;}")
                self.special_background_on = False
            else:
                pic_index = randint(0, len(available_background) - 1)
                # we add .QWidget so the background is specific to this widget and is not applied by other widgets
                self.scrollAreaWidgetContents.setStyleSheet(
                    ".QWidget{background-image:url(\"cicada/gui/icons/rc/" + available_background[pic_index] +
                    "\"); background-position: center; background-repeat:no-repeat;}")
                self.special_background_on = True

    # Will be used at the end to start the analysis, but not done yet !
    def load_parameters(self):
        QMessageBox.warning(self, "Proverbe du jour :",
                            "しかし、あなたが知っている、私は良いまたは悪い状況があるとは思わないが、\n"
                            "私はあなたと今日の私の人生を要約するとした場合、私はそれが私に手を差し伸べ\n"
                            "る最初と何よりも私ができなかった時、私は一人で家にいた時、そして事故に遭遇し\n"
                            "たということは運命を偽造すると言うのはむしろ好奇心が強いです。あなたが物の味を\n"
                            "持っているとき、あなたは物事の味を持っているとき、美しいジェスチャー、\n"
                            "時には私たちは反対の人を見つけられない、私は言うだろう、あなたが前進する\n"
                            "のに役立ちます鏡。私がそこに言ったように、私はそうではありません、私は逆に、\n"
                            "私は可能であり、私はあなたに人生に感謝すると言うので、私はあなたに感謝すると言\n"
                            "います。今日の多くの人が私に言っています、「しかし、どうやってこの人間性を持って\n"
                            "いるのですか」、私は彼らに非常に簡単に答えます、それが愛のこの味なのです。機械的な\n"
                            "構造を始めるために、しかし明日、知っている、多分私達をコミュニティの奉仕に置くために、\n"
                            "贈り物をするために、自分自身の贈り物を…,\n\n"
                            "Mais, vous savez, moi je ne crois pas qu'il y ait de bonne ou de mauvaise situation.\n"
                            " Moi, si je devais résumer ma vie aujourd'hui avec vous, je dirais que c'est d'abord\n"
                            " des rencontres, des gens qui m'ont tendu la main, peut-être à un moment où je ne\n"
                            " pouvais pas, où j'étais seul chez moi. Et c'est assez curieux de se dire que les \n"
                            "hasards, les rencontres forgent une destinée... Parce que quand on a le goût de la\n"
                            " chose, quand on a le goût de la chose bien faite, le beau geste, parfois\n"
                            " on ne trouve pas l'interlocuteur en face, je dirais, le miroir qui vous aide\n"
                            " à avancer. Alors ce n'est pas mon cas, comme je le disais là, puisque moi\n"
                            " au contraire, j'ai pu ; et je dis merci à la vie, je lui dis merci,\n"
                            " je chante la vie, je danse la vie... Je ne suis qu'amour ! Et finalement, \n"
                            " quand beaucoup de gens aujourd'hui me disent : Mais comment fais-tu pour avoir \n"
                            " cette humanité ?, eh ben je leur réponds très simplement, je leur dis que c'est \n"
                            " ce goût de l'amour, ce goût donc qui m'a poussé aujourd'hui à entreprendre une\n"
                            " construction mécanique, mais demain, qui sait, peut-être seulement à me mettre\n"
                            " au service de la communauté, à faire le don, le don de soi...",
                            QMessageBox.Cancel)
        QApplication.instance().quit()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    set_param = MainWindow()
    set_param.show()
    sys.exit(app.exec_())
