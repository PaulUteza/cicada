from pynwb import NWBHDF5IO

from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
import matplotlib.pyplot as plt
import yaml
import hdf5storage
import pyabf
import math

from pynwb import NWBFile, load_namespaces
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence, CorrectedImageStack
from pynwb.device import Device
from pynwb.base import TimeSeries
from pynwb.file import Subject
import os
import time
from PIL import ImageSequence
from ScanImageTiffReader import ScanImageTiffReader
import PIL
import PIL.Image as pil_image
from pynwb import NWBHDF5IO

# start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
# create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
#
# nwbfile = NWBFile(session_description='demonstrate advanced HDF5 I/O features',
#                   identifier='NWB123',
#                   session_start_time=start_time,
#                   file_create_date=create_date)
#
#
# data = np.arange(100, 200, 10)
# timestamps = np.arange(10)
# test_ts = TimeSeries(name='test_regular_timeseries',
#                      data=data,
#                      unit='SIunit',
#                      timestamps=timestamps)
# nwbfile.add_acquisition(test_ts)
#
# io = NWBHDF5IO('advanced_io_example.nwb', 'w')
# io.write(nwbfile)
# io.close()
#
# io = NWBHDF5IO('advanced_io_example.nwb', 'r')
# nwbfile = io.read()

"""
Reusing timestamps
When working with multi-modal data, it can be convenient and efficient to store timestamps once and associate multiple data with the single timestamps instance. PyNWB enables this by letting you reuse timestamps across TimeSeries objects. To reuse a TimeSeries timestamps in a new TimeSeries, pass the existing TimeSeries as the new TimeSeries timestamps:

data = list(range(101, 201, 10))
reuse_ts = TimeSeries('reusing_timeseries', data, 'SIunit', timestamps=test_ts)
"""

"""
https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
https://stackoverflow.com/questions/51142320/how-to-instantiate-class-by-its-string-name-in-python-from-current-file
To import module using string:
https://stackoverflow.com/questions/9806963/how-to-use-pythons-import-function-properly-import
"""


class ConvertToNWB:

    def __init__(self, nwb_file):
        self.nwb_file = nwb_file

    def convert(self, **kwargs):
        """
        Convert the data and add to the nwb_file
        """
        pass


class ConvertCIMovieToNWB(ConvertToNWB):

    def __init__(self, nwb_file):
        super().__init__(nwb_file)

    @staticmethod
    def load_tiff_movie_in_memory_using_pil(tif_movie_file_name, frames_to_add=None):
        """

        :param tif_movie_file_name:
        :param frames_to_add: is a dict, with key the frame after which add blank frames
        and value being the number of frames to add
        :return:
        """
        start_time = time.time()
        im = pil_image.open(tif_movie_file_name)
        n_frames = len(list(ImageSequence.Iterator(im)))
        dim_y, dim_x = np.array(im).shape
        print(f"n_frames {n_frames}, dim_x {dim_x}, dim_y {dim_y}")
        if frames_to_add is not None:
            n_frames += np.sum(list(frames_to_add.values))
        tiff_movie = np.zeros((n_frames, dim_y, dim_x), dtype="uint16")
        frame_index = 0
        for frame, page in enumerate(ImageSequence.Iterator(im)):
            tiff_movie[frame_index] = np.array(page)
            frame_index += 1
            # adding blank frames
            if frame in frames_to_add:
                frame_index += frames_to_add[frame]
        stop_time = time.time()
        print(f"Time for loading movie: "
              f"{np.round(stop_time - start_time, 3)} s")
        return tiff_movie

    @staticmethod
    def load_tiff_movie_in_memory(tif_movie_file_name, frames_to_add=None):
        if tif_movie_file_name is not None:
            print(f"Loading movie")
            if frames_to_add is not None:
                return ConvertCIMovieToNWB.load_tiff_movie_in_memory_using_pil(tif_movie_file_name,
                                                                               frames_to_add=frames_to_add)
            else:
                try:
                    start_time = time.time()
                    tiff_movie = ScanImageTiffReader(tif_movie_file_name).data()
                    stop_time = time.time()
                    print(f"Time for loading movie with scan_image_tiff: "
                          f"{np.round(stop_time - start_time, 3)} s")
                except Exception as e:
                    return ConvertCIMovieToNWB.load_tiff_movie_in_memory_using_pil(tif_movie_file_name,
                                                                                   frames_to_add=frames_to_add)

            return tiff_movie

    def convert(self, **kwargs):
        super().convert(**kwargs)

        # ### setting parameters ####
        formats_implemented = ["external", "tiff"]
        if "format" not in kwargs:
            raise Exception(f"'format' argument should be pass to convert function in class {self.__class__.__name__}")
        elif kwargs["format"] not in formats_implemented:
            raise Exception(f"'format' argument should have one of these values {formats_implemented} "
                            f"for the convert function in class {self.__class__.__name__}")
        movie_format = kwargs["format"]

        if "motion_corrected_file_name" not in kwargs:
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

        if "imaging_rate" in yaml_data:
            imaging_rate = yaml_data["imaging_rate"]
        else:
            raise Exception(f"No 'imaging_rate' provided for movie {motion_corrected_file_name} in the yaml file "
                            f"{kwargs['yaml_file_name']}")

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
        # TODO: test the code that uses frames_to_add
        if "frames_to_add" in yaml_data:
            """
            # exemple, give a frame number and how many frames to add after this one
            # frames added will be blank frames, filled of zeros
            # this is possible so far only if format is not "external
            frames_to_add:
                2499: 50
                4999: 36 
            """
            frames_to_add = yaml_data["image_plane_location"]
        else:
            frames_to_add = None

        # ### end setting parameters ####

        device = Device('2P_device')
        self.nwb_file.add_device(device)
        optical_channel = OpticalChannel('my_optchan', 'description', emission_lambda)

        imaging_plane = self.nwb_file.create_imaging_plane(name='my_imgpln',
                                                           optical_channel=optical_channel,
                                                           description='a very interesting part of the brain',
                                                           device=device,
                                                           excitation_lambda=excitation_lambda,
                                                           imaging_rate=imaging_rate,
                                                           indicator=indicator,
                                                           location=image_plane_location)

        if movie_format != "external":
            tiff_movie = self.load_tiff_movie_in_memory(motion_corrected_file_name, frames_to_add=frames_to_add)
            dim_y, dim_x = tiff_movie.shape[1:]
            n_frames = tiff_movie.shape[0]
            motion_corrected_img_series = TwoPhotonSeries(name='motion_corrected_ci_movie', dimension=[dim_x, dim_y],
                                                          data=tiff_movie,
                                                          imaging_plane=imaging_plane,
                                                          starting_frame=[0], format=movie_format, rate=imaging_rate)
            if original_movie_file_name is not None:
                original_tiff_movie = self.load_tiff_movie_in_memory(original_movie_file_name,
                                                                     frames_to_add=frames_to_add)
                dim_y, dim_x = original_tiff_movie.shape[1:]
                original_img_series = TwoPhotonSeries(name='original_ci_movie', dimension=[dim_x, dim_y],
                                                      data=original_tiff_movie,
                                                      imaging_plane=imaging_plane,
                                                      starting_frame=[0], format=movie_format,
                                                      rate=imaging_rate)
        else:
            # TODO: if 'external' see how to keep in memory frames_to_add ?
            #  as a time series of nb of segments to add x 2 (frame after which to add, and nb of frames) ?
            im = PIL.Image.open(motion_corrected_file_name)
            n_frames = len(list(ImageSequence.Iterator(im)))
            dim_y, dim_x = np.array(im).shape
            motion_corrected_img_series = TwoPhotonSeries(name='motion_corrected_ci_movie', dimension=[dim_x, dim_y],
                                                          external_file=[motion_corrected_file_name],
                                                          imaging_plane=imaging_plane,
                                                          starting_frame=[0], format=movie_format, rate=imaging_rate)
            if original_movie_file_name is not None:
                im = PIL.Image.open(original_movie_file_name)
                dim_y, dim_x = np.array(im).shape
                original_img_series = TwoPhotonSeries(name='original_ci_movie',
                                                      dimension=[dim_x, dim_y],
                                                      external_file=[original_movie_file_name],
                                                      imaging_plane=imaging_plane,
                                                      starting_frame=[0], format=movie_format,
                                                      rate=imaging_rate)

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
                if (frames_to_add is not None) and (frame in frames_to_add):
                    frame_index += frames_to_add[frame]
            xy_translation_time_series = TimeSeries(name="xy_translation", data=xy_translation)
            corrected_image_stack = CorrectedImageStack(corrected=motion_corrected_img_series,
                                                        original=original_img_series,
                                                        xy_translation=xy_translation_time_series)


class ConvertSuite2PRoisToNWB(ConvertToNWB):

    def __init__(self, nwb_file):
        super().__init__(nwb_file)

    def convert(self, **kwargs):
        super().convert(**kwargs)
        if "suite2p_dir" not in kwargs:
            raise Exception(f"'suite2p_dir' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")
        suite2p_dir = kwargs["suite2p_dir"]

        image_series = self.nwb_file.acquisition["motion_corrected_ci_movie"]

        mod = self.nwb_file.create_processing_module('ophys', 'contains optical physiology processed data')
        img_seg = ImageSegmentation()
        mod.add_data_interface(img_seg)
        imaging_plane = self.nwb_file.get_imaging_plane("my_imgpln")
        ps = img_seg.create_plane_segmentation('output from segmenting my favorite imaging plane',
                                               imaging_plane, 'my_planeseg', image_series)

        stat = np.load(os.path.join(suite2p_dir, "stat.npy"),
                       allow_pickle=True)
        is_cell = np.load(os.path.join(suite2p_dir, "iscell.npy"),
                          allow_pickle=True)

        if image_series.format == "tiff":
            dim_y, dim_x = image_series.data.shape[1:]
            n_frames = image_series.data.shape[0]
            print(f"dim_y, dim_x: {image_series.data.shape[1:]}")
        elif image_series.format == "external":
            im = PIL.Image.open(image_series.external_file[0])
            n_frames = len(list(ImageSequence.Iterator(im)))
            dim_y, dim_x = np.array(im).shape
            print(f"dim_y, dim_x: {np.array(im).shape}")
        else:
            raise Exception(f"Format of calcium movie imaging {image_series.format} not yet implemented")

        n_cells = 0
        # Add rois
        for cell in np.arange(len(stat)):
            if is_cell[cell][0] == 0:
                continue
            n_cells += 1
            pix_mask = [(y, x, 1) for x, y in zip(stat[cell]["xpix"], stat[cell]["ypix"])]
            image_mask = np.zeros((dim_y, dim_x))
            for pix in pix_mask:
                image_mask[pix[0], pix[1]] = pix[2]
            # we can id to identify the cell (int) otherwise it will be incremented at each step
            ps.add_roi(pixel_mask=pix_mask, image_mask=image_mask)

        fl = Fluorescence()
        mod.add_data_interface(fl)

        rt_region = ps.create_roi_table_region('all cells', region=list(np.arange(n_cells)))
        if format == "external":
            if image_series.external_file[0].endswith(".tiff") or \
                    image_series.external_file[0].endswith(".tif"):
                # TODO: See how to deal if some frames need to be added
                ci_movie = ConvertCIMovieToNWB.load_tiff_movie_in_memory(image_series.external_file[0])
            else:
                raise Exception(f"Calcium imaging format not supported yet {image_series.external_file[0]}")
        else:
            ci_movie = image_series.data
        raw_traces = np.zeros((n_cells, ci_movie.shape[0]))
        for cell in np.arange(n_cells):
            img_mask = ps['image_mask'][cell]
            img_mask = img_mask.astype(bool)
            raw_traces[cell, :] = np.mean(ci_movie[:, img_mask], axis=1)
        rrs = fl.create_roi_response_series(name='my_rrs', data=raw_traces, unit='lumens',
                                            rois=rt_region, timestamps=np.arange(n_frames),
                                            description="raw traces")


class ConvertAbfToNWB(ConvertToNWB):

    def __init__(self, nwb_file):
        super().__init__(nwb_file)
        self.abf_sampling_rate = None

    def convert(self, **kwargs):
        super().convert(**kwargs)
        # TODO: See to use a default config yaml file and use a specific yaml file,
        #  only if this abf doesn't follow the default configuration.
        if "abf_yaml_file_name" not in kwargs:
            raise Exception(f"'abf_yaml_file' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        if "abf_file_name" not in kwargs:
            raise Exception(f"'abf_file_name' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        # yaml_file that will contains the information to read the abf file
        abf_yaml_file_name = kwargs["abf_yaml_file_name"]

        with open(abf_yaml_file_name, 'r') as stream:
            abf_yaml_data = yaml.safe_load(stream)

        if "frames_channel" in abf_yaml_data:
            frames_channel = int(abf_yaml_data["frames_channel"])
        else:
            raise Exception(f"No 'frames_channel' provided in the yaml file "
                            f"{abf_yaml_file_name}")

        # channel with the LFP data
        lfp_channel = abf_yaml_data.get("lfp_channel")
        # give the sampling rate to use for downsampling the lfp and record
        # it in the nwb file. If no argument, then the original sampling_rate will be kept
        lfp_downsampling_hz = abf_yaml_data.get("lfp_downsampling_hz")

        # channel with the run data
        run_channel = abf_yaml_data.get("run_channel")
        run_downsampling_hz = abf_yaml_data.get("run_downsampling_hz")

        # channel with the piezzo data (could be more than one channel
        piezzo_channels = abf_yaml_data.get("piezzo_channels")
        piezzo_downsampling_hz = abf_yaml_data.get("piezzo_downsampling_hz")

        # if given, indicated an offset to be taken in consideration between the data acquisition
        # and the frames
        offset = abf_yaml_data.get("offset")

        if piezzo_channels is not None and isinstance(piezzo_channels, int):
            # converting int in list
            piezzo_channels = [piezzo_channels]

        abf_file_name = kwargs["abf_file_name"]

        try:
            abf = pyabf.ABF(abf_file_name)
        except (FileNotFoundError, OSError) as e:
            raise Exception(f"Abf file not found: {abf_file_name}")

        abf.setSweep(sweepNumber=0, channel=frames_channel)
        times_in_sec = abf.sweepX
        frames_data = abf.sweepY
        original_time_in_sec = times_in_sec
        original_frames_data = frames_data
        # first frame corresponding at the first frame recorded in the calcium imaging movie
        first_frame_index = np.where(frames_data < 0.01)[0][0]

        # looping through the channels
        # for current_channel in np.arange(1, abf.channelCount):
        #     times_in_sec = np.copy(original_time_in_sec)
        #     frames_data = np.copy(original_frames_data)

        if run_channel is not None:
            self.process_run_data(run_channel=run_channel)

    def detect_run_periods(self, run_data, min_speed):
        nb_period_by_wheel = 500
        wheel_diam_cm = 2 * math.pi * 1.75
        cm_by_period = wheel_diam_cm / nb_period_by_wheel
        binary_mvt_data = np.zeros(len(run_data), dtype="int8")
        speed_by_time = np.zeros(len(run_data))
        is_running = np.zeros(len(run_data), dtype="int8")

        binary_mvt_data[run_data >= 4] = 1
        d_times = np.diff(binary_mvt_data)
        pos_times = np.where(d_times == 1)[0] + 1
        for index, pos in enumerate(pos_times[1:]):
            run_duration = pos - pos_times[index - 1]
            run_duration_s = run_duration / self.abf_sampling_rate
            # in cm/s
            speed = cm_by_period / run_duration_s
            # if speed < 1:
            #     print(f"#### speed_i {index}: {np.round(speed, 3)}")
            # else:
            #     print(f"speed_i {index}: {np.round(speed, 3)}")
            if speed >= min_speed:
                speed_by_time[pos_times[index - 1]:pos] = speed
                is_running[pos_times[index - 1]:pos] = 1
                # print(f"is_running {index}: {pos_times[index-1]} to {pos}")

        #  1024 cycle = 1 tour de roue (= 2 Pi 1.5) -> Vitesse (cm / temps pour 1024 cycles).
        # the period of time between two 1 represent a run
        mvt_periods = get_continous_time_periods(is_running)
        mvt_periods = self.merging_time_periods(time_periods=mvt_periods,
                                                min_time_between_periods=0.5 * self.abf_sampling_rate)
        print(f"mvt_periods {mvt_periods}")
        speed_during_mvt_periods = []
        for period in mvt_periods:
            speed_during_mvt_periods.append(speed_by_time[period[0]:period[1] + 1])
        return mvt_periods, speed_during_mvt_periods, speed_by_time


    def process_run_data(self, run_channel, abf, times_in_sec, frames_data, first_frame_index,
                         abf_sampling_rate):
        running_data = None
        times_in_sec = times_in_sec[:-first_frame_index]
        frames_data = frames_data[first_frame_index:]
        threshold_value = 0.02
        if abf_sampling_rate < 50000:
            # frames_data represent the content of the abf channel that contains the frames
            # the index stat at the first frame recorded, meaning the first value where the
            # value is < 0.01
            mask_frames_data = np.ones(len(frames_data), dtype="bool")
            # we need to detect the frames manually, but first removing data between movies
            selection = np.where(frames_data >= threshold_value)[0]
            mask_selection = np.zeros(len(selection), dtype="bool")
            pos = np.diff(selection)
            # looking for continuous data between movies
            to_keep_for_removing = np.where(pos == 1)[0] + 1
            mask_selection[to_keep_for_removing] = True
            selection = selection[mask_selection]
            # we remove the "selection" from the frames data
            mask_frames_data[selection] = False
            frames_data = frames_data[mask_frames_data]
            # len_frames_data_in_s = np.round(len(frames_data) / self.abf_sampling_rate, 3)

            active_frames = np.linspace(0, len(frames_data), 12500).astype(int)
            mean_diff_active_frames = np.mean(np.diff(active_frames)) / self.abf_sampling_rate
            # print(f"mean diff active_frames {np.round(mean_diff_active_frames, 3)}")
            if mean_diff_active_frames < 0.09:
                raise Exception("mean_diff_active_frames < 0.09")
        else:
            binary_frames_data = np.zeros(len(frames_data), dtype="int8")
            binary_frames_data[frames_data >= threshold_value] = 1
            binary_frames_data[frames_data < threshold_value] = 0
            # +1 due to the shift of diff
            # contains the index at which each frame from the movie is matching the abf signal
            # length should be 12500
            active_frames = np.where(np.diff(binary_frames_data) == 1)[0] + 1

        abf.setSweep(sweepNumber=0, channel=run_channel)
        run_data = abf.sweepY
        mvt_periods, speed_during_mvt_periods, speed_by_time = \
            self.detect_run_periods(run_data=run_data, min_speed=0.5)
        speed_by_time = speed_by_time[active_frames]

        """
               Source: https://pynwb.readthedocs.io/en/latest/tutorials/domain/brain_observatory.html#sphx-glr-tutorials-domain-brain-observatory-py
            
        """
        running_speed_time_series = TimeSeries(
            name='running_speed',
            data=speed_by_time,
            timestamps=timestamps,
            unit='cm/s')

        self.nwbfile.add_acquisition(running_speed_time_series)



def create_nwb_file(format_movie):
    root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
    path_data = os.path.join(root_path, "data_cicada_format")
    session_id = "p6_18_02_07_a001"
    tiff_file_name = f"{session_id}/{session_id}.tif"
    yaml_file_name = f"{session_id}/{session_id}.yaml"

    # Weight SI unit is newton

    yaml_data = None
    with open(os.path.join(path_data, yaml_file_name), 'r') as stream:
        yaml_data = yaml.safe_load(stream)
    if yaml_data is None:
        raise Exception(f"Issue while reading the file {yaml_file_name}")

    keys_kwargs_subject = ["age", "weight", "genotype", "subject_id", "species", "sex", "date_of_birth"]
    kwargs_subject = dict()
    for key in keys_kwargs_subject:
        kwargs_subject[key] = yaml_data.get(key)
        if kwargs_subject[key] is not None:
            kwargs_subject[key] = str(kwargs_subject[key])
    print(f'kwargs_subject {kwargs_subject}')
    subject = Subject(**kwargs_subject)

    #####################################
    # ###    creating the NWB file    ###
    #####################################
    keys_kwargs_nwb_file = ["session_description", "identifier", "session_start_time", "session_id",
                            "experimenter", "experiment_description", "institution", "keywords",
                            "notes", "pharmacology", "protocol", "related_publications",
                            "source_script", "source_script_file_name", "data_collection", "surgery", "virus",
                            "stimulus_notes", "lab"
                            ]
    # TODO: for "notes", "pharmacology", "protocol", "related_publications" "data_collection", "surgery", "virus",
    #  "stimulus_notes" see if yaml format is the best option ?

    kwargs_nwb_file = dict()
    for key in keys_kwargs_nwb_file:
        kwargs_nwb_file[key] = yaml_data.get(key)
        if kwargs_nwb_file[key] is not None:
            kwargs_nwb_file[key] = str(kwargs_nwb_file[key])
    if "session_description" not in kwargs_nwb_file:
        raise Exception(f"session_description is needed in the file {yaml_file_name}")
    if "identifier" not in kwargs_nwb_file:
        raise Exception(f"identifier is needed in the file {yaml_file_name}")
    if "session_start_time" not in kwargs_nwb_file or kwargs_nwb_file["session_start_time"] is None:
        kwargs_nwb_file["session_start_time"] = datetime.now(tzlocal())
    if "session_id" not in kwargs_nwb_file:
        kwargs_nwb_file["session_id"] = kwargs_nwb_file["identifier"]

    # #### arguments that are not in the yaml file (yet ?)
    # file_create_date, timestamps_reference_time=None, slices=None, acquisition=None, analysis=None, stimulus=None,
    # stimulus_template=None, epochs=None, epoch_tags=set(), trials=None, invalid_times=None,
    # time_intervals=None, units=None, modules=None, lab_meta_data=None, electrodes=None,
    # electrode_groups=None, ic_electrodes=None, sweep_table=None, imaging_planes=None,
    # ogen_sites=None, devices=None, subject=None

    kwargs_nwb_file["subject"] = subject
    kwargs_nwb_file["file_create_date"] = datetime.now(tzlocal())
    # TODO: See how to load invalid_times, from yaml file ?
    # kwargs_nwb_file["invalid_times"] = invalid_times
    print(f'kwargs_nwb_file {kwargs_nwb_file}')
    nwb_file = NWBFile(**kwargs_nwb_file)

    # TODO: if yaml file stating which file to open with which instance of ConvertToNWB,
    #  use it, otherwise read a directory and depending on extension of the file and keywords
    #  using a yaml file that map those to an instance ConvertToNWB. There should be a default
    #  yaml file for this mapping and use could make its own that will override the default one.
    #  the yaml file should associated for each argument of the convert function the keyword +
    #  extension allowing to find the file_name to give as argument.
    ci_movie_converter = ConvertCIMovieToNWB(nwb_file)
    ci_movie_converter.convert(format=format_movie,
                               motion_corrected_file_name=os.path.join(path_data, tiff_file_name),
                               non_motion_corrected_file_name=None,
                               xy_translation_file_name=None,
                               yaml_file_name=os.path.join(path_data, yaml_file_name))

    suite2p_dir = os.path.join(path_data, "p6_18_02_07_a001", "suite2p")
    suite2p_rois_converter = ConvertSuite2PRoisToNWB(nwb_file)
    suite2p_rois_converter.convert(suite2p_dir=suite2p_dir)


    # TODO: use create_time_intervals(name, description='experimental intervals', id=None, columns=None, colnames=None)
    #  to create time_intervals using npy files or other file in which intervals are contained through a
    #  an instance of ConvertToNWB and the yaml_file for extension and keywords

    with NWBHDF5IO(os.path.join(path_data, 'ophys_example.nwb'), 'w') as io:
        io.write(nwb_file)


def load_nwb_file():
    root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
    path_data = os.path.join(root_path, "data_cicada_format")
    io = NWBHDF5IO(os.path.join(path_data, 'ophys_example.nwb'), 'r')
    nwb_file = io.read()

    # print(f"nwb_file.acquisition {nwb_file.acquisition}")
    image_series = nwb_file.acquisition["motion_corrected_ci_movie"]
    if image_series.format == "external":
        print(f"image_series.external_file[0] {image_series.external_file[0]}")
    elif image_series.format == "tiff":
        print(f"image_series.data.shape {image_series.data.shape}")
        # plt.imshow(image_series.data[0, :])
        # plt.show()
    mod = nwb_file.modules['ophys']

    ps = mod['ImageSegmentation'].get_plane_segmentation()

    rrs = mod['Fluorescence'].get_roi_response_series()

    # get the data...
    rrs_data = rrs.data
    rrs_timestamps = rrs.timestamps
    rrs_rois = rrs.rois
    # and now do something cool!

    print(f"rrs_data.shape {rrs_data.shape}")
    # plt.plot(rrs_data[0])
    # plt.show()


def test_main():
    # interesting page: https://nwb-schema.readthedocs.io/en/latest/format.html#sec-labmetadata
    # IntervalSeries: used for interval periods
    create_nwb_file(format_movie="tiff")  # "tiff"

    # load_nwb_file()


test_main()
