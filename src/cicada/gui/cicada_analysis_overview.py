from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
import numpy as np
from qtpy import QtCore
from random import randint
from cicada.gui.cicada_analysis_parameters_gui import AnalysisParametersApp, AnalysisPackage
import gc
from functools import partial


class AnalysisOverview(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.special_background_on = False
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"
        self.created_analysis_names = []

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
        self.run_analysis_button.setEnabled(True)
        self.run_analysis_button.clicked.connect(self.add_analysis_overview)

        self.main_layout.addWidget(self.run_analysis_button)
        self.setLayout(self.main_layout)

    def add_analysis_overview(self, analysis_name, analysis_id, obj):
        self.created_analysis_names.append(analysis_id + '_overview')
        exec('self.' + analysis_id + '_overview = AnalysisState( "' + str(obj) +
             '", self.scroll_area_widget_contents, "' + analysis_name + '")')
        eval('self.layout.addWidget(self.' + analysis_id + '_overview)')

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


class AnalysisState(QLabel):

    def __init__(self, analysis_id, parent=None,analysis_name=''):
        super().__init__(parent)
        self.setText(analysis_name)
        self.mouseDoubleClickEvent = partial(self.bring_to_front, analysis_id)


    def bring_to_front(self, window_id, event):
        """Bring analysis' window to the front"""
        for obj in gc.get_objects():
            if str(obj) == str(window_id):
                obj.setWindowState(obj.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                obj.activateWindow()
