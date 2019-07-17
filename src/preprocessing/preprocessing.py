import hdf5storage
import datetime
from dateutil.tz import tzlocal

import numpy as np

import yaml
import os

from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device


class Preprocessing(object):

    def add_required_metadata(self,data,key):
        print("Missing required metadata : " + key + "\n")
        metadata_value = input("Type the value (with respect of the type) : ")
        data[key] = metadata_value
        return data

    def add_optional_metadata(self,data):
        keyboard_input = False
        while not keyboard_input:
            metadata_key = input("Type the name of the metadata you want to add ? ")
            metadata_key.lower().replace("","_")
            metadata_value = input("Type the value (with respect of the type) : ")
            data[metadata_key] = metadata_value
            go = input("Continue ? (yes/no)")
            if go.lower() == "no":
                keyboard_input = True
        return data

    def metadata_acquisition(self):
        required_metadata = ["session_description", "identifier", "session_start_time", "device",
                              "optical_channel_name", "optical_channel_description", "emission_lambda",
                              "image_plane_name", "image_plane_description", "excitation_lambda",
                              "imaging_rate", "indicator", "image_plane_location","timeseries_name",
                              "image_segmentation_description","roiresponseseries_name","processing_module_name",
                              "processing_module_description",]
        if os.path.isfile("data.yaml"):
            with open("data.yaml", 'r') as stream:
                data = yaml.safe_load(stream)
            metadata_to_add = list(set(required_metadata) - set(list(data.keys())))
            for i in metadata_to_add:
                data = self.add_required_metadata(data, i)

        elif os.path.isfile("data.yml"):
            with open("data.yml", 'r') as stream:
                data = yaml.safe_load(stream)
            metadata_to_add = list(set(required_metadata) - set(list(data.keys())))
            for i in metadata_to_add:
                data = self.add_required_metadata(data, i)
        else:
            data=dict()
            for i in required_metadata:
                data = self.add_required_metadata(data, i)
        print("Found metadata : " + str(list(data.keys())))
        add_metadata = input("Do you want to add more metadata ? (yes/no) ")
        if add_metadata.lower() == "yes":
            data = self.add_optional_metadata(data)
        with open('data.yaml', 'w+') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
        print(data.get("session_start_time"))

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
                               virus=data.get("virus"), stimulus_notes=data.get("stimulus_notes"), lab=data.get("lab"))
        device = Device(name=data.get("device"))
        self.nwbfile.add_device(device)
        optical_channel = OpticalChannel(name=data.get("optical_channel_name"),
                                         description=data.get("optical_channel_description"),
                                         emission_lambda=float(data.get("emission_lambda")))
        self.mod = self.nwbfile.create_processing_module(name=data.get("processing_module_name"),
                                                         description=data.get("processing_module_description"))
        img_seg = ImageSegmentation()
        self.mod.add_data_interface(img_seg)
        imaging_plane = self.nwbfile.create_imaging_plane(name=data.get("image_plane_name"),
                                                          optical_channel=optical_channel,
                                                          description=data.get("image_plane_description"),
                                                          device=device,
                                                          excitation_lambda=float(data.get("excitation_lambda")),
                                                          imaging_rate=float(data.get("imaging_rate")),
                                                          indicator=data.get("indicator"),
                                                          location=data.get("image_plane_location"),
                                                          manifold=data.get("manifold"),
                                                          conversion=data.get("image_plane_conversion"),
                                                          unit=data.get("image_plane_unit"),
                                                          reference_frame=data.get("image_plane_reference_frame"))

if __name__ == '__main__':
    new = Preprocessing()
    Preprocessing.metadata_acquisition(new)