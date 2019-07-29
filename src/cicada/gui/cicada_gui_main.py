import sys
from qtpy.QtWidgets import *
from qtpy import QtCore, QtGui
import os
from pynwb import NWBHDF5IO


"""
Main file to be called to launch the CICADA GUI
In test for now
"""

import random

class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.hello = ["Hallo Welt", "Hei maailma",
            "Hola Mundo", "Привет мир"]

        self.button = QPushButton("Click me!")
        self.text = QLabel("Hello World")
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.magic)

    def magic(self):
        self.text.setText(random.choice(self.hello))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # widget = MyWidget()
    # widget.show()

    nwb_files_dir = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/data/nwb_files/"
    file_names = []
    # look for filenames in the fisrst directory, if we don't break, it will go through all directories
    for (dirpath, dirnames, local_filenames) in os.walk(nwb_files_dir):
        file_names.extend(local_filenames)
        break

    data_files = []
    labels = []
    for file_name in file_names:
        if not file_name.endswith(".nwb"):
            continue
        io = NWBHDF5IO(os.path.join(nwb_files_dir, file_name), 'r')
        nwb_file = io.read()
        data_files.append(nwb_file)
        labels.append(nwb_file.identifier)

    layout = QVBoxLayout()
    q_list = QListWidget()
    layout.addWidget(q_list)
    q_list.insertItems(0, labels)
    run_analysis_button = QPushButton("Push me and then just touch me")
    layout.addWidget(run_analysis_button)
    run_analysis_button.clicked.connect(lambda: print("Satisfaction !"))
    window = QWidget()
    window.setLayout(layout)
    window.show()
    app.exec_()

    # sys.exit(app.exec_())

# def cicada_gui_main():
#     # Create the application object
#     app = QApplication(sys.argv)
#
#     # Create a simple dialog box
#     msg_box = QMessageBox()
#     msg_box.setText("Hello World!")
#     msg_box.show()
#
#     sys.exit(msg_box.exec_())
#
# cicada_gui_main()