from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
import numpy as np
from qtpy import QtCore
from random import randint
import sys
from abc import ABC, abstractmethod
from pynwb import NWBHDF5IO


class MetaDataFinder:

    def __init__(self, data_file):
        self.data_file = data_file
        self.metadata_from_data_file = self.get_all_metadata_in_nwb()

    def get_metadata(self, name):
        return self.metadata_from_data_file[name]

    def get_all_metadata_in_nwb(self):
        metadata_from_data_file = {
            "acquisition":  getattr(self.data_file, "acquisition"),
            "analysis":  getattr(self.data_file, "analysis"),
            "children":  getattr(self.data_file, "children"),
            "container_source":  getattr(self.data_file, "container_source"),
            "data_collection":  getattr(self.data_file, "data_collection"),
            "devices":  getattr(self.data_file, "devices"),
            "ec_electrode_groups":  getattr(self.data_file, "ec_electrode_groups"),
            "ec_electrodes":  getattr(self.data_file, "ec_electrodes"),
            "electrode_groups":  getattr(self.data_file, "electrode_groups"),
            "electrodes":  getattr(self.data_file, "electrodes"),
            "epoch_tags":  getattr(self.data_file, "epoch_tags"),
            "epochs":  getattr(self.data_file, "epochs"),
            "experiment_description":  getattr(self.data_file, "experiment_description"),
            "experimenter":  getattr(self.data_file, "experimenter"),
            "fields":  getattr(self.data_file, "fields"),
            "file_create_date":  getattr(self.data_file, "file_create_date"),
            "ic_electrodes":  getattr(self.data_file, "ic_electrodes"),
            "identifier":  getattr(self.data_file, "identifier"),
            "imaging_planes":  getattr(self.data_file, "imaging_planes"),
            "institution":  getattr(self.data_file, "institution"),
            "intervals":  getattr(self.data_file, "intervals"),
            "invalid_times":  getattr(self.data_file, "invalid_times"),
            "keywords":  getattr(self.data_file, "keywords"),
            "lab":  getattr(self.data_file, "lab"),
            "lab_meta_data":  getattr(self.data_file, "lab_meta_data"),
            "modified":  getattr(self.data_file, "modified"),
            "modules":  getattr(self.data_file, "modules"),
            "name":  getattr(self.data_file, "name"),
            "namespace":  getattr(self.data_file, "namespace"),
            "neurodata_type":  getattr(self.data_file, "neurodata_type"),
            "notes":  getattr(self.data_file, "notes"),
            "ogen_sites":  getattr(self.data_file, "ogen_sites"),
            "parent":  getattr(self.data_file, "parent"),
            "pharmacology":  getattr(self.data_file, "pharmacology"),
            "processing":  getattr(self.data_file, "processing"),
            "protocol":  getattr(self.data_file, "protocol"),
            "related_publications":  getattr(self.data_file, "related_publications"),
            "session_description":  getattr(self.data_file, "session_description"),
            "session_id":  getattr(self.data_file, "session_id"),
            "session_start_time":  getattr(self.data_file, "session_start_time"),
            "slices":  getattr(self.data_file, "slices"),
            "source_script":  getattr(self.data_file, "source_script"),
            "source_script_file_name":  getattr(self.data_file, "source_script_file_name"),
            "stimulus":  getattr(self.data_file, "stimulus"),
            "stimulus_notes":  getattr(self.data_file, "stimulus_notes"),
            "stimulus_template":  getattr(self.data_file, "stimulus_template"),
            "subject":  getattr(self.data_file, "subject"),
            "surgery":  getattr(self.data_file, "surgery"),
            "sweep_table":  getattr(self.data_file, "sweep_table"),
            "timestamps_reference_time":  getattr(self.data_file, "timestamps_reference_time"),
            "trials":  getattr(self.data_file, "trials"),
            "units":  getattr(self.data_file, "units"),
            "virus":  getattr(self.data_file, "virus")}

        return metadata_from_data_file

    def test_data_got_in_nwb(self):
        for truc in dir(self.data_file):
            if truc[0] != '_':
                print(truc)
                print(getattr(self.data_file, truc))


class CicadaMetaDataContainer:

    def __init__(self, data_file, data_format):
        self.data_file = data_file

        self.metadata_handler = MetaDataHandler(cicada_metadata_container=self)

        self.metadata_finder_wrapper = None
        self.initiate_metadata_finder_wrapper(data_format=data_format)

    def initiate_metadata_finder_wrapper(self, data_format):
        if data_format == "nwb":
            self.metadata_finder_wrapper = MetaDataFinder(self.data_file)

    def add_metadata_group_for_gui(self, **kwargs):

        self.metadata_handler.add_group(**kwargs)

    def set_metadata_for_gui(self):

        # All metadata with names, value_types, value and description !

        acquisition_metadata = {"metadata_name": "acquisition", "value_type": "dictionnary",
                                "value": self.metadata_finder_wrapper.get_metadata("acquisition"),
                                "description": "Raw TimeSeries objects belonging to this NWBFile"}

        analysis_metadata = {"metadata_name": "analysis", "value_type": "dictionnary",
                             "value": self.metadata_finder_wrapper.get_metadata("analysis"),
                             "description": "result of analysis"}

        container_source_metadata = {"metadata_name": "container_source", "value_type": "str",
                                     "value": self.metadata_finder_wrapper.get_metadata("container_source"),
                                     "description": "path to the container source"}

        data_collection_metadata = {"metadata_name": "data_collection", "value_type": "str",
                                    "value": self.metadata_finder_wrapper.get_metadata("data_collection"),
                                    "description": "Notes about data collection and analysis"}

        devices_metadata = {"metadata_name": "devices", "value_type": "dictionnary",
                            "value": self.metadata_finder_wrapper.get_metadata("devices"),
                            "description": "Device objects belonging to this NWBFile"}

        electrode_groups_metadata = {"metadata_name": "electrode_groups", "value_type": "dictionnary",
                                     "value": self.metadata_finder_wrapper.get_metadata("electrode_groups"),
                                     "description": "a dictionary containing the ElectrodeGroup in this"
                                                    " NWBFile container"}

        electrodes_metadata = {"metadata_name": "electrodes", "value_type": "dictionnary",
                               "value": self.metadata_finder_wrapper.get_metadata("electrodes"),
                               "description": "the ElectrodeTable that belongs to this NWBFile"}

        epoch_tags_metadata = {"metadata_name": "epoch_tags", "value_type": "set",
                               "value": self.metadata_finder_wrapper.get_metadata("epoch_tags"),
                               "description": "A sorted list of tags used across all epochs"}

        epochs_metadata = {"metadata_name": "epochs", "value_type": "dictionnary",
                           "value": self.metadata_finder_wrapper.get_metadata("epochs"),
                           "description": "Epoch objects belonging to this NWBFile"}

        experiment_description_metadata = {"metadata_name": "experiment_description", "value_type": "str",
                                           "value": self.metadata_finder_wrapper.get_metadata("experiment_description"),
                                           "description": "general description of the experiment"}

        experimenter_metadata = {"metadata_name": "experimenter", "value_type": "str",
                                 "value": self.metadata_finder_wrapper.get_metadata("experimenter"),
                                 "description": "name of person who performed experiment"}

        file_create_date_metadata = {"metadata_name": "file_create_date", "value_type": "datetime",
                                     "value": self.metadata_finder_wrapper.get_metadata("file_create_date"),
                                     "description": "the date and time the file was created and subsequent"
                                                    " modifications made"}

        ic_electrodes_metadata = {"metadata_name": "ic_electrodes", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("ic_electrodes"),
                                  "description": "a dictionary containing the IntracellularElectrode in this"
                                                 " NWBFile container"}

        identifier_metadata = {"metadata_name": " identifier", "value_type": "str",
                               "value": self.metadata_finder_wrapper.get_metadata(" identifier"),
                               "description": "a unique text identifier for the file"}

        imaging_planes_metadata = {"metadata_name": "imaging_planes", "value_type": "dictionnary",
                                   "value": self.metadata_finder_wrapper.get_metadata("imaging_planes"),
                                   "description": "a dictionary containing the ImagingPlane in this NWBFile container"}

        institution_metadata = {"metadata_name": "institution", "value_type": "str",
                                "value": self.metadata_finder_wrapper.get_metadata("institution"),
                                "description": "institution(s) where experiment is performed"}

        invalid_times_metadata = {"metadata_name": "invalid_times", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("invalid_times"),
                                  "description": "A table containing times to be omitted from analysis"}

        keywords_metadata = {"metadata_name": "keywords", "value_type": "list",
                             "value": self.metadata_finder_wrapper.get_metadata("keywords"),
                             "description": "Terms to search over"}

        lab_metadata = {"metadata_name": "lab", "value_type": "str",
                        "value": self.metadata_finder_wrapper.get_metadata("lab"),
                        "description": "lab where experiment was performed"}

        lab_meta_data_metadata = {"metadata_name": "lab_meta_data", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("lab_meta_data"),
                                  "description": "an extension that contains lab-specific meta-data"}

        modified_metadata = {"metadata_name": "modified", "value_type": "bool",
                             "value": self.metadata_finder_wrapper.get_metadata("modified"),
                             "description": "No description"}

        modules_metadata = {"metadata_name": "modules", "value_type": "dictionnary",
                            "value": self.metadata_finder_wrapper.get_metadata("modules"),
                            "description": "ProcessingModule objects belonging to this NWBFile"}

        neurodata_type_metadata = {"metadata_name": "neurodata_type", "value_type": "str",
                                   "value": self.metadata_finder_wrapper.get_metadata("neurodata_type"),
                                   "description": "No description"}

        notes_metadata = {"metadata_name": "notes", "value_type": "str",
                          "value": self.metadata_finder_wrapper.get_metadata("notes"),
                          "description": "Notes about the experiment"}

        ogen_sites_metadata = {"metadata_name": "ogen_sites", "value_type": "dictionnary",
                               "value": self.metadata_finder_wrapper.get_metadata("ogen_sites"),
                               "description": "OptogeneticStimulusSites that belong to this NWBFile"}

        pharmacology_metadata = {"metadata_name": "pharmacology", "value_type": "str",
                                 "value": self.metadata_finder_wrapper.get_metadata("pharmacology"),
                                 "description": "Description of drugs used, including how and when they were"
                                                " administered. Anesthesia(s), painkiller(s), etc., plus dosage,"
                                                " concentration, etc."}

        protocol_metadata = {"metadata_name": "protocol", "value_type": "str",
                             "value": self.metadata_finder_wrapper.get_metadata("protocol"),
                             "description": "Experimental protocol, if applicable. E.g., include IACUC protocol"}

        related_publications_metadata = {"metadata_name": "related_publications", "value_type": "str",
                                         "value": self.metadata_finder_wrapper.get_metadata("related_publications"),
                                         "description": "Publication information.PMID, DOI, URL, etc. If multiple,"
                                                        " concatenate together and describe which is which. such as"
                                                        " PMID, DOI, URL, etc"}

        session_description_metadata = {"metadata_name": "session_description", "value_type": "str",
                                        "value": self.metadata_finder_wrapper.get_metadata("session_description"),
                                        "description": "a description of the session where this data was generated"}

        session_id_metadata = {"metadata_name": "session_id", "value_type": "str",
                               "value": self.metadata_finder_wrapper.get_metadata("session_id"),
                               "description": "lab-specific ID for the session"}

        session_start_time_metadata = {"metadata_name": "session_start_time", "value_type": "datetime",
                                       "value": self.metadata_finder_wrapper.get_metadata("session_start_time"),
                                       "description": "the start date and time of the recording session"}

        slices_metadata = {"metadata_name": "slices", "value_type": "str",
                           "value": self.metadata_finder_wrapper.get_metadata("slices"),
                           "description": "Description of slices, including information about preparation "
                                          "thickness, orientation, temperature and bath solution"}

        source_script_metadata = {"metadata_name": "source_script", "value_type": "str",
                                  "value": self.metadata_finder_wrapper.get_metadata("source_script"),
                                  "description": "Script file used to create this NWB file"}

        source_script_file_name_metadata = {"metadata_name": "source_script_file_name", "value_type": "str",
                                            "value": self.metadata_finder_wrapper.get_metadata(
                                                "source_script_file_name"),
                                            "description": "Name of the source_script file"}

        stimulus_metadata = {"metadata_name": "stimulus", "value_type": "dictionnary",
                             "value": self.metadata_finder_wrapper.get_metadata("stimulus"),
                             "description": "Stimulus TimeSeries objects belonging to this NWBFile"}

        stimulus_notes_metadata = {"metadata_name": "stimulus_notes", "value_type": "str",
                                   "value": self.metadata_finder_wrapper.get_metadata("stimulus_notes"),
                                   "description": "Notes about stimuli, such as how and where presented"}

        stimulus_template_metadata = {"metadata_name": "stimulus_template", "value_type": "dictionnary",
                                      "value": self.metadata_finder_wrapper.get_metadata("stimulus_template"),
                                      "description": "Stimulus template TimeSeries objects belonging to this NWBFile"}

        subject_metadata = {"metadata_name": "subject", "value_type": "class",
                            "value": self.metadata_finder_wrapper.get_metadata("subject"),
                            "description": "subject metadata"}

        surgery_metadata = {"metadata_name": "surgery", "value_type": "str",
                            "value": self.metadata_finder_wrapper.get_metadata("surgery"),
                            "description": "Narrative description about surgery/surgeries,"
                                           " including date(s) and who performed surgery"}

        sweep_table_metadata = {"metadata_name": "sweep_table", "value_type": "class",
                                "value": self.metadata_finder_wrapper.get_metadata("sweep_table"),
                                "description": "the SweepTable that belong to this NWBFile"}

        timestamps_reference_time_metadata = {"metadata_name": "timestamps_reference_time", "value_type": "datetime",
                                              "value": self.metadata_finder_wrapper.get_metadata(
                                                  "timestamps_reference_time"),
                                              "description": "date and time corresponding to time zero of all "
                                                             "timestamps; defaults to value of session_start_time"}

        trials_metadata = {"metadata_name": "trials", "value_type": "class",
                           "value": self.metadata_finder_wrapper.get_metadata("trials"),
                           "description": "A table containing trial data"}

        units_metadata = {"metadata_name": "units", "value_type": "class",
                          "value": self.metadata_finder_wrapper.get_metadata("units"),
                          "description": "A table containing unit metadata"}

        virus_metadata = {"metadata_name": "virus", "value_type": "str",
                          "value": self.metadata_finder_wrapper.get_metadata("virus"),
                          "description": "Information about virus(es) used in experiments, including virus ID,"
                                         " source, date made, injection location, volume, etc."}

        # Define groups to add :

        general_metadata = dict()
        general_metadata["group_name"] = 'general_metadata'
        general_metadata["widget_type"] = 'QTable'
        general_metadata["description"] = 'metadata about session, laboratory ...'
        general_metadata["metadata_in_group"] = [session_description_metadata,
                                                 identifier_metadata,
                                                 session_start_time_metadata,
                                                 file_create_date_metadata,
                                                 experimenter_metadata,
                                                 experiment_description_metadata,
                                                 session_id_metadata,
                                                 institution_metadata,
                                                 notes_metadata,
                                                 pharmacology_metadata,
                                                 protocol_metadata,
                                                 related_publications_metadata,
                                                 slices_metadata,
                                                 source_script_metadata,
                                                 source_script_file_name_metadata,
                                                 data_collection_metadata,
                                                 surgery_metadata,
                                                 virus_metadata,
                                                 stimulus_notes_metadata,
                                                 lab_metadata,
                                                 timestamps_reference_time_metadata]

        self.add_metadata_group_for_gui(**general_metadata)

        other_metadata = dict()
        general_metadata["group_name"] = 'other_metadata'
        general_metadata["widget_type"] = 'QTable'
        general_metadata["description"] = 'metadata which are not affiliated to a group'
        general_metadata["metadata_in_group"] = [keywords_metadata,
                                                 acquisition_metadata,
                                                 analysis_metadata,
                                                 stimulus_metadata,
                                                 stimulus_template_metadata,
                                                 epochs_metadata,
                                                 epoch_tags_metadata,
                                                 trials_metadata,
                                                 invalid_times_metadata,
                                                 units_metadata,
                                                 modules_metadata,
                                                 lab_metadata,
                                                 electrodes_metadata,
                                                 electrode_groups_metadata,
                                                 ic_electrodes_metadata,
                                                 sweep_table_metadata,
                                                 imaging_planes_metadata,
                                                 ogen_sites_metadata,
                                                 devices_metadata,
                                                 subject_metadata,
                                                 neurodata_type_metadata,
                                                 lab_meta_data_metadata,
                                                 modified_metadata,
                                                 container_source_metadata
                                                 ]

    @staticmethod
    def save_changes():
        print("Ah !")


class MetaDataHandler:

    def __init__(self, cicada_metadata_container):
        self.groups_dict = dict()
        self.cicada_metadata_container = cicada_metadata_container

    def add_group(self, **kwargs):
        metadata_group = MetaDataGroup(**kwargs)
        self.groups_dict[metadata_group.group_name] = metadata_group

    def get_all_metadata_groups(self):
        all_metadata_groups = list(self.groups_dict.values())
        return all_metadata_groups

    def get_gui_widgets(self):

        gui_widgets = []
        all_metadata_groups = self.get_all_metadata_groups()
        for metadata_group in all_metadata_groups:
            widget = metadata_group.get_gui_widget()
            if widget:
                gui_widgets.append(widget)
        return gui_widgets

    def save_changes(self):
        kwargs = {}
        for metadata_name, metadata in self.groups_dict.items():
            kwargs[metadata_name] = metadata.get_metadata_value()
        self.cicada_metadata_container.run_analysis(**kwargs)


class MetaData:

    def __init__(self, idx_position, **kwargs):
        """

        Args:
            **kwargs:
                - metadata_name
                - value_type
                - value
                - description
        """
        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)

        self.position_in_widget = idx_position

        self.final_value = None

    def set_metadata_value(self, value):
        self.final_value = value


class MetaDataGroup:  # In case of Qtable

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:
                - group_name
                - widget_type
                - description
                - metadata_in_group
        """

        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)

        self.widget = None
        self.metadata_dict = dict()
        self.idx_position = 0  # Counter, add 1 each time a metadata is add to the group to define its position inside

    # Convert metadata from CicadaMetadataContainer in MetaData class and add it to metadata_dict
    def add_metadata(self, **kwargs):
        metadata = MetaData(self.idx_position, **kwargs)
        self.metadata_dict[metadata.metadata_name] = metadata
        self.idx_position += 1

    # TODO : Try to add a QTable to see if it works !
    def get_gui_widget(self, metadata_group):
        # Get widget depending of the widget_type
        # In case of QTable, should construct a QTable with size corresponding to metadata_group size
        pass

    def put_metadata_in_widget(self, metadata):
        pass

    def get_metadata_value(self, metadata):
        if self.widget is None:
            return None
        if not metadata.position_in_widget:
            return self.widget.get_value()
        else:
            pass
            # SEE WHAT TO DO HERE !!!


class MetaDataWidget(QWidget):

    def __init__(self, data_file, parent=None):
        QWidget.__init__(self, parent=parent)

        self.data_file = data_file
        self.cicada_metadata_container = None
        self.metadata_handler = None

        self.special_background_on = False
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"

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

        self.save_button = QPushButton("Done", self)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_changes)
        self.main_layout.addWidget(self.save_button)

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
        self.save_button.setEnabled(False)

    def create_widgets(self, cicada_metadata_container):

        self.cicada_metadata_container = cicada_metadata_container

        # clearing the widget to update it
        self.tabula_rasa()
        # ==============================

        self.metadata_handler = self.cicada_metadata_container.metadata_handler

        # list of instances of MetadataArgument
        gui_widgets = self.metadata_handler.get_gui_widgets()

        for gui_widget in gui_widgets:
            # print(f"gui_widget {gui_widget}")
            self.layout.addWidget(gui_widget)
            # See to check if gui_widget is an instance of QFrame to round the border only
            # for QFrame instances
            gui_widget.setStyleSheet(
                "background-color:transparent; border-radius: 20px;")

        self.layout.addStretch(1)
        self.save_button.setEnabled(True)

    def keyPressEvent(self, event):
        available_background = ["michou_BG.jpg", "michou_BG2.jp"]
        if event.key() == QtCore.Qt.Key_A:
            if self.special_background_on:
                self.current_style_sheet_background = \
                    ".QWidget{background-image:url(\"\"); background-position: center;}"
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

    def save_changes(self):
        if self.metadata_handler is None:
            return

        self.metadata_handler.save_changes()


'''
class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def setData(self):
        horHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
'''
'''
def main(args):
    app = QApplication(args)
    table = TableView(data, 4, 3)
    table.show()
    sys.exit(app.exec_())
'''


if __name__ == "__main__":
    # main(sys.argv)
    io = NWBHDF5IO('F:/nwb_files/p6_18_02_07_a002.nwb', 'r')
    nwb_file = io.read()
    all_metadata = MetaDataFinder(nwb_file).get_all_metadata_in_nwb()
    for metadata, value in all_metadata.items():
        print(metadata + '\n')
    for metadata, value in all_metadata.items():
        print(metadata + ' : ' + str(value) + '\n')
    #MetaDataFinder(nwb_file).test_data_got_in_nwb()