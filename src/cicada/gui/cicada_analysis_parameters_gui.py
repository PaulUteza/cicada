from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QProcess
from PyQt5 import QtCore as Core
from qtpy import QtGui
import numpy as np
from qtpy import QtCore
import sys
from random import randint
from abc import ABC, abstractmethod


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

    # TODO: add set_value, allow to load params from a file for ex, though AnalysisArgumentHandler


class MyQFrame(QFrame):

    def __init__(self, analysis_arg, parent=None):
        QFrame.__init__(self, parent=parent)
        self.analysis_arg = analysis_arg

        self.v_box = QVBoxLayout()
        description = self.analysis_arg.get_description()
        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.v_box.addWidget(q_label)

        self.setLayout(self.v_box)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def get_layout(self):
        return self.v_box

# to resolve: TypeError: metaclass conflict: the metaclass of a derived class
# must be a (non-strict) subclass of the metaclasses of all its bases
# might not be a good idea to do multiple-heritage with a Qclass
# solution from: https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
# http://www.phyast.pitt.edu/~micheles/python/metatype.html
class FinalMeta(type(ParameterWidgetModel), type(QWidget)):
    pass

# TODO: some of the widgets to add
#  - choose directory
#  - choose a color
#  -

class FileDialogWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Create a widget that will contain a button to open a FileDialog and a label to display the file or directory choosen
    A label will also explain what this parameter do
    """

    def __init__(self, analysis_arg, save_file_dialog, directory_only, parent=None):
        QFrame.__init__(self, parent=parent)
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


class ListCheckboxWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
       Allows multiple choices
       """

    def __init__(self, analysis_arg, choices_attr_name, parent=None):
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.list_widget = QListWidget()
        # property is used to have a specificy stylesheet for this QList
        self.list_widget.setProperty("param", "True")

        h_box = QHBoxLayout()
        h_box.addWidget(self.list_widget)
        self.v_box.addLayout(h_box)
        # self.v_box.addStretch(1)

        choices = getattr(self.analysis_arg, choices_attr_name, None)
        default_value = self.analysis_arg.get_default_value()
        if choices:
            for choice in choices:
                item = QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable |
                              QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if default_value and (choice == default_value):
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)

                item.setText(str(choice))
                self.list_widget.addItem(item)

        # self.list_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.list_widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def get_value(self):
        checked_items = []
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).checkState() == 2:
                checked_items.append(self.list_widget.item(index).text())

        if self.analysis_arg.get_default_value() and (len(checked_items) == 0):
            # then we put the default value as results
            checked_items.append(self.analysis_arg.get_default_value())

        return checked_items


class LineEditWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg

        self.line_edit = QLineEdit()

        if self.analysis_arg.get_default_value():
            self.line_edit.setText(self.analysis_arg.get_default_value())

        v_box = QVBoxLayout()
        description = self.analysis_arg.get_description()
        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            v_box.addWidget(q_label)

        h_box = QHBoxLayout()
        h_box.addWidget(self.line_edit)
        v_box.addLayout(h_box)
        # h_box.addStretch(1)
        self.setLayout(v_box)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def get_value(self):
        return self.line_edit.text()


class ComboBoxWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg
        self.combo_boxes = dict()

        default_value = self.analysis_arg.get_default_value()

        if self.analysis_arg.choices is not None:

            # two cases, either choices is a list
            # then we're displaying option valid for all sessions
            if isinstance(self.analysis_arg.choices, list):
                # we put "toto", but it doesn't matter, if there is only one element
                # then the key won't be displayed
                self.combo_boxes["toto"] = QComboBox()
                index = 0
                for choice in self.analysis_arg.choices:
                    # need to put 2 arguments, in order to be able to find it using findData
                    self.combo_boxes["toto"].addItem(str(choice), str(choice))
                    if default_value:
                        if choice == default_value:
                            self.combo_boxes["toto"].setCurrentIndex(index)
                    index += 1
            elif isinstance(self.analysis_arg.choices, dict):
                # then each key represent a session_id and the value will be a list of choices
                index = 0
                for session_id, choices in self.analysis_arg.choices.items():
                    self.combo_boxes[session_id] = QComboBox()
                    for choice in choices:
                        # need to put 2 arguments, in order to be able to find it using findData
                        self.combo_boxes[session_id].addItem(str(choice), str(choice))
                        # TODO: implement default_value, see how make it practical
                        # if default_value:
                        #     if choice == default_value:
                        #         self.combo_box.setCurrentIndex(index)
                        index += 1

        # setting it to default if it exists
        # if self.analysis_arg.get_default_value():
        #     index = self.combo_box.findData(self.analysis_arg.get_default_value())
        #     if index >= 0:
        #         self.combo_box.setCurrentIndex(index)

        v_box = QVBoxLayout()
        description = self.analysis_arg.get_description()
        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            v_box.addWidget(q_label)



        for session_id, combo_box in self.combo_boxes.items():
            h_box = QHBoxLayout()
            if len(self.combo_boxes) > 1:
                # if more than one session_id, we display the name of the session
                q_label = QLabel(session_id)
                # q_label.setAlignment(Qt.AlignCenter)
                q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                h_box.addWidget(q_label)
                h_box.addWidget(combo_box)
            else:
                h_box.addWidget(combo_box)
            v_box.addLayout(h_box)
        # h_box.addStretch(1)
        self.setLayout(v_box)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def get_value(self):
        if len(self.combo_boxes) == 1:
            for combo_box in self.combo_boxes.values():
                return combo_box.currentText()
        result_dict = dict()
        for session_id, combo_box in self.combo_boxes.items():
            result_dict[session_id] = combo_box.currentText()


class CheckBoxWidget(QFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        QWidget.__init__(self, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg

        self.check_box = QCheckBox()

        if getattr(self.check_box, "default_value", False):
            self.check_box.setChecked(True)

        # False by default otherwise
        if self.analysis_arg.get_default_value():
            # using setCheckState make it a triState
            self.check_box.setChecked(self.analysis_arg.get_default_value())

        description = self.analysis_arg.get_description()
        if description:
            self.check_box.setText(description)
        #
        v_box = QVBoxLayout()
        # description = self.analysis_arg.get_description()
        # if description:
        #     q_label = QLabel(description)
        #     q_label.setAlignment(Qt.AlignCenter)
        #     q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #     q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #     v_box.addWidget(q_label)

        h_box = QHBoxLayout()
        h_box.addWidget(self.check_box)
        v_box.addLayout(h_box)
        # h_box.addStretch(1)
        self.setLayout(v_box)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def get_value(self):
        return self.check_box.checkState()


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

        if (self.analysis_arg.max_value is not None) and (self.analysis_arg.min_value is not None):
            self.slider.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)
            self.spin_box.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)

        if self.analysis_arg.get_default_value():
            self.slider.setValue(self.analysis_arg.get_default_value())
            self.spin_box.setValue(self.analysis_arg.get_default_value())

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
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"
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
        self.run_analysis_button.setEnabled(False)
        self.run_analysis_button.clicked.connect(self.run_analysis)
        self.main_layout.addWidget(self.run_analysis_button)

        self.setLayout(self.main_layout)
        # self.show()


    def tabula_rasa(self):
        """
        Erase the widgets and make an empty section
        Returns:

        """
        # clearing the widget to update it
        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_widget_contents.setStyleSheet(self.current_style_sheet_background)
        self.run_analysis_button.setEnabled(False)


    def create_widgets(self, cicada_analysis):
        """

        Args:
            cicada_analysis:

        Returns:

        """
        self.cicada_analysis = cicada_analysis

        # clearing the widget to update it
        self.tabula_rasa()
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
        self.run_analysis_button.setEnabled(True)

    def keyPressEvent(self, event):
        available_background = ["black_widow.png", "captain_marvel.png", "iron_man.png", "hulk.png"]
        if event.key() == QtCore.Qt.Key_A:
            if self.special_background_on:
                self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"
                self.scroll_area_widget_contents.setStyleSheet(self.current_style_sheet_background)
                self.special_background_on = False
            else:
                pic_index = randint(0, len(available_background) - 1)
                # we add .QWidget so the background is specific to this widget and is not applied by other widgets
                self.current_style_sheet_background = ".QWidget{background-image:url(\"cicada/gui/icons/rc/" + \
                                                      available_background[pic_index] + \
                                                      "\"); background-position: center; background-repeat:no-repeat;}"
                self.scroll_area_widget_contents.setStyleSheet(self.current_style_sheet_background)
                self.special_background_on = True

    def run_analysis(self):
        if self.analysis_arguments_handler is None:
            return

        self.analysis_arguments_handler.run_analysis()


class EmittingStream(QtCore.QObject):

    textWritten = Core.pyqtSignal(str)

    def write(self, text):
        # QMessageBox.critical(None, str(text), str(text))
        self.textWritten.emit(str(text))

class AnalysisData(QWidget):

    def __init__(self, session_list, analysis_description, parent=None):
        QWidget.__init__(self, parent=parent)
        self.layout = QVBoxLayout()
        self.q_list = QListWidget()
        self.analysis_description = QTextEdit()
        self.analysis_description.append(analysis_description)
        self.analysis_description.setReadOnly(True)
        self.populate_session_list(session_list)
        self.layout.addWidget(self.q_list)
        self.layout.addWidget(self.analysis_description)
        self.setLayout(self.layout)

    def populate_session_list(self, session_list):
        for session in session_list:
            item = QListWidgetItem()
            item.setText(str(session.identifier))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            self.q_list.addItem(item)

class AnalysisPackage(QWidget):

    def __init__(self, cicada_analysis, analysis_name, analysis_description, parent=None):
        QWidget.__init__(self, parent=parent)
        super().__init__()
        # print(cicada_analysis.analysis_arguments_handler)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.resize(1000, 750)
        self.setWindowTitle(analysis_name)
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.analysis_data = AnalysisData(cicada_analysis._data_to_analyse, analysis_description)
        self.hlayout.addWidget(self.analysis_data)
        self.arguments_section_widget = AnalysisParametersApp()
        self.arguments_section_widget.create_widgets(cicada_analysis=cicada_analysis)
        self.hlayout.addWidget(self.arguments_section_widget)
        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.text_output)
        self.setLayout(self.layout)
        self.show()



    def normalOutputWritten(self, text):
        """
        Append text to the QTextEdit.

        Args:
            text (str): Output of the standard output in python interpreter
        """
        cursor = self.text_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.text_output.setTextCursor(cursor)
        self.text_output.ensureCursorVisible()

    def closeEvent(self, QCloseEvent):
        sys.stdout = sys.__stdout__


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