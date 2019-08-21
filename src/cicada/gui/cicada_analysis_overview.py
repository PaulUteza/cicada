from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
import numpy as np
import os
from qtpy import QtCore
from qtpy.QtCore import QThread
from random import randint
# from cicada.gui.cicada_analysis_parameters_gui import AnalysisPackage
import gc
from functools import partial
import subprocess
from time import time, sleep
import sys


class AnalysisOverview(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.special_background_on = False
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"
        self.created_analysis_names = []
        self.created_analysis = []
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
        # we add strech now and we will insert new widget before the strech
        self.layout.addStretch(1)
        # ==============================
        self.setLayout(self.main_layout)

    def add_analysis_overview(self, cicada_analysis, analysis_id, obj):
        """
        Add a widget to track the corresponding analysis
        Args:
            cicada_analysis (CicadaAnalysis): CicadaAnalysis instance
            analysis_id (str): Randomly generated ID linked to the analysis
            obj (object): The analysis window's object itself

        """
        self.created_analysis_names.append(analysis_id + '_overview')

        setattr(self, analysis_id + '_overview', AnalysisState(analysis_id=obj, cicada_analysis=cicada_analysis,
                                                               parent=self.scroll_area_widget_contents))
        analysis_overview = getattr(self, analysis_id + '_overview')

        # self.layout.addWidget(analysis_overview)
        self.layout.insertLayout(self.layout.count() - 1, analysis_overview)
        # analysis_overview.setStyleSheet("background-color:transparent; border-radius: 20px;")
        setattr(self, 'hlayout_' + analysis_id, QHBoxLayout())
        h_layout = getattr(self, 'hlayout_' + analysis_id)
        # setattr(self, analysis_id + '_remaining_time_label', RemainingTime())
        # exec('self.' + analysis_id + '_remaining_time_label = RemainingTime()')
        setattr(self, analysis_id + '_progress_bar', QProgressBar())
        # exec('self.' + analysis_id + '_progress_bar = QProgressBar()')
        h_layout.addWidget(getattr(self, analysis_id + '_progress_bar'))
        setattr(self, analysis_id + '_button', ResultsButton(cicada_analysis=cicada_analysis))
        results_button = getattr(self, analysis_id + '_button')
        # eval('self.hlayout_' + analysis_id + '.addWidget(self.' + analysis_id + '_remaining_time_label)')
        self.layout.insertLayout(self.layout.count() - 1, h_layout)
        self.layout.insertLayout(self.layout.count() - 1, results_button)
        # self.layout.addLayout(h_layout)


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


class AnalysisState(QHBoxLayout):

    def __init__(self, analysis_id, cicada_analysis, parent=None, without_bringing_to_front=False):
        super().__init__(parent)

        self.q_scroll_bar = QScrollArea()
        # self.h_layout = QHBoxLayout()
        property_value = "True"
        if without_bringing_to_front:
            # this way we can remove the change of color for QLabel when hover state
            # and we can increase the max-height of the scrollbar
            property_value = "False"

        self.q_label_analysis_name = QLabel()
        self.q_label_analysis_name.setText(cicada_analysis.name)
        self.q_label_analysis_name.setAlignment(Qt.AlignCenter)
        # use for personnalized style-sheet
        self.q_label_analysis_name.setProperty("state", property_value)
        self.setProperty("state", "True")
        if not without_bringing_to_front:
            self.q_label_analysis_name.mouseDoubleClickEvent = partial(self.bring_to_front, analysis_id)
        self.addWidget(self.q_label_analysis_name)

        data_identifiers = "\n".join(cicada_analysis.get_data_identifiers())
        self.q_label_data_identifiers = QLabel()
        self.q_label_data_identifiers.setText(data_identifiers)
        self.q_label_data_identifiers.setAlignment(Qt.AlignCenter)
        # use for personnalized style-sheet
        self.q_label_data_identifiers.setProperty("state", property_value)
        self.q_scroll_bar.setProperty("state", property_value)

        if not without_bringing_to_front:
            self.q_label_data_identifiers.mouseDoubleClickEvent = partial(self.bring_to_front, analysis_id)

        # ScrollBarAlwaysOff = 1
        # ScrollBarAlwaysOn = 2
        # ScrollBarAsNeeded = 0
        self.q_scroll_bar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.q_scroll_bar.setWidgetResizable(True)
        self.q_scroll_bar.setWidget(self.q_label_data_identifiers)

        self.addWidget(self.q_scroll_bar)
        # self.addStretch(1)

    def bring_to_front(self, window_id, event):
        """Bring corresponding analysis window to the front (re-routed from the double click method)"""
        window_id.setWindowState(window_id.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        window_id.activateWindow()
        window_id.raise_()

    def deleteLater(self):
        try:
            self.q_label_analysis_name.deleteLater()
            self.q_label_data_identifiers.deleteLater()
        except RuntimeError:
            pass


class ResultsButton(QHBoxLayout):

    def __init__(self, cicada_analysis):
        super().__init__()
        self.result_button = QPushButton()
        self.result_button.setEnabled(False)
        self.result_button.setText('Open results folder')
        self.result_path = cicada_analysis.get_results_path()
        self.addWidget(self.result_button)
        self.result_button.clicked.connect(self.open_explorer)

    def open_explorer(self):
        if self.result_path is None:
            pass
        else:
            if sys.platform == 'darwin':
                subprocess.run(['open', '--', os.path.realpath(self.result_path)])
            elif sys.platform == 'linux2':
                subprocess.run(['xdg-open', '--', os.path.realpath(self.result_path)])
            elif sys.platform == 'win32':
                subprocess.run(['explorer', os.path.realpath(self.result_path)])

    def deleteLater(self):
        try:
            self.result_button.deleteLater()
        except RuntimeError:
            pass