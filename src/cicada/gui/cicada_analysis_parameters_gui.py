from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QProcess
from PyQt5 import QtCore as Core
from qtpy import QtGui
import numpy as np
from qtpy import QtCore
import sys
from random import randint
from abc import ABC, abstractmethod
from cicada.gui.cicada_analysis_overview import AnalysisOverview, AnalysisState, ResultsButton
from qtpy.QtCore import QThread
import os
from functools import partial
from time import time



class ParameterWidgetModel(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_value(self):
        """
        Return the value of the widget
        Returns:

        """
        return None

    @abstractmethod
    def set_value(self, value):
        """
        Set the widget value to the value passed
        Returns:

        """
        pass


class MyQFrame(QFrame):

    def __init__(self, analysis_arg, parent=None):
        QFrame.__init__(self, parent=parent)
        self.analysis_arg = analysis_arg

        self.v_box = QVBoxLayout()
        description = self.analysis_arg.get_description()
        if description:
            self.q_label_description = QLabel(description)
            self.q_label_description.setAlignment(Qt.AlignCenter)
            self.q_label_description.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.q_label_description.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.v_box.addWidget(self.q_label_description)

        self.setLayout(self.v_box)

        self.mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(self.mandatory))

    def change_mandatory_property(self, value):
        """
        Changing the property allowing to change the style sheet depending on the mandatory aspect of the argument
        Args:
            value:

        Returns:

        """
        self.setProperty("is_mandatory", value)
        self.style().unpolish(self)
        self.style().polish(self)

    def get_layout(self):
        return self.v_box

    def set_property_to_missing(self):
        """
        Allows the change the stylesheet and indicate the user that a
        Returns:

        """
        self.setProperty("something_is_missing", "True")


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

class FileDialogWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Create a widget that will contain a button to open a FileDialog and a label to display the file or directory choosen
    A label will also explain what this parameter do
    """

    def __init__(self, analysis_arg, directory_only, parent=None):
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)
        self.analysis_arg = analysis_arg
        # both are booleans
        # self.save_file_dialog = save_file_dialog
        self.directory_only = directory_only

        description = self.analysis_arg.get_description()
        if description is None:
            if directory_only:
                description = "Choose directory"
            else:
                description = "Choose a file or a directory"
        self.q_label_description.setText(description)

        self.file_dialog = QFileDialog(self, description)

        # setting options
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        self.file_dialog.setOptions(options)

        # ARE WE TALKING ABOUT FILES OR FOLDERS
        if directory_only:
            self.file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        else:
            self.file_dialog.setFileMode(QFileDialog.AnyFile)

        # OPENING OR SAVING
        # self.file_dialog.setAcceptMode(QFileDialog.AcceptOpen) if forOpen else \
        #     self.file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        # self.file_dialog.setSidebarUrls([QtCore.QUrl.fromLocalFile(place)])

        # SET THE STARTING DIRECTORY
        default_value = self.analysis_arg.get_default_value()
        if default_value is not None and isinstance(default_value, str):
            self.file_dialog.setDirectory(default_value)
        # else:
        #     self.file_dialog.setDirectory(str(ROOT_DIR))

        # SET FORMAT, IF SPECIFIED
        # if fmt != '' and directory_only is False:
        #     self.file_dialog.setDefaultSuffix(fmt)
        #     self.file_dialog.setNameFilters([f'{fmt} (*.{fmt})'])

        h_box = QHBoxLayout()
        select_button = QPushButton("Select", self)
        select_button.clicked.connect(self.open_dialog)
        h_box.addStretch(1)
        h_box.addWidget(select_button)
        h_box.addStretch(1)
        self.v_box.addLayout(h_box)

        label_text = ""
        if default_value is not None and isinstance(default_value, str):
            label_text = default_value
        self.q_label_path = QLabel(label_text)
        self.q_label_path.setAlignment(Qt.AlignCenter)
        self.q_label_path.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.q_label_path.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.scrollArea = QScrollArea()
        # ScrollBarAlwaysOff = 1
        # ScrollBarAlwaysOn = 2
        # ScrollBarAsNeeded = 0
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setProperty("label_path", "True")
        self.v_box.addWidget(self.scrollArea)

        self.scrollArea.setWidget(self.q_label_path)
        # v_box.addWidget(self.q_label_path)


        # def openFileNameDialog(self):
        #     options = QFileDialog.Options()
        #     setFileMode(QFileDialog.Directory)
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

    def open_dialog(self):
        if self.file_dialog.exec_() == QDialog.Accepted:
            path = self.file_dialog.selectedFiles()[0]  # returns a list
            self.file_dialog.setDirectory(path)
            self.q_label_path.setText(path)
            if self.mandatory:
                self.change_mandatory_property(value="False")

    def get_value(self):
        text = self.q_label_path.text()
        if text == "":
            return None
        return text

    def set_value(self, value):
        if value is None:
            if self.mandatory:
                self.change_mandatory_property(value="True")
            self.q_label_path.setText('')
        else:
            # then we checks if it exists
            if os.path.exists(value):
                if self.analysis_arg.is_mandatory():
                    self.change_mandatory_property(value="True")
                self.q_label_path.setText(value)
                self.file_dialog.setDirectory(value)


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
        if isinstance(default_value, str):
            default_value = [default_value]
        if choices:
            for choice in choices:
                item = QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable |
                              QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if default_value and (choice in default_value):
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)

                item.setText(str(choice))
                self.list_widget.addItem(item)

        # self.list_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.list_widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def set_value(self, value):
        """
        Set the value.
        Args:
            value: value is either a string or integer or float, or a list. If a list, then item whose value matches
            one of the elements in the list will be checkeds
        Returns: None

        """
        # first we uncheck them all
        for i in np.arange(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        if value is None:
            return

        if not isinstance(value, list):
            values = [value]
        else:
            values = value

        # then we find the item that match the values and checked them
        for value in values:
            items = self.list_widget.findItems(value, Qt.MatchExactly)
            for item in items:
                item.setCheckState(QtCore.Qt.Checked)

    def get_value(self):
        checked_items = []
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).checkState() == 2:
                checked_items.append(self.list_widget.item(index).text())

        if self.analysis_arg.get_default_value() and (len(checked_items) == 0):
            # then we put the default value as results
            checked_items.append(self.analysis_arg.get_default_value())

        return checked_items


class LineEditWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg

        self.line_edit = QLineEdit()

        if self.analysis_arg.get_default_value():
            self.line_edit.setText(self.analysis_arg.get_default_value())

        h_box = QHBoxLayout()
        h_box.addWidget(self.line_edit)
        self.v_box.addLayout(h_box)
        # h_box.addStretch(1)

    def set_value(self, value):
        if value is not None:
            self.line_edit.setText(value)

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

    def set_value(self, value):
        """
        Set a new value.
        Either value is None and nothing will happen
        If value is a list instance,
        Args:
            value:

        Returns:

        """
        if value is None:
            return

        if isinstance(value, dict):
            # means each key represent the session_id and the value the default value
            for session_id, value_to_set in value.items():
                # first checking is the session exists
                if session_id not in self.combo_boxes:
                    continue
                combo_box = self.combo_boxes[session_id]
                index = combo_box.findData(value_to_set)
                # -1 for not found
                if index != -1:
                    combo_box.setCurrentIndex(index)
        else:
            # otherwise we look for the value in each of the combo_box
            for combo_box in self.combo_boxes.values():
                index = combo_box.findData(value)
                # -1 for not found
                if index != -1:
                    combo_box.setCurrentIndex(index)


    def get_value(self):
        if len(self.combo_boxes) == 1:
            for combo_box in self.combo_boxes.values():
                return combo_box.currentText()
        result_dict = dict()
        for session_id, combo_box in self.combo_boxes.items():
            result_dict[session_id] = combo_box.currentText()
        return result_dict


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

    def set_value(self, value):
        if value is None:
            value = False
        self.check_box.setChecked(value)

    def get_value(self):
        return self.check_box.isChecked()


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

    def set_value(self, value):
        if value is not None:
            self.spin_box.setValue(value)

    def get_value(self):
        return self.slider.value()


class AnalysisParametersApp(QWidget):
    """Class containing the parameters widgets"""
    def __init__(self, thread_name, progress_bar, height_main_window, parent=None):
        QWidget.__init__(self)
        self.name = thread_name
        self.parent = parent
        self.thread_list = []
        self.progress_bar = progress_bar
        self.setFixedHeight(int(height_main_window * 0.70))
        self.special_background_on = False
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"
        self.cicada_analysis = None
        self.dataView = None
        self.analysis_tree_model = None
        # will be initialize when the param section will have been created
        self.param_section_widget = None
        self.analysis_arguments_handler = None
        # use for multithreading

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

        self.load_arguments_button = QPushButton("Load arguments", self)
        self.load_arguments_button.setEnabled(True)
        self.load_arguments_button.clicked.connect(self.load_arguments)

        self.reset_arguments_button = QPushButton("Reset arguments to default value", self)
        self.reset_arguments_button.setEnabled(True)
        self.reset_arguments_button.clicked.connect(self.reset_arguments)
        # self.main_layout.addWidget(self.run_analysis_button)

        self.setLayout(self.main_layout)
        # self.show()

    def load_arguments(self):
        """
        Will open a FileDialog to select a yaml file used to load arguments used for a previous analysis

        """
        file_dialog = QFileDialog(self, "Loading arguments")

        # setting options
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        file_dialog.setOptions(options)

        # ARE WE TALKING ABOUT FILES OR FOLDERS
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Yaml files (*.yml *.yaml)")

        # OPENING OR SAVING
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)


        # SET THE STARTING DIRECTORY
        # default_value = self.analysis_arg.get_default_value()
        # if default_value is not None and isinstance(default_value, str):
        #     self.file_dialog.setDirectory(default_value)

        if file_dialog.exec_() == QDialog.Accepted:
            yaml_file = file_dialog.selectedFiles()[0]
            self.analysis_arguments_handler.load_analysis_argument_from_yaml_file(yaml_file)

    def tabula_rasa(self):
        """
        Erase the widgets and make an empty section

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
            cicada_analysis (CicadaAnalysis): Chosen analysis

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

    def reset_arguments(self):
        """Reset all arguments to default value"""
        self.analysis_arguments_handler.set_widgets_to_default_value()

    def run_analysis(self):
        """Check if the parameters are valid and then create a thread which will run the analysis"""
        if self.analysis_arguments_handler is None:
            return

        # first we check if analysis_arguments are filled correctly
        if not self.analysis_arguments_handler.check_arguments_validity():
            return

        # first we disable the button so we can launch a given analysis only once
        self.run_analysis_button.setEnabled(False)
        self.worker = Worker(self.name, self.cicada_analysis, self.analysis_arguments_handler, self.parent)
        self.thread_list.append(self.worker)
        self.worker.updateProgress.connect(self.progress_bar.update_progress_bar)
        self.worker.updateProgress2.connect(self.progress_bar.update_progress_bar_overview)
        self.worker.start()

class EmittingStream(QtCore.QObject):
    """Class managing the std.out redirection"""
    def __init__(self, parent=None):
        self.parent = parent
        self.terminal = sys.stdout
        self.textWritten = QtCore.Signal(str)

    def write(self, text):
        """
        Override of the write function used to display output
        Args:
            text (str): Python output from stdout

        """
        # Add thread name to the output when writting in the the widget
        current_thread = QThread.currentThread()
        thread_text = text + str(current_thread.name)
        self.terminal.write(str(text))
        dir_path = current_thread.cicada_analysis.get_results_path()
        self.parent.normalOutputWritten(thread_text, dir_path)


    def flush(self):
        pass


class EmittingErrStream(QtCore.QObject):
    """Class managing the std.err redirection"""
    def __init__(self, parent=None):
        self.parent = parent
        self.terminal = sys.stderr
        self.errWritten = QtCore.Signal(str)


    def write(self, text):
        """
        Override of the write function used to display output
        Args:
            text (str): Python output from stdout

        """

        # Add thread name to the output when writting in the the widget

        current_thread = QThread.currentThread()
        thread_text = text + str(current_thread.name)
        self.terminal.write(str(text))
        dir_path = current_thread.cicada_analysis.get_results_path()
        self.parent.errOutputWritten(thread_text, dir_path)

    def flush(self):
        pass

class AnalysisData(QWidget):

    def __init__(self, cicada_analysis, arguments_section_widget, parent=None):
        QWidget.__init__(self, parent=parent)
        # self.special_background_on_list = False
        # self.special_background_on_text = False
        self.layout = QVBoxLayout()
        # self.q_list = QListWidget()
        # self.q_list.keyPressEvent = self.on_key_press_list
        # self.analysis_description = QTextEdit()
        # self.analysis_description.keyPressEvent = self.on_key_press_text
        # self.analysis_description.append(analysis_description)
        # to jump a line
        # self.populate_session_list(session_list)
        # self.layout.addWidget(self.q_list)

        self.analysis_state = AnalysisState(analysis_id=None, cicada_analysis=cicada_analysis,
                                       without_bringing_to_front=True)

        self.layout.addLayout(self.analysis_state)
        self.layout.addStretch(1)
        self.layout.addWidget(arguments_section_widget.reset_arguments_button)
        self.layout.addWidget(arguments_section_widget.load_arguments_button)
        self.layout.addWidget(arguments_section_widget.run_analysis_button)

        self.setLayout(self.layout)

    def populate_session_list(self, session_list):
        """
        Add all session to the QListWidget
        Args:
            session_list (list): List of all sessions' identifier

        """
        for session in session_list:
            item = QListWidgetItem()
            item.setText(str(session.identifier))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            self.q_list.addItem(item)

    def on_key_press_list(self, event):
        if event.key() == QtCore.Qt.Key_J:
            if self.special_background_on_list:
                self.current_style_sheet_background_list = "background-image:url(\"\"); background-position: center;"
                self.q_list.setStyleSheet(self.current_style_sheet_background_list)
                self.special_background_on_list = False
            else:
                # we add .QWidget so the background is specific to this widget and is not applied by other widgets
                self.current_style_sheet_background_list = "background-image:url(\"cicada/gui/icons/rc/test.jpg\");" \
                                                           "background-position: center; background-repeat:no-repeat;"
                self.q_list.setStyleSheet(self.current_style_sheet_background_list)
                self.special_background_on_list = True

    def on_key_press_text(self, event):
        if event.key() == QtCore.Qt.Key_J:
            if self.special_background_on_text:
                self.current_style_sheet_background_text = "background-image:url(\"\"); background-position: center;"
                self.analysis_description.setStyleSheet(self.current_style_sheet_background_text)
                self.special_background_on_text = False
            else:
                pic_index = 0
                # we add .QWidget so the background is specific to this widget and is not applied by other widgets
                self.current_style_sheet_background_text = "background-image:url(\"cicada/gui/icons/rc/test2.jpg\");" \
                                                           "background-position: center; background-repeat:no-repeat;"
                self.analysis_description.setStyleSheet(self.current_style_sheet_background_text)
                self.special_background_on_text = True


class AnalysisPackage(QWidget):
    """Widget containing the whole analysis window"""

    def __init__(self, cicada_analysis, analysis_name, name, main_window, parent=None):
        """

        Args:
            cicada_analysis (CicadaAnalysis): Chosen analysis
            analysis_name (str): Analysis name
            name (str): Analysis ID
        """
        QWidget.__init__(self)
        super().__init__()
        self.name = name
        self.parent = parent
        self.main_window = main_window
        self.closeEvent = self.on_close
        height_window = 750
        self.resize(1000, height_window)
        # self.setFixedSize(self.size())
        self.remaining_time_label = RemainingTime()
        self.progress_bar = ProgressBar(self.remaining_time_label, parent=self)
        self.progress_bar.setEnabled(False)
        cicada_analysis.progress_bar_analysis = self.progress_bar
        # print(cicada_analysis.analysis_arguments_handler)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_output = QLabel()
        self.text_output.setWordWrap(True)
        self.text_output.setAlignment(Qt.AlignLeft)
        self.text_output.setAlignment(Qt.AlignTop)
        self.text_output.show()

        self.scrollAreaErr = QScrollArea()
        self.scrollAreaErr.setWidgetResizable(True)
        self.scrollAreaErr.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollAreaErr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_output_err = QLabel()
        self.text_output_err.setStyleSheet("color: red;")
        self.text_output_err.setWordWrap(True)
        self.text_output_err.setAlignment(Qt.AlignLeft)
        self.text_output_err.setAlignment(Qt.AlignTop)
        self.text_output_err.show()
        self.setWindowTitle(analysis_name)
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()

        self.arguments_section_widget = AnalysisParametersApp(thread_name=self.name, progress_bar=self.progress_bar,
                                                              height_main_window=height_window, parent=self)
        self.arguments_section_widget.create_widgets(cicada_analysis=cicada_analysis)

        self.analysis_data = AnalysisData(cicada_analysis=cicada_analysis,
                                          arguments_section_widget=self.arguments_section_widget)
        self.hlayout.addWidget(self.analysis_data)

        self.hlayout.addWidget(self.arguments_section_widget)

        self.layout.addLayout(self.hlayout)
        self.hlayout2 = QHBoxLayout()
        self.hlayout2.addWidget(self.progress_bar)
        self.hlayout2.addWidget(self.remaining_time_label)
        self.layout.addLayout(self.hlayout2)
        # self.layout.addWidget(self.text_output)
        self.scrollArea.setWidget(self.text_output)
        self.scrollAreaErr.setWidget(self.text_output_err)
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(self.scrollAreaErr)
        self.setLayout(self.layout)
        self.show()

    def normalOutputWritten(self, text, path):
        """
        Append std.out text to the QLabel and create a log file.

        Args:
            text (str): Output of the standard output in python interpreter
            path (str): path where we will output the log file
        """
        if self.name in text:
            text = text.replace(self.name, "\n")
            text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])

            text = self.text_output.text() + text
            self.text_output.setText(text)
            self.scrollArea.verticalScrollBar().setSliderPosition(self.text_output.height())
            file = open(os.path.join(path, "log.txt"), "w+")
            file.write(str(self.text_output.text()))
            file.close()

    def errOutputWritten(self, text, path):
        """
        Append std.err text to the QLabel and create an err file.

        Args:
            text (str): Output of the standard output in python interpreter
            path (str): path where we will output the err file

        """

        if self.name in text:
            text = text.replace(self.name, "\n")
            text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])
            text = self.text_output_err.text() + text
            self.text_output_err.setText(text)
            self.scrollAreaErr.verticalScrollBar().setSliderPosition(self.text_output.height())
            file = open(os.path.join(path, "err.txt"), "w+")
            file.write(str(self.text_output_err.text()))
            file.close()



    def on_close(self, event):
        """
        Check if an analysis is still on going and prompt the user to let him know then ask whether he still wants to
        close. If yes, delete the associated overview and stop the thread

        Args:
            event (QEvent): Qt Event triggered when attempting to close the window

        """
        thread_found = False
        for thread in self.arguments_section_widget.thread_list:
            if thread.name == self.name:
                thread_found = True
                if thread.run_state:
                    self.confirm_quit = QMessageBox()
                    self.confirm_quit.setWindowTitle("CICADA")
                    self.confirm_quit.setText("The analysis is still ongoing, do you still want to quit ?")
                    self.confirm_quit.setStandardButtons(QMessageBox.Yes)
                    self.confirm_quit.addButton(QMessageBox.No)
                    self.confirm_quit.setDefaultButton(QMessageBox.No)
                    if self.confirm_quit.exec() == QMessageBox.Yes:
                        self.progress_bar.setEnabled(False)
                        self.main_window.object_created.remove(self)
                        thread.terminate()
                        obj = self.parent.analysis_overview
                        for attr in dir(obj):
                            if self.name in attr:
                                if "layout" in attr:
                                    eval('obj.layout.removeItem( obj.' + attr + ')')
                                else:
                                    eval('obj.' + attr + '.setParent(None)')
                                    eval('obj.' + attr + '.deleteLater()')
                    else:
                        event.ignore()

                else:
                    self.main_window.object_created.remove(self)
                    obj = self.parent.analysis_overview
                    for attr in dir(obj):
                        if self.name in attr:
                            if "layout" in attr:
                                eval('obj.layout.removeItem( obj.' + attr + ')')
                            else:
                                eval('obj.' + attr + '.setParent(None)')
                                eval('obj.' + attr + '.deleteLater()')
        if not thread_found:
            self.main_window.object_created.remove(self)
            obj = self.parent.analysis_overview
            for attr in dir(obj):
                if self.name in attr:
                    if "layout" in attr:
                        eval('obj.layout.removeItem( obj.' + attr + ')')
                    else:
                        eval('obj.' + attr + '.setParent(None)')
                        eval('obj.' + attr + '.deleteLater()')



class Worker(QtCore.QThread):
    """Thread to manage multiple analysises at the same time"""

    # Signals to update the progress bar in the analysis window and overview
    updateProgress = QtCore.Signal(float, float, float)
    updateProgress2 = QtCore.Signal(str, float, float)

    def __init__(self, name, cicada_analysis, analysis_arguments_handler, parent):
        """

        Args:
            name (str): Analysis ID, should be unique
            cicada_analysis (CicadaAnalysis): the analysis run in the thread
            analysis_arguments_handler:
        """
        QtCore.QThread.__init__(self)
        self.name = name
        self.parent = parent
        self.run_state = False
        self.cicada_analysis = cicada_analysis
        self.analysis_arguments_handler = analysis_arguments_handler

    def run(self):
        """Run the analysis"""
        self.run_state = True
        sys.stdout = EmittingStream(self.parent)
        # Comment to debug, else we will get unhandled python exception
        # sys.stderr = EmittingErrStream(self.parent)
        self.analysis_arguments_handler.run_analysis()
        self.set_results_path(self.cicada_analysis.get_results_path())
        self.setProgress(self.name, new_set_value=100)
        self.run_state = False

    def setProgress(self, name, time_started=0, increment_value=0, new_set_value=0):
        """
        Emit the new value of the progress bar and time remaining

        Args:
            name (str): Analysis ID
            time_started (float): Start time of the analysis
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar


        """
        self.updateProgress.emit(time_started, increment_value, new_set_value)
        self.updateProgress2.emit(name, increment_value, new_set_value)

    def set_results_path(self, results_path):
        """
        Set the selected path to the results in the "Open result folder" button in the corresponding overview

        Args:
            results_path (str): Path to the results

        """
        # TODO : Get rid of the garbage collector
        obj = self.parent.analysis_overview
        if eval('obj.' + self.name + '_button.result_path') is None:
            exec('obj.' + self.name + '_button.result_path = "' + results_path + '"')
            eval('obj.' + self.name + '_button.result_button.setEnabled(True)')
        else:
            pass

class ProgressBar(QProgressBar):
    """Class containing the progress bar of the current analysis"""
    def __init__(self, remaining_time_label, parent=None):
        """

        Args:
            remaining_time_label: Associated analysis remaining time
        """
        QProgressBar.__init__(self)
        self.setMinimum(0)
        self.parent=parent
        self.remaining_time_label = remaining_time_label

    def update_progress_bar(self, time_started, increment_value=0, new_set_value=0):
        """
        Update the progress bar in the analysis widget and the corresponding remaining time
        Args:
            time_started (float): Start time of the analysis
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar

        Returns:

        """
        self.current_thread = QThread.currentThread()
        self.setEnabled(True)
        if new_set_value != 0:
            self.setValue(new_set_value)

        if increment_value != 0:
            self.setValue(self.value() + increment_value)

        if self.isEnabled() and self.value() != 0:
            if self.value() == 100:
                self.remaining_time_label.update_remaining_time(self.value(), time_started, True)
            else:
                self.remaining_time_label.update_remaining_time(self.value(), time_started)

    def update_progress_bar_overview(self, name, increment_value=0, new_set_value=0):
        """
        Update the overview progress bar

        Args:
            name (str): Analysis ID
            time_started (float): Start time of the analysis
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar

        """
        obj = self.parent.parent.analysis_overview
        try:
            eval('obj.' + name + '_progress_bar.setEnabled(True)')
            if new_set_value != 0:
                eval('obj.' + name + '_progress_bar.setValue(new_set_value)')

            if increment_value != 0:
                eval('obj.' + name + '_progress_bar.setValue(obj.' + name +
                     '_progress_bar.value() + increment_value)')

            if eval('obj.' + name + '_progress_bar.isEnabled()') and eval(
                    'obj.' + name + '_progress_bar.value()') != 0:
                eval('obj.' + name + '_progress_bar.setEnabled(True)')

        except:
            pass


class RemainingTime(QLabel):
    """Class containing the remaining time of the analysis"""
    def __init__(self, parent=None):
        QLabel.__init__(self, parent=parent)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(self.size())
        self.setText("Time remaining : ")

    def update_remaining_time(self, progress_value, time_started, done=False):
        """
        Update the remaining time
        Args:
            progress_value (float): Current progress bar value
            time_started (float): Start time of the analysis
            done (bool): True if the analysis is done and false if still running

        """
        if not done:
            remaining_time = ((time() - time_started) * 100) / progress_value
            time_elapsed = time() - time_started
            remaining_time_text = self.correct_time_converter(remaining_time)
            time_elapsed_text = self.correct_time_converter(time_elapsed)
            self.setText("Time remaining : " + time_elapsed_text + "/" + remaining_time_text)
        else:
            self.setText("Analysis done")

    @staticmethod
    def correct_time_converter(time):
        """
        Convert a float in a correct duration value
        Args:
            time (float): Float value to be converted in a correct duration with MM.SS

        Returns:
            time_text (str): String of the correct duration
        """
        minutes = int(time)
        seconds = int(time * 100) - minutes * 100
        minutes_to_add = seconds // 60
        seconds_remaining = seconds % 60
        seconds_remaining_text = str(seconds_remaining)
        if len(seconds_remaining_text) == 1:
            seconds_remaining_text = "0" + seconds_remaining_text
        time_text = str(minutes + minutes_to_add) + "." + seconds_remaining_text
        return time_text

def clearvbox(self, L=False):
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
