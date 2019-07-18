# import hdf5storage
# import datetime
# from dateutil.tz import tzlocal
#
# import numpy as np

import yaml
import os

from pynwb import NWBHDF5IO
from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device
from pynwb.file import Subject


class Preprocessing(object):

    def load_yaml(self):
        # Open YAML file with metadata if existing then dump all data in a dict
        if os.path.isfile("data.yaml"):
            with open("data.yaml", 'r') as stream:
                data = yaml.safe_load(stream)
        # Same but with .yml extension
        elif os.path.isfile("data.yml"):
            with open("data.yml", 'r') as stream:
                data = yaml.safe_load(stream)
        data["subject_metadata"] = self.subject_metadata_acquisition(data.get("subject_metadata"))
        data["ophys_metadata"] = self.ophys_metadata_acquisition(data.get("ophys_metadata"))
        # Dump the dict in the YAML file to save what the user inputted for future use
        with open('data.yaml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    def add_required_metadata(self, data, key, metadata_type):
        # Prompt user to give required metadata
        # Need to be wary of the type (put " " for string and datetime.datetime(%Y, %m, %d) for datetime)
        print("Missing required " + metadata_type + " metadata : " + key + "\n")
        metadata_value = input("Type the value (with respect of the type) : ")
        data[key] = eval(metadata_value)
        return data

    def add_optional_metadata(self, data):
        # Allow user to add as much metadata as he wants with the key he wants
        # Need to refer to documentation if he wants to fill existing attributes but he can create new ones and use
        # them in his own code
        keyboard_input = False
        while not keyboard_input:
            # Prompt user to give optional metadata
            # Need to be wary of the type (put " " for string and datetime.datetime(%Y, %m, %d) for datetime)
            metadata_key = input("Type the name of the metadata you want to add ? ")
            metadata_key.lower().replace("", "_")
            metadata_value = input("Type the value (with respect of the type) : ")
            data[metadata_key] = eval(metadata_value)
            go = input("Continue ? (yes/no)")
            # Prevent errors if other input than yes/np
            while go.lower() != "no" and go.lower() != "yes":
                go = input("Continue ? (yes/no)")
            if go.lower() == "no":
                keyboard_input = True
        return data

    def ophys_metadata_acquisition(self, data):

        # TODO: Peut être faire un dictionnaire de sous-dictionnaires correspondant à chaque classe à remplir
        #         Points positifs : Plus grand lisibilité dans le YAML, gestion simple des ambiguités de nom
        #         tout en gardant la notation de NWB.
        #         Points négatifs : Plus dur à rentrer en input pour l'utilisateur (il faut lui demander à quelle classe
        #         correspond sa valeur).

        # List of the required metadata

        # TODO : maybe better implementation is possible ?

        required_metadata = ["session_description", "identifier", "session_start_time", "device",
                             "optical_channel_name", "optical_channel_description", "emission_lambda",
                             "image_plane_name", "image_plane_description", "excitation_lambda",
                             "imaging_rate", "indicator", "image_plane_location", "timeseries_name",
                             "image_segmentation_description", "roiresponseseries_name", "processing_module_name",
                             "processing_module_description", ]

        if data is None:
            data = dict()
            for i in required_metadata:
                data = self.add_required_metadata(data, i, "ophys")
        else:
            # Check if YAML file doesn't have all the required attributes and ask them the missing ones
            metadata_to_add = list(set(required_metadata) - set(list(data.keys())))
            for i in metadata_to_add:
                data = self.add_required_metadata(data, i, "ophys")

        print("Found ophys metadata : " + str(list(data.keys())))
        add_metadata = input("Do you want to add more ophys metadata ? (yes/no) ")
        # Prevent errors if other input than yes/np
        while add_metadata.lower() != "no" and add_metadata.lower() != "yes":
            add_metadata = input("Continue ? (yes/no)")
        if add_metadata.lower() == "yes":
            data = self.add_optional_metadata(data)

        # Create new NWB file with all known attributes
        self.nwbfile = NWBFile(session_description=data.get("session_description"), identifier=data.get("identifier"),
                               session_start_time=data.get("session_start_time"),
                               file_create_date=data.get("file_create_date"),
                               timestamps_reference_time=data.get("timestamps_reference_time"),
                               experimenter=data.get("experimenter"),
                               experiment_description=data.get("experiment_description"),
                               session_id=data.get("session_id"), institution=data.get("institution"),
                               keywords=data.get("keywords"), notes=data.get("notes"),
                               pharmacology=data.get("pharmacology"), protocol=data.get("protocol"),
                               related_publications=data.get("related_publications"),
                               slices=data.get("slices"), source_script=data.get("source_script"),
                               source_script_file_name=data.get("source_script_file_name"),
                               data_collection=data.get("data_collection"), surgery=data.get("surgery"),
                               virus=data.get("virus"), stimulus_notes=data.get("stimulus_notes"), lab=data.get("lab"),
                               subject=self.subject)

        device = Device(name=data.get("device"))
        self.nwbfile.add_device(device)
        optical_channel = OpticalChannel(name=data.get("optical_channel_name"),
                                         description=data.get("optical_channel_description"),
                                         emission_lambda=data.get("emission_lambda"))
        self.mod = self.nwbfile.create_processing_module(name=data.get("processing_module_name"),
                                                         description=data.get("processing_module_description"))
        img_seg = ImageSegmentation()
        self.mod.add_data_interface(img_seg)
        imaging_plane = self.nwbfile.create_imaging_plane(name=data.get("image_plane_name"),
                                                          optical_channel=optical_channel,
                                                          description=data.get("image_plane_description"),
                                                          device=device,
                                                          excitation_lambda=data.get("excitation_lambda"),
                                                          imaging_rate=data.get("imaging_rate"),
                                                          indicator=data.get("indicator"),
                                                          location=data.get("image_plane_location"),
                                                          manifold=data.get("manifold"),
                                                          conversion=data.get("image_plane_conversion"),
                                                          unit=data.get("image_plane_unit"),
                                                          reference_frame=data.get("image_plane_reference_frame"))
        image_series = TwoPhotonSeries(name='test_iS', dimension=[2],
                                       external_file=['images.tiff'], imaging_plane=imaging_plane,
                                       starting_frame=[0], format='tiff', starting_time=0.0, rate=1.0)
        self.nwbfile.add_acquisition(image_series)
        ps = img_seg.create_plane_segmentation('output from segmenting my favorite imaging plane',
                                               imaging_plane, 'my_planeseg', image_series)
        w, h = 3, 3
        pix_mask1 = [(0, 0, 1.1), (1, 1, 1.2), (2, 2, 1.3)]
        img_mask1 = [[0.0 for x in range(w)] for y in range(h)]
        img_mask1[0][0] = 1.1
        img_mask1[1][1] = 1.2
        img_mask1[2][2] = 1.3
        ps.add_roi(pixel_mask=pix_mask1, image_mask=img_mask1)

        pix_mask2 = [(0, 0, 2.1), (1, 1, 2.2)]
        img_mask2 = [[0.0 for x in range(w)] for y in range(h)]
        img_mask2[0][0] = 2.1
        img_mask2[1][1] = 2.2
        ps.add_roi(pixel_mask=pix_mask2, image_mask=img_mask2)
        return data

    def subject_metadata_acquisition(self, data):
        # Check if metadata about the subject exists and prompt the user if he wants to add some
        if data is None:
            print("No subject metadata found \n ")
            data = dict()
        elif len(data) == 0:
            print("No subject metadata found \n ")
        else:
            print("Found subject metadata : " + str(list(data.keys())))
        add_metadata = input("Do you want to add more subject metadata ? (yes/no) ")
        # Prevent errors if other input than yes/np
        while add_metadata.lower() != "no" and add_metadata.lower() != "yes":
            add_metadata = input("Continue ? (yes/no)")
        if add_metadata.lower() == "yes":
            data = self.add_optional_metadata(data)

        self.subject = Subject(age=data.get("age"), description=data.get("description"), genotype=data.get("genotype"),
                               sex=data.get("sex"), species=data.get("species"), subject_id=data.get("subject_id"),
                               weight=data.get("weight"), date_of_birth=data.get("date_of_birth"))

        return data


if __name__ == '__main__':
    new = Preprocessing()
    Preprocessing.load_yaml(new)

    with NWBHDF5IO('ophys_example.nwb', 'w') as io:
        io.write(new.nwbfile)
