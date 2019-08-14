from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
from qtpy.QtGui import *
import numpy as np
from qtpy import QtCore
from random import randint
import sys
import os
from abc import ABC, abstractmethod
from pynwb import NWBHDF5IO, get_manager, NWBContainer
from datetime import datetime
from pynwb.core import LabelledDict
from pynwb.file import NWBFile, Subject
import hdmf
from shutil import copyfile


class MetaDataFinder:

    def __init__(self, data_path):
        self.data_path = data_path
        self.data_file = self.get_data_file()
        self.metadata_from_data_file = self.get_general_metadata_in_nwb()
        self.subject_metadata_from_data_file = self.get_subject_metadata_in_nwb(self.metadata_from_data_file['subject'])
        self.containers_from_data_file = self.get_containers_in_nwb()

    def get_data_file(self):
        io_read = NWBHDF5IO(self.data_path, 'r')
        data_file_to_get = io_read.read()
        io_read.close()
        return data_file_to_get

    def get_metadata(self, name):
        return self.metadata_from_data_file[name]

    def get_subject_metadata(self, name):
        return self.subject_metadata_from_data_file[name]

    def get_general_metadata_in_nwb(self):
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

    def get_containers_in_nwb(self):

        containers_from_data_file = dict()

        for field in self.data_file.fields:
            field_class = self.data_file.fields.get(field)
            if isinstance(field_class, LabelledDict):
                for sub_field in field_class:
                    sub_field_class = field_class.get(sub_field)
                    print(type(sub_field_class))
                    if isinstance(sub_field_class, NWBContainer):
                        containers_from_data_file[sub_field_class.name] = sub_field_class
                        print(sub_field_class.name)

        return containers_from_data_file

    @staticmethod
    def get_subject_metadata_in_nwb(subject):
        subject_metadata_from_data_file = {
            "age": getattr(subject, "age"),
            "description": getattr(subject, "description"),
            "genotype": getattr(subject, "genotype"),
            "sex": getattr(subject, "sex"),
            "species": getattr(subject, "species"),
            "subject_id": getattr(subject, "subject_id"),
            "weight": getattr(subject, "weight"),
            "date_of_birth": getattr(subject, "date_of_birth")}

        return subject_metadata_from_data_file


class CicadaMetaDataContainer:

    def __init__(self, data_path, data_format):

        self.data_path = data_path

        self.metadata_finder_wrapper = None
        self.initiate_metadata_finder_wrapper(data_format=data_format)

        self.data_file = self.metadata_finder_wrapper.data_file

        self.metadata_handler = MetaDataHandler(cicada_metadata_container=self)

        self.set_metadata_for_gui()
        self.set_containers_for_gui()

    def initiate_metadata_finder_wrapper(self, data_format):
        if data_format == "nwb":
            self.metadata_finder_wrapper = MetaDataFinder(self.data_path)

    def add_metadata_group_for_gui(self, **kwargs):

        self.metadata_handler.add_group(**kwargs)

    def set_metadata_for_gui(self):

        # All metadata with names, value_types, value and description !

        acquisition_metadata = {"metadata_name": "acquisition", "value_type": "dictionnary",
                                "value": self.metadata_finder_wrapper.get_metadata("acquisition"),
                                "description": "Raw TimeSeries objects belonging to this NWBFile"}

        analysis_metadata = {"metadata_name": "analysis", "value_type": "dictionnary",
                             "value": self.metadata_finder_wrapper.get_metadata("analysis"),
                             "description": "Result of analysis"}

        container_source_metadata = {"metadata_name": "container_source", "value_type": "str",
                                     "value": self.metadata_finder_wrapper.get_metadata("container_source"),
                                     "description": "Path to the container source"}

        data_collection_metadata = {"metadata_name": "data_collection", "value_type": "str",
                                    "value": self.metadata_finder_wrapper.get_metadata("data_collection"),
                                    "description": "Notes about data collection and analysis"}

        devices_metadata = {"metadata_name": "devices", "value_type": "dictionnary",
                            "value": self.metadata_finder_wrapper.get_metadata("devices"),
                            "description": "Device objects belonging to this NWBFile"}

        electrode_groups_metadata = {"metadata_name": "electrode_groups", "value_type": "dictionnary",
                                     "value": self.metadata_finder_wrapper.get_metadata("electrode_groups"),
                                     "description": "A dictionary containing the ElectrodeGroup in this"
                                                    " NWBFile container"}

        electrodes_metadata = {"metadata_name": "electrodes", "value_type": "dictionnary",
                               "value": self.metadata_finder_wrapper.get_metadata("electrodes"),
                               "description": "The ElectrodeTable that belongs to this NWBFile"}

        epoch_tags_metadata = {"metadata_name": "epoch_tags", "value_type": "set",
                               "value": self.metadata_finder_wrapper.get_metadata("epoch_tags"),
                               "description": "A sorted list of tags used across all epochs"}

        epochs_metadata = {"metadata_name": "epochs", "value_type": "dictionnary",
                           "value": self.metadata_finder_wrapper.get_metadata("epochs"),
                           "description": "Epoch objects belonging to this NWBFile"}

        experiment_description_metadata = {"metadata_name": "experiment_description", "value_type": "str",
                                           "value": self.metadata_finder_wrapper.get_metadata("experiment_description"),
                                           "description": "General description of the experiment"}

        experimenter_metadata = {"metadata_name": "experimenter", "value_type": "str",
                                 "value": self.metadata_finder_wrapper.get_metadata("experimenter"),
                                 "description": "Name of person who performed experiment"}

        file_create_date_metadata = {"metadata_name": "file_create_date", "value_type": "datetime",
                                     "value": self.metadata_finder_wrapper.get_metadata("file_create_date"),
                                     "description": "The date and time the file was created and subsequent"
                                                    " modifications made"}

        ic_electrodes_metadata = {"metadata_name": "ic_electrodes", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("ic_electrodes"),
                                  "description": "A dictionary containing the IntracellularElectrode in this"
                                                 " NWBFile container"}

        identifier_metadata = {"metadata_name": "identifier", "value_type": "str",
                               "value": self.metadata_finder_wrapper.get_metadata("identifier"),
                               "description": "A unique text identifier for the file"}

        imaging_planes_metadata = {"metadata_name": "imaging_planes", "value_type": "dictionnary",
                                   "value": self.metadata_finder_wrapper.get_metadata("imaging_planes"),
                                   "description": "A dictionary containing the ImagingPlane in this NWBFile container"}

        institution_metadata = {"metadata_name": "institution", "value_type": "str",
                                "value": self.metadata_finder_wrapper.get_metadata("institution"),
                                "description": "Institution(s) where experiment is performed"}

        invalid_times_metadata = {"metadata_name": "invalid_times", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("invalid_times"),
                                  "description": "A table containing times to be omitted from analysis"}

        keywords_metadata = {"metadata_name": "keywords", "value_type": "list",
                             "value": self.metadata_finder_wrapper.get_metadata("keywords"),
                             "description": "Terms to search over"}

        lab_metadata = {"metadata_name": "lab", "value_type": "str",
                        "value": self.metadata_finder_wrapper.get_metadata("lab"),
                        "description": "Lab where experiment was performed"}

        lab_meta_data_metadata = {"metadata_name": "lab_meta_data", "value_type": "dictionnary",
                                  "value": self.metadata_finder_wrapper.get_metadata("lab_meta_data"),
                                  "description": "An extension that contains lab-specific meta-data"}

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
                                                " administered.\nAnesthesia(s), painkiller(s), etc., plus dosage,"
                                                " concentration, etc."}

        protocol_metadata = {"metadata_name": "protocol", "value_type": "str",
                             "value": self.metadata_finder_wrapper.get_metadata("protocol"),
                             "description": "Experimental protocol, if applicable. E.g., include IACUC protocol"}

        related_publications_metadata = {"metadata_name": "related_publications", "value_type": "str",
                                         "value": self.metadata_finder_wrapper.get_metadata("related_publications"),
                                         "description": "Publication information.PMID, DOI, URL, etc. If multiple,\n"
                                                        "concatenate together and describe which is which. such as"
                                                        " PMID, DOI, URL, etc"}

        session_description_metadata = {"metadata_name": "session_description", "value_type": "str",
                                        "value": self.metadata_finder_wrapper.get_metadata("session_description"),
                                        "description": "A description of the session where this data was generated"}

        session_id_metadata = {"metadata_name": "session_id", "value_type": "str",
                               "value": self.metadata_finder_wrapper.get_metadata("session_id"),
                               "description": "Lab-specific ID for the session"}

        session_start_time_metadata = {"metadata_name": "session_start_time", "value_type": "datetime",
                                       "value": self.metadata_finder_wrapper.get_metadata("session_start_time"),
                                       "description": "The start date and time of the recording session"}

        slices_metadata = {"metadata_name": "slices", "value_type": "str",
                           "value": self.metadata_finder_wrapper.get_metadata("slices"),
                           "description": "Description of slices, including information about preparation\n"
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
                            "description": "Subject metadata"}

        surgery_metadata = {"metadata_name": "surgery", "value_type": "str",
                            "value": self.metadata_finder_wrapper.get_metadata("surgery"),
                            "description": "Narrative description about surgery/surgeries,\n"
                                           "including date(s) and who performed surgery"}

        sweep_table_metadata = {"metadata_name": "sweep_table", "value_type": "class",
                                "value": self.metadata_finder_wrapper.get_metadata("sweep_table"),
                                "description": "The SweepTable that belong to this NWBFile"}

        timestamps_reference_time_metadata = {"metadata_name": "timestamps_reference_time", "value_type": "datetime",
                                              "value": self.metadata_finder_wrapper.get_metadata(
                                                  "timestamps_reference_time"),
                                              "description": "Date and time corresponding to time zero of all "
                                                             "timestamps;\ndefaults to value of session_start_time"}

        trials_metadata = {"metadata_name": "trials", "value_type": "class",
                           "value": self.metadata_finder_wrapper.get_metadata("trials"),
                           "description": "A table containing trial data"}

        units_metadata = {"metadata_name": "units", "value_type": "class",
                          "value": self.metadata_finder_wrapper.get_metadata("units"),
                          "description": "A table containing unit metadata"}

        virus_metadata = {"metadata_name": "virus", "value_type": "str",
                          "value": self.metadata_finder_wrapper.get_metadata("virus"),
                          "description": "Information about virus(es) used in experiments, including virus ID,\n"
                                         "source, date made, injection location, volume, etc."}

        # Subject part :

        age_subject_metadata = {"metadata_name": "age", "value_type": "str",
                                "value": self.metadata_finder_wrapper.get_subject_metadata("age"),
                                "description": "The age of the subject"}

        description_subject_metadata = {"metadata_name": "description", "value_type": "str",
                                        "value": self.metadata_finder_wrapper.get_subject_metadata("description"),
                                        "description": "A description of the subject"}

        genotype_subject_metadata = {"metadata_name": "genotype", "value_type": "str",
                                     "value": self.metadata_finder_wrapper.get_subject_metadata("genotype"),
                                     "description": "The genotype of the subject"}

        sex_subject_metadata = {"metadata_name": "sex", "value_type": "str",
                                "value": self.metadata_finder_wrapper.get_subject_metadata("sex"),
                                "description": "The sex of the subject"}

        species_subject_metadata = {"metadata_name": "species", "value_type": "str",
                                    "value": self.metadata_finder_wrapper.get_subject_metadata("species"),
                                    "description": "The species of the subject"}

        subject_id_subject_metadata = {"metadata_name": "subject_id", "value_type": "str",
                                       "value": self.metadata_finder_wrapper.get_subject_metadata("subject_id"),
                                       "description": "A unique identifier for the subject"}

        weight_subject_metadata = {"metadata_name": "weight", "value_type": "str",
                                   "value": self.metadata_finder_wrapper.get_subject_metadata("weight"),
                                   "description": "The weight of the subject"}

        date_of_birth_subject_metadata = {"metadata_name": "date_of_birth", "value_type": "datetime",
                                          "value": self.metadata_finder_wrapper.get_subject_metadata("date_of_birth"),
                                          "description": "Datetime of date of birth.\nMay be supplied instead of age"}

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

        metadata_from_subject = dict()
        metadata_from_subject["group_name"] = 'metadata_from_subject'
        metadata_from_subject["widget_type"] = 'QTable'
        metadata_from_subject["description"] = 'metadata about the subject'
        metadata_from_subject["metadata_in_group"] = [age_subject_metadata,
                                                      description_subject_metadata,
                                                      genotype_subject_metadata,
                                                      sex_subject_metadata,
                                                      species_subject_metadata,
                                                      subject_id_subject_metadata,
                                                      weight_subject_metadata,
                                                      date_of_birth_subject_metadata]

        self.add_metadata_group_for_gui(**metadata_from_subject)

        # TODO : for each of those following metadata, find a way to show them
        other_metadata = dict()
        other_metadata["group_name"] = 'other_metadata'
        other_metadata["widget_type"] = 'QTable'
        other_metadata["description"] = 'metadata which are not affiliated to a group'
        other_metadata["metadata_in_group"] = [keywords_metadata,
                                               epochs_metadata,
                                               trials_metadata,
                                               invalid_times_metadata,
                                               units_metadata,
                                               electrodes_metadata,
                                               sweep_table_metadata,
                                               neurodata_type_metadata,
                                               modified_metadata,
                                               container_source_metadata]

    def set_containers_for_gui(self):

        containers_from_data_file = self.metadata_finder_wrapper.containers_from_data_file

        container_metadata = dict()
        container_metadata["group_name"] = 'containers'
        container_metadata["widget_type"] = 'QTable'
        container_metadata["description"] = 'all containers with data (value indicates if the container contains data)'
        container_metadata["metadata_in_group"] = []

        for container in containers_from_data_file.values():
            container_dict = {'metadata_name': container.name, 'value_type': container.neurodata_type,
                              'value': getattr(container, 'data', None) is not None,
                              'description': getattr(container, 'description', None)}
            container_metadata["metadata_in_group"].append(container_dict)

        self.add_metadata_group_for_gui(**container_metadata)

    def save_changes(self, general_metadata, subject_metadata):
        # TODO : wrapper for save : only in NWB for the moment

        # SaveModifiedNWB(self.data_path, general_metadata=general_metadata, subject_metadata=subject_metadata)
        pass


class SaveModifiedNWB:
    # IT DOESN'T WORK !!!
    # TODO: make it work

    # I tried to open the initial NWB_file, add to it all metadata completed by the user on the GUI
    # and then save the modified NWB_file in a new file. However there is a problem with all container objects like
    # acquisition : when I try to save the file, they are not found ...

    def __init__(self, nwb_path, general_metadata=None, subject_metadata=None):
        self.manager = get_manager()
        self.nwb_path = nwb_path

        # New path to save the modified NWB
        parent_dir, file_name = os.path.split(self.nwb_path)
        self.new_path = os.path.join(parent_dir, "new_" + file_name)

        self.io_read = None
        self.io_write = None
        self.nwb_file = self.get_nwb_file()
        self.general_metadata = general_metadata  # dictionnary with all general metadata fields and values
        self.subject_metadata = subject_metadata  # dictionnary with all value metadata fields and values

        self.modify_general_metadata()
        self.modify_subject_metadata()

        self.write_nwb()

    def get_nwb_file(self):
        self.io_read = NWBHDF5IO(self.nwb_path, 'r', manager=self.manager)
        nwb_file_to_get = self.io_read.read()
        return nwb_file_to_get

    def modify_general_metadata(self):
        # Add general metadata if not already exists
        for metadata_field, metadata_value in self.general_metadata.items():
            try:
                setattr(self.nwb_file, metadata_field, metadata_value)
            except AttributeError:
                print(metadata_field, " : NO ! NO ! NO !")

    def modify_subject_metadata(self):
        # Add subject metadata if not already exists
        if getattr(self.nwb_file, 'subject', None) is None:
            pass
        else:
            for metadata_field, metadata_value in self.subject_metadata.items():
                try:
                    setattr(self.nwb_file.subject, metadata_field, metadata_value)
                except AttributeError:
                    print(metadata_field, " : NO ! NO ! NO !")
                except Exception as e:
                    print(e)

    def write_nwb(self):
        # It seems that io.read need to be open to save data in file, so I try to save data in an other file
        self.io_write = NWBHDF5IO(self.new_path, 'a', manager=self.manager)
        self.io_write.write(self.nwb_file, link_data=False)
        self.io_read.close()
        self.io_write.close()


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
        general_metadata_values = dict()
        subject_metadata_values = dict()
        for metadata_group_name, metadata_group in self.groups_dict.items():
            for metadata_name, metadata in metadata_group.metadata_dict.items():
                if metadata_group_name == 'general_metadata':
                    general_metadata_values[metadata_name] = metadata_group.get_metadata_value_in_widget(metadata)
                elif metadata_group_name == 'metadata_from_subject':
                    subject_metadata_values[metadata_name] = metadata_group.get_metadata_value_in_widget(metadata)
        self.cicada_metadata_container.save_changes(general_metadata_values, subject_metadata_values)


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

    def get_metadata_value(self):
        return getattr(self, "value", None)

    def get_metadata_name(self):
        return getattr(self, "name", None)


class MetaDataGroup:  # Necessary to add multiple metadata in one widget

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

        if getattr(self, "metadata_in_group", None) is not None:
            for raw_metadata in getattr(self, "metadata_in_group", None):
                self.add_metadata(**raw_metadata)
        else:
            print("No metadata found !")

    # Convert metadata from CicadaMetadataContainer in MetaData class and add it to metadata_dict
    def add_metadata(self, **kwargs):
        metadata_to_add = MetaData(self.idx_position, **kwargs)
        self.metadata_dict[metadata_to_add.metadata_name] = metadata_to_add
        self.idx_position += 1

    def get_gui_widget(self):
        if getattr(self, "widget_type", None) == "QTable":
            self.widget = TableWidget(metadata_group=self)
            return self.widget

    def get_metadata_value_in_widget(self, metadata):
        if self.widget is None:
            return None
        if getattr(self, "widget_type", None) == "QTable":
            return self.widget.get_value(metadata.position_in_widget)
        else:
            return self.widget.get_value()

    def get_group_description(self):
        return getattr(self, "description", None)


class MetaDataWidget(QWidget):

    def __init__(self, file_path, extension, parent=None):
        QWidget.__init__(self, parent=parent)

        self.cicada_metadata_container = CicadaMetaDataContainer(file_path, extension)
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
        self.create_widgets(self.cicada_metadata_container)
        self.show()

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


class TableWidget(QFrame):
    def __init__(self, metadata_group, parent=None):
        QWidget.__init__(self, parent=parent)

        self.metadata_group = metadata_group
        self.metadata_dict = self.metadata_group.metadata_dict

        self.table = QTableWidget()

        nb_rows = len(self.metadata_dict)
        nb_columns = 4
        # TODO : set nb_columns depending of metadata struct

        self.table.setRowCount(nb_rows)
        self.table.setColumnCount(nb_columns)

        self.table.setHorizontalHeaderLabels(["metadata name", "value type", "value", "description"])

        for metadata_to_add in self.metadata_dict.values():
            print(metadata_to_add.metadata_name)
            position = metadata_to_add.position_in_widget
            self.table.setItem(position, 0, QTableWidgetItem(metadata_to_add.metadata_name))
            self.table.setItem(position, 1, QTableWidgetItem(metadata_to_add.value_type))
            self.table.setItem(position, 2, QTableWidgetItem(str(metadata_to_add.value)))
            self.table.setItem(position, 3, QTableWidgetItem(metadata_to_add.description))
            self.table.move(0, 0)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        v_box = QVBoxLayout()
        description = self.metadata_group.get_group_description()

        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            v_box.addWidget(q_label)

        h_box = QHBoxLayout()
        h_box.addWidget(self.table)
        v_box.addLayout(h_box)

        self.setLayout(v_box)

    def get_value(self, metadata_position):
        return self.table.item(metadata_position, 2).text()



# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # Change the path !
#     # ============================================
#     file_path = 'C:/Users/Public/nwb_files/p6_18_02_07_a002.nwb'
#     # ============================================
#     cicada_metadata_container = CicadaMetaDataContainer(file_path, "nwb")
#     widget = MetaDataWidget()
#     widget.create_widgets(cicada_metadata_container)
#     widget.show()
#     '''
#     all_metadata = MetaDataFinder(nwb_file).get_all_metadata_in_nwb()
#     for metadata, value in all_metadata.items():
#         print(metadata + '\n')
#     for metadata, value in all_metadata.items():
#         print(metadata + ' : ' + str(value) + '\n')
#     '''
#     sys.exit(app.exec_())
