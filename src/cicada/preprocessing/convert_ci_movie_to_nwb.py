from cicada.preprocessing.convert_to_nwb import ConvertToNWB
from PIL import ImageSequence
from ScanImageTiffReader import ScanImageTiffReader
import PIL
import PIL.Image as pil_image
import time
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, CorrectedImageStack
import yaml
import numpy as np
import os
import hdf5storage
from pynwb.base import TimeSeries
from pynwb.device import Device

class ConvertCiMovieToNWB(ConvertToNWB):
    """Class to convert Calcium Imaging movies to NWB"""
    def __init__(self, nwb_file):
        """
        Initialize some parameters
        Args:
             nwb_file (NWB.File) : NWB file object
        """
        super().__init__(nwb_file)
        self.ci_sampling_rate = None
        # dict with key an int representing the frame index after which add frames.
        # the value is the number of frames to add (integer)
        self.frames_to_add = dict()


    def load_tiff_movie_in_memory_using_pil(self, tif_movie_file_name):
        """
            Load tiff movie from filename using PIL library

            Args:
                tif_movie_file_name (str) : Absolute path to tiff movie

            Returns:
                tiff_movie (array) : Tiff movie as 3D-array
        """
        start_time_timer = time.time()
        im = pil_image.open(tif_movie_file_name)
        n_frames = len(list(ImageSequence.Iterator(im)))
        dim_y, dim_x = np.array(im).shape
        print(f"n_frames {n_frames}, dim_x {dim_x}, dim_y {dim_y}")

        if len(self.frames_to_add) > 0:
            n_frames += np.sum(list(self.frames_to_add.values()))
        tiff_movie = np.zeros((n_frames, dim_y, dim_x), dtype="uint16")
        frame_index = 0
        for frame, page in enumerate(ImageSequence.Iterator(im)):
            tiff_movie[frame_index] = np.array(page)
            frame_index += 1
            # adding blank frames
            if frame in self.frames_to_add:
                frame_index += self.frames_to_add[frame]
        stop_time_timer = time.time()
        print(f"Time for loading movie: "
              f"{np.round(stop_time_timer - start_time_timer, 3)} s")
        return tiff_movie

    def load_tiff_movie_in_memory(self, tif_movie_file_name):
        """
            Load tiff movie from filename using Scan Image Tiff

            Args:
                tif_movie_file_name (str) : Absolute path to tiff movie

            Returns:
                tiff_movie (array) : Tiff movie as 3D-array
        """
        if tif_movie_file_name is not None:
            print(f"Loading movie")
            try:
                if 'ci_recording_on_pause' in self.nwb_file.intervals:
                    return self.load_tiff_movie_in_memory_using_pil(tif_movie_file_name)
            except AttributeError:
                try:
                    start_time = time.time()
                    tiff_movie = ScanImageTiffReader(tif_movie_file_name).data()
                    stop_time = time.time()
                    print(f"Time for loading movie with scan_image_tiff: "
                          f"{np.round(stop_time - start_time, 3)} s")
                except Exception as e:
                    return self.load_tiff_movie_in_memory_using_pil(tif_movie_file_name)

            return tiff_movie

    def convert(self, **kwargs):
        """Convert the data and add to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """
        super().convert(**kwargs)

        # ### setting parameters ####
        formats_implemented = ["external", "tiff"]
        if not kwargs.get("format"):
            raise Exception(f"'format' argument should be pass to convert function in class {self.__class__.__name__}")
        elif kwargs["format"] not in formats_implemented:
            raise Exception(f"'format' argument should have one of these values {formats_implemented} "
                            f"for the convert function in class {self.__class__.__name__}")
        movie_format = kwargs["format"]

        if not kwargs.get("motion_corrected_file_name"):
            raise Exception(f"'motion_corrected_file_name' attribute should be pass to convert "
                            f"function in class {self.__class__.__name__}")
        motion_corrected_file_name = kwargs["motion_corrected_file_name"]

        if "original_movie_file_name" in kwargs:
            original_movie_file_name = kwargs["original_movie_file_name"]
        else:
            original_movie_file_name = None

        if "xy_translation_file_name" in kwargs:
            xy_translation_file_name = kwargs["xy_translation_file_name"]
        else:
            xy_translation_file_name = None

        # Open YAML file with metadata if existing then dump all data in a dict
        if ("yaml_file_name" in kwargs) and kwargs["yaml_file_name"] is not None:
            with open(kwargs["yaml_file_name"], 'r') as stream:
                yaml_data = yaml.safe_load(stream)
        else:
            raise Exception(f"'yaml_file_name' attribute should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        # a calcium imaging rate has to be given, either trought the yaml file, either as argument
        # self.ci_sampling_rate can be obtained by the abf_converter
        if "imaging_rate" in yaml_data:
            self.ci_sampling_rate = yaml_data["imaging_rate"]
        elif "ci_sampling_rate" in kwargs:
            self.ci_sampling_rate = kwargs["ci_sampling_rate"]
        else:
            raise Exception(f"No 'imaging_rate' provided for movie {motion_corrected_file_name} in the yaml file "
                            f"{kwargs['yaml_file_name']} or throught argument 'ci_sampling_rate' to function convert() "
                            f"of the class {self.__class__.__name__}")

        if "indicator" in yaml_data:
            indicator = yaml_data["indicator"]
        else:
            raise Exception(f"No 'indicator' provided for movie {motion_corrected_file_name} in the yaml file "
                            f"{kwargs['yaml_file_name']}")

        if "excitation_lambda" in yaml_data:
            excitation_lambda = yaml_data["excitation_lambda"]
        else:
            raise Exception(f"No 'excitation_lambda' provided for movie {motion_corrected_file_name} in the yaml file "
                            f"{kwargs['yaml_file_name']}")

        if "emission_lambda" in yaml_data:
            emission_lambda = yaml_data["emission_lambda"]
        else:
            raise Exception(f"No 'emission_lambda' provided for movie {motion_corrected_file_name} in the yaml file "
                            f"{kwargs['yaml_file_name']}")

        if "image_plane_location" in yaml_data:
            image_plane_location = yaml_data["image_plane_location"]
        else:
            raise Exception(
                f"No 'image_plane_location' provided for movie {motion_corrected_file_name} in the yaml file "
                f"{kwargs['yaml_file_name']}")
        try :
            if 'ci_recording_on_pause' in self.nwb_file.intervals:
                pause_intervals = self.nwb_file.intervals['ci_recording_on_pause']
                pause_intervals_df = pause_intervals.to_dataframe()
                start_times = pause_intervals_df.loc[:, "start_time"]
                stop_times = pause_intervals_df.loc[:, "stop_time"]

                try:
                    ci_frames_time_series = self.nwb_file.get_acquisition("ci_frames")
                    ci_frames = np.where(ci_frames_time_series.data)[0]
                    ci_frames_timestamps = ci_frames_time_series.timestamps[ci_frames]
                    for i, start_time in enumerate(start_times):
                        frame_index = np.searchsorted(a=ci_frames_timestamps, v=start_time)
                        n_frames_to_add = (stop_times[i] - start_time) * self.ci_sampling_rate
                        self.frames_to_add[frame_index] = int(n_frames_to_add)
                except KeyError:
                    pass
        except AttributeError:
            pass
        # ### end setting parameters ####

        device = Device('2P_device')
        self.nwb_file.add_device(device)
        optical_channel = OpticalChannel('my_optchan', 'description', emission_lambda)

        imaging_plane = self.nwb_file.create_imaging_plane(name='my_imgpln',
                                                           optical_channel=optical_channel,
                                                           description='a very interesting part of the brain',
                                                           device=device,
                                                           excitation_lambda=excitation_lambda,
                                                           imaging_rate=float(self.ci_sampling_rate),
                                                           indicator=indicator,
                                                           location=image_plane_location)

        if movie_format != "external":
            tiff_movie = self.load_tiff_movie_in_memory(motion_corrected_file_name)
            dim_y, dim_x = tiff_movie.shape[1:]
            n_frames = tiff_movie.shape[0]
            motion_corrected_img_series = TwoPhotonSeries(name='motion_corrected_ci_movie', dimension=[dim_x, dim_y],
                                                          data=tiff_movie,
                                                          imaging_plane=imaging_plane,
                                                          starting_frame=[0], format=movie_format,
                                                          rate=self.ci_sampling_rate)
            if original_movie_file_name is not None:
                original_tiff_movie = self.load_tiff_movie_in_memory(original_movie_file_name)
                dim_y, dim_x = original_tiff_movie.shape[1:]
                original_img_series = TwoPhotonSeries(name='original_ci_movie', dimension=[dim_x, dim_y],
                                                      data=original_tiff_movie,
                                                      imaging_plane=imaging_plane,
                                                      starting_frame=[0], format=movie_format,
                                                      rate=float(self.ci_sampling_rate))
        else:
            im = PIL.Image.open(motion_corrected_file_name)
            n_frames = len(list(ImageSequence.Iterator(im)))
            dim_y, dim_x = np.array(im).shape
            motion_corrected_img_series = TwoPhotonSeries(name='motion_corrected_ci_movie', dimension=[dim_x, dim_y],
                                                          external_file=[motion_corrected_file_name],
                                                          imaging_plane=imaging_plane,
                                                          starting_frame=[0], format=movie_format,
                                                          rate=float(self.ci_sampling_rate))
            if original_movie_file_name is not None:
                im = PIL.Image.open(original_movie_file_name)
                dim_y, dim_x = np.array(im).shape
                original_img_series = TwoPhotonSeries(name='original_ci_movie',
                                                      dimension=[dim_x, dim_y],
                                                      external_file=[original_movie_file_name],
                                                      imaging_plane=imaging_plane,
                                                      starting_frame=[0], format=movie_format,
                                                      rate=float(self.ci_sampling_rate))

        self.nwb_file.add_acquisition(motion_corrected_img_series)
        if original_movie_file_name is not None:
            self.nwb_file.add_acquisition(original_img_series)

        if xy_translation_file_name is not None:
            if xy_translation_file_name.endswith(".mat"):
                mvt_x_y = hdf5storage.loadmat(os.path.join(xy_translation_file_name))
                x_shifts = mvt_x_y['xshifts'][0]
                y_shifts = mvt_x_y['yshifts'][0]
            elif xy_translation_file_name.endswith(".npy"):
                ops = np.load(os.path.join(xy_translation_file_name))
                ops = ops.item()
                x_shifts = ops['xoff']
                y_shifts = ops['yoff']
            xy_translation = np.zeros((n_frames, 2), dtype="int16")
            frame_index = 0
            for frame in np.arange(len(x_shifts)):
                xy_translation[frame_index, 0] = x_shifts[frame]
                xy_translation[frame_index, 1] = y_shifts[frame]
                # adding frames is necessary, in case the movie would be a concatenation of movie for exemple
                if frame in self.frames_to_add:
                    frame_index += self.frames_to_add[frame]
            xy_translation_time_series = TimeSeries(name="xy_translation", data=xy_translation)
            corrected_image_stack = CorrectedImageStack(name="CorrectedImageStack",
                                                        corrected=motion_corrected_img_series,
                                                        original=original_img_series,
                                                        xy_translation=xy_translation_time_series)

            self.nwb_file.add_acquisition(corrected_image_stack)
