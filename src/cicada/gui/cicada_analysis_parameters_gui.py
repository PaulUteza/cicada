from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
import numpy as np
from qtpy import QtCore
from random import randint


# TODO: Class that represent a widget for a given parameter

class ParameterWidgetModel:
    def __init__(self):
        self.mandatory = False


class SliderWidget(QWidget, ParameterWidgetModel):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg
        self.slider = QSlider(Qt.Horizontal)

        self.widget = QSpinBox()

        if self.analysis_arg.default_value is not None:
            self.slider.setValue(self.analysis_arg.default_value)
            self.widget.setValue(self.analysis_arg.default_value)
        if (self.analysis_arg.max_value is not None) and (self.analysis_arg.min_value is not None):
            self.slider.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)
            self.widget.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)

        # TODO: connect to analysisArg to change its value directly
        self.widget.valueChanged.connect(self.slider.setValue)

        self.slider.valueChanged.connect(self.widget.setValue)

        h_box = QHBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.widget)
        # h_box.addStretch(1)
        self.setLayout(h_box)




class AnalysisParametersApp(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.special_background_on = False
        self.cicada_analysis = None
        self.dataView = None
        self.analysis_tree_model = None
        # will be initialize when the param section will have been created
        self.param_section_widget = None

        # Add the scroll bar
        # ==============================
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        # ==============================

        self.run_analysis_button = QPushButton("Push me and then just touch me", self)
        # self.run_analysis_button.clicked.connect()
        self.main_layout.addWidget(self.run_analysis_button)

        self.setLayout(self.main_layout)
        # self.show()

    def create_widgets(self, cicada_analysis):
        """

        Args:
            cicada_analysis:

        Returns:

        """
        print("params create_widgets")
        self.cicada_analysis = cicada_analysis

        # clearing the widget to update it
        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        # ==============================

        analysis_arguments_handler = self.cicada_analysis.analysis_arguments_handler

        # list of instances of AnalysisArgument
        analysis_arguments = analysis_arguments_handler.get_analysis_arguments()

        for analysis_argument in analysis_arguments:
            new_widget = analysis_argument.get_gui_widget()
            print(f"new_widget {new_widget}")
            if new_widget is None:
                continue
            self.layout.addWidget(new_widget)
            new_widget.setStyleSheet(
                "background-color:transparent")

        # self.button1 = QPushButton("大丈夫")
        # self.button1.setStyleSheet(
        #     "background-color:transparent")
        # # self.button1.clicked.connect(self.launch_analysis)
        # self.layout.addWidget(self.button1)
        self.layout.addStretch(1)

    def keyPressEvent(self, event):
        available_background = ["black_widow.png", "captain_marvel.png", "iron_man.png", "hulk.png"]
        if event.key() == QtCore.Qt.Key_A:
            if self.special_background_on:
                self.scroll_area_widget_contents.setStyleSheet(
                    ".QWidget{background-image:url(\"\"); background-position: center;}")
                self.special_background_on = False
            else:
                pic_index = randint(0, len(available_background) - 1)
                # we add .QWidget so the background is specific to this widget and is not applied by other widgets
                self.scroll_area_widget_contents.setStyleSheet(
                    ".QWidget{background-image:url(\"cicada/gui/icons/rc/" + available_background[pic_index] +
                    "\"); background-position: center; background-repeat:no-repeat;}")
                self.special_background_on = True


def clearvbox(self, L = False):
    if not L:
        L = self.vbox
    if L is not None:
        while L.count():
            item = L.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()
            else:
                self.clearvbox(item.layout())