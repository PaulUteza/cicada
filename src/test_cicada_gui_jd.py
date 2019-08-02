from cicada.gui.cicada_analysis_tree_gui import AnalysisTreeApp
from cicada.gui.cicada_main_window import CicadaMainWindow
import sys
# from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import *
# from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
# from qtpy.QtGui import QPalette, QColor
# import qdarkstyle
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # set the environment variable to use a specific wrapper
    # it can be set to PyQt, PyQt5, PySide or PySide2 (not implemented yet)
    # os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'

    # from https://gist.github.com/mstuttgart/37c0e6d8f67a0611674e08294f3daef7
    # dark_palette = QPalette()
    #
    # dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.WindowText, Qt.white)
    # dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    # dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    # dark_palette.setColor(QPalette.Text, Qt.white)
    # dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ButtonText, Qt.white)
    # dark_palette.setColor(QPalette.BrightText, Qt.red)
    # dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    #
    # app.setPalette(dark_palette)
    #
    # app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    # dark_style_style_sheet = qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=True)
    file_name = os.path.join(f"cicada/gui/cicada_qdarkstyle.css")
    # with open(file_name, "w", encoding='UTF-8') as file:
    #     file.write(dark_style_style_sheet)
    with open(file_name, "r", encoding='UTF-8') as file:
        dark_style_cicada_style_sheet = file.read()

    app.setStyleSheet(dark_style_cicada_style_sheet)

    cicada_main_window = CicadaMainWindow()
    # putting the window at the center of the screen
    # screenGeometry is an instance of Qrect
    screenGeometry = QApplication.desktop().screenGeometry()
    x = (screenGeometry.width() - cicada_main_window.width()) / 2
    y = (screenGeometry.height() - cicada_main_window.height()) / 2
    cicada_main_window.move(x, y)
    cicada_main_window.show()

    sys.exit(app.exec_())