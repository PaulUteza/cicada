from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
import numpy as np
from qtpy import QtCore
from random import randint
from abc import ABC, abstractmethod


# TODO: Class that represent a widget for a given parameter

class ParameterWidgetModel(ABC):
    def __init__(self):
        self.mandatory = False

    @abstractmethod
    def get_value(self):
        """
        Return the value of the widget
        Returns:

        """
        return None


# to resolve: TypeError: metaclass conflict: the metaclass of a derived class
# must be a (non-strict) subclass of the metaclasses of all its bases
# might not be a good idea to do multiple-heritage with a Qclass
# solution from: https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
# http://www.phyast.pitt.edu/~micheles/python/metatype.html
class FinalMeta(type(ParameterWidgetModel), type(QWidget)):
    pass


class FileDialogWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Create a widget that will contain a button to open a FileDialog and a label to display the file or directory choosen
    A label will also explain what this parameter do
    """

    def __init__(self, analysis_arg, save_file_dialog, directory_only, parent=None):
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg
        # both are booleans
        self.save_file_dialog = save_file_dialog
        self.directory_only = directory_only

        # def openFileNameDialog(self):
        #     options = QFileDialog.Options()
        #     options |= QFileDialog.DontUseNativeDialog
        #     fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                               "All Files (*);;Python Files (*.py)", options=options)
        #     if fileName:
        #         print(fileName)
        #
        # def openFileNamesDialog(self):
        #     options = QFileDialog.Options()
        #     options |= QFileDialog.DontUseNativeDialog
        #     files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
        #                                             "All Files (*);;Python Files (*.py)", options=options)
        #     if files:
        #         print(files)
        #
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
        #                                           "All Files (*);;Text Files (*.txt)", options=options)
        # if fileName:
        #     print(fileName)

        # fileDialog = QtWidgets.QFileDialog(self, "Choose directory")
        # # directory only
        # fileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        # # just list mode is quite sufficient for choosing a diectory
        # fileDialog.setViewMode(QtWidgets.QFileDialog.List)
        # # only want to to show directories
        # fileDialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        # # native dialog, at least under Ubuntu GNOME is a bit naff for choosing a directory
        # # (shows files but greyed out), so going for Qt's own cross-plaform chooser
        # fileDialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        # # get rid of (or at least grey out) file-types selector
        # fileDialog.setOption(QtWidgets.QFileDialog.HideNameFilterDetails)
        # # DontResolveSymlinks seemingly recommended by http://doc.qt.io/qt-5/qfiledialog.html#getExistingDirectory
        # # but I found it didn't make any difference (symlinks resolved anyway)
        # # fileDialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks)


class SliderWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg
        self.slider = QSlider(Qt.Horizontal)

        self.spin_box = QSpinBox()

        if self.analysis_arg.get_default_value():
            self.slider.setValue(self.analysis_arg.get_default_value())
            self.spin_box.setValue(self.analysis_arg.get_default_value())
        if (self.analysis_arg.max_value is not None) and (self.analysis_arg.min_value is not None):
            self.slider.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)
            self.spin_box.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)

        self.spin_box.valueChanged.connect(self.spin_box_value_changed)

        self.slider.valueChanged.connect(self.slider_value_changed)

        v_box = QVBoxLayout()
        description = self.analysis_arg.get_description()
        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            v_box.addWidget(q_label)

        h_box = QHBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.spin_box)
        v_box.addLayout(h_box)
        # h_box.addStretch(1)
        self.setLayout(v_box)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))


    def slider_value_changed(self, value):
        self.spin_box.setValue(value)
        # self.analysis_arg.set_argument_value(value)

    def spin_box_value_changed(self, value):
        self.slider.setValue(value)
        # self.analysis_arg.set_argument_value(value)

    def get_value(self):
        return self.slider.value()


class AnalysisParametersApp(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.special_background_on = False
        self.cicada_analysis = None
        self.dataView = None
        self.analysis_tree_model = None
        # will be initialize when the param section will have been created
        self.param_section_widget = None
        self.analysis_arguments_handler = None

        # Add the scroll bar
        # ==============================
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        # ScrollBarAlwaysOff = 1
        # ScrollBarAlwaysOn = 2
        # ScrollBarAsNeeded = 0
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        # ==============================

        self.run_analysis_button = QPushButton("Push me and then just touch me", self)
        self.run_analysis_button.clicked.connect(self.run_analysis)
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

        self.analysis_arguments_handler = self.cicada_analysis.analysis_arguments_handler

        # list of instances of AnalysisArgument
        gui_widgets = self.analysis_arguments_handler.get_gui_widgets()

        for gui_widget in gui_widgets:
            # print(f"gui_widget {gui_widget}")
            self.layout.addWidget(gui_widget)
            # See to check if gui_widget is an instance of QFrame to round the border only
            # for QFrame instances
            gui_widget.setStyleSheet(
                "background-color:transparent; border-radius: 20px;")

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

    def run_analysis(self):
        if self.analysis_arguments_handler is None:
            return

        self.analysis_arguments_handler.run_analysis()



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