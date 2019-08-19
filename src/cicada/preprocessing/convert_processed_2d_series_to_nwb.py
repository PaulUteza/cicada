from cicada.preprocessing.convert_to_nwb import ConvertToNWB
import yaml
import numpy as np
import hdf5storage
from pynwb.base import TimeSeries

# TODO: Use to be ConvertRasterplotToNWB make it more modulable.
#  could take any 2d array time series that fit the calcium imaging movie such as onsets, peaks, raster_dur
#  raster_dur could be loaded through a npz, npy or .mat file. It could also be predictions
#  then a threshold should be passed as argument. And for predicitons file, a keyword determining the network used to
#  train it should be passed

"""
use to be in the pre_processing_default.yaml
ConvertRasterplotToNWB :
  rasterdur_file_name :
    keyword: ["Raster"]
    keyword_to_exclude: ["._"]
    extension: ["mat"]
    value: ["corrected_rasterdur"]
  yaml_file_name:
    keyword: ["data"]
    keyword_to_exclude: ["default"]
    extension: ["yaml"]
    value: []
"""

class ConvertProcessed2dSeriesToNWB(ConvertToNWB):
    """Class to convert 2D series to NWB """
    def __init__(self, nwb_file):
        super().__init__(nwb_file)

    @staticmethod
    def load_rasterplot_in_memory(rasterplot_file_name, matlab_string, frames_to_add=None):
        """
        Get 2D series data from file

        Args:
            rasterplot_file_name (str) : Absolute path to file containing 2D series
            matlab_string (str) : Key to the data from matlab and npz files
            frames_to_add (dict) : Key is the frame where you add blank frames and value is the number of frames to add
            Default is None.

        Returns:
            raster (np.array) : Raster data as a 2d array
        """
        if rasterplot_file_name is not None:
            print(f"Loading Rasterplot")
            raster_data = hdf5storage.loadmat(rasterplot_file_name)
            raster = raster_data[matlab_string]
            nb_cells, nb_frames = np.array(raster).shape

            if frames_to_add is not None:
                nb_frames += np.sum(list(frames_to_add.values()))
                print(f"nb_cells {nb_cells}, nb_frames {nb_frames}")

                raster_modified = np.zeros((nb_cells, nb_frames), dtype="uint16")
                frame_index = 0
                for frame in range(nb_frames):
                    # adding blank frames
                    if frame in frames_to_add:
                        frame_index += frames_to_add[frame]
                    frame_index += 1
                return raster_modified
            else:
                print(f"nb_cells {nb_cells}, nb_frames {nb_frames}")

                return raster

    def convert(self, **kwargs):
        """Convert the data and add to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """
        super().convert(**kwargs)

        if "rasterdur_file_name" not in kwargs or not kwargs["rasterdur_file_name"]:
            raise Exception(f"'rasterdur_file_name' argument should be passed to convert "
                            f"function in class {self.__class__.__name__}")

        if type(kwargs["rasterdur_file_name"]) == str and kwargs["rasterdur_file_name"].endswith(".mat"):
            raise Exception(f"'{utils.path_leaf(kwargs['rasterdur_file_name'])}' is a matlab file "
                            f"but no key to access data was provided for function in class {self.__class__.__name__}")

        rasterdur_file_name = kwargs["rasterdur_file_name"][0]
        matlab_string = kwargs["rasterdur_file_name"][1]

        # Create or get the processing module 'ophys'
        try:
            mod = self.nwb_file.get_processing_module("ophys")
        except:
            mod = self.nwb_file.create_processing_module('ophys', 'contains optical physiology processed data')

        # Open YAML file with metadata if existing then dump all data in a dict
        if ("yaml_file_name" in kwargs) and kwargs["yaml_file_name"] is not None:
            with open(kwargs["yaml_file_name"], 'r') as stream:
                yaml_data = yaml.safe_load(stream)
        else:
            raise Exception(f"'yaml_file_name' attribute should be passed to convert "
                            f"function in class {self.__class__.__name__}")

        if "frames_to_add" in yaml_data:
            """
            # exemple, give a frame number and how many frames to add after this one
            # frames added will be blank frames, filled of zeros
            # this is possible so far only if format is not "external
            frames_to_add:
                2499: 50
                4999: 36
            """
            frames_to_add = yaml_data["frames_to_add"]
        else:
            frames_to_add = None

        # Add rasterplot in the NWB file

        raster_data = self.load_rasterplot_in_memory(rasterdur_file_name, matlab_string, frames_to_add=frames_to_add)
        nb_cells, nb_frames = raster_data.shape

        rasterplot = TimeSeries(name='Rasterplot', data=raster_data, timestamps=np.arange(nb_frames),
                                description='rasterplot')

        mod.add_data_interface(rasterplot)