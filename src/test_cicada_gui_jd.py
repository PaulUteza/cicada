from gui.cicada_analysis_tree_gui_test import AnalysisTreeApp
import sys
from qtpy.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnalysisTreeApp()
    sys.exit(app.exec_())