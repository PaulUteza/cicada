from cicada.preprocessing.convert_to_nwb import ConvertToNWB
import numpy as np
import yaml
import pyabf
import math
from pynwb.base import TimeSeries
from cicada.preprocessing.utils import get_continous_time_periods, merging_time_periods, class_name_to_file_name

class ConvertAbfToNWB(ConvertToNWB):
    """Class to convert ABF data to NWB """
    def __init__(self, nwb_file):
        super().__init__(nwb_file)
        self.abf = None
        self.first_frame_index = 0
        # array of integers representing the index at which the frame has been acquired
        # the indices is used in sweepY
        self.ci_frames_indices = None
        self.frames_data = None
        self.timestamps_in_sec = None
        self.timestamps_in_ms = None
        # means if there are more than one movie, we consider it as one movie (concatenation of the segments)
        # without any breaks in the movie
        self.fusion_movie_segments = False
        self.sampling_rate_calcium_imaging = None
        # contains the frames indices (matching self.ci_frames_indices) after which there is a gap (for ex when
        # 2 movies are concatenated)
        self.gap_indices = np.zeros(0, dtype="int16")

    def convert(self, **kwargs):
        """
        The goal of this function is to extract from an Axon Binary Format (ABF) file its content
        and make it accessible through the NWB file.
        The content can be: LFP signal, piezzo signal, speed of the animal on the treadmill. All, None or a few
        of these informations could be available.
        One information always present is the timestamps, at the abf sampling_rate, of the frames acquired
        by the microscope to create the calcium imaging movie. Such movie could be the concatenation of a few
        movies, such is the case if the movie need to be saved every x frames for memory issue for ex.
        If the movie is the concatenation of many, then there is an option to choose to extract the information as
        if 2 frames concatenate are contiguous in times (such as then LFP signal or piezzo would be match movie),
        or to add interval_times indicating at which time the recording is on pause and at which time it's starting
        again. The time interval containing this information is named "ci_recording_on_pause" and you can get it
        doing:
        if 'ci_recording_on_pause' in nwb_file.intervals:
        pause_intervals = nwb_file.intervals['ci_recording_on_pause']

        Args:
            **kwargs (dict) : kwargs is a dictionary, potentials keys and values types are:
            abf_yaml_file_name: mandatory parameter. The value is a string representing the path
            and file_name of the yaml file associated to this abf file. In the abf:
            frames_channel: mandatory parameter. The value is an int representing the channel
            of the abf in which is the frames timestamps data.
            abf_file_name: mandatory parameter. The value is a string representing the path
            and file_name of the abf file.

        """
        super().convert(**kwargs)

        if "abf_yaml_file_name" not in kwargs:
            raise Exception(f"'abf_yaml_file' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        if "abf_file_name" not in kwargs:
            raise Exception(f"'abf_file_name' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        if "fusion_movie_segments" in kwargs:
            self.fusion_movie_segments = bool(kwargs["fusion_movie_segments"])

        # yaml_file that will contains the information to read the abf file
        abf_yaml_file_name = kwargs["abf_yaml_file_name"]
        if abf_yaml_file_name is None:
            return
        with open(abf_yaml_file_name, 'r') as stream:
            abf_yaml_data = yaml.safe_load(stream)

        if "frames_channel" in abf_yaml_data:
            frames_channel = int(abf_yaml_data["frames_channel"])
        else:
            raise Exception(f"No 'frames_channel' provided in the yaml file "
                            f"{abf_yaml_file_name}")

        # key is an int representing a channel index, value is a list of 1 or 2 elements, first element is a string
        # caraterazing the channel name and the second element (optionnal) is the new sampling_rate in which saving
        # the data. If not present, the original sampling_rate will be kept
        channels_to_save_dict = dict()
        # channel with the LFP data
        lfp_channel = abf_yaml_data.get("lfp_channel")
        if lfp_channel is not None:
            channels_to_save_dict[lfp_channel] = ["LFP"]
            # give the sampling rate to use for downsampling the lfp and record
            # it in the nwb file. If no argument, then the original sampling_rate will be kept
            lfp_downsampling_hz = abf_yaml_data.get("lfp_downsampling_hz")
            if lfp_downsampling_hz is not None:
                channels_to_save_dict[lfp_channel].append(lfp_downsampling_hz)

        # channel with the run data
        run_channel = abf_yaml_data.get("run_channel")
        if run_channel is not None:
            channels_to_save_dict[run_channel] = ["run"]

        # channel with the piezzo data (could be more than one channel
        piezo_channels = abf_yaml_data.get("piezo_channels")

        if piezo_channels is not None:
            if isinstance(piezo_channels, int):
                # converting int in list
                piezo_channels = [piezo_channels]
            for piezo_channel in piezo_channels:
                channels_to_save_dict[piezo_channel] = ["piezo_" + str(piezo_channel)]
                piezzo_downsampling_hz = abf_yaml_data.get("piezo_downsampling_hz")
                if piezzo_downsampling_hz is not None:
                    channels_to_save_dict[piezo_channel].append(piezzo_downsampling_hz)

        # if given, indicated an offset to be taken in consideration between the data acquisition
        # and the frames
        offset = abf_yaml_data.get("offset")

        abf_file_name = kwargs["abf_file_name"]
        """
        dir(abf):
        abf ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', 
        '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', 
        '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
        '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_adcSection', '_cacheStimulusFiles', 
        '_dacSection', '_dataGain', '_dataOffset', '_dtype', '_epochPerDacSection', '_epochSection', 
        '_fileSize', '_headerV2', '_ide_helper', '_loadAndScaleData', '_makeAdditionalVariables', 
        '_nDataFormat', '_preLoadData', '_protocolSection', '_readHeadersV1', '_readHeadersV2', 
        '_sectionMap', '_stringsIndexed', '_stringsSection', '_sweepBaselinePoints', '_tagSection', 
        'abfDateTime', 'abfDateTimeString', 'abfFileComment', 'abfFilePath', 'abfID', 'abfVersion', 
        'abfVersionString', 'adcNames', 'adcUnits', 'channelCount', 'channelList', 'creatorVersion', 
        'creatorVersionString', 'dacNames', 'dacUnits', 'data', 'dataByteStart', 'dataLengthMin', 
        'dataLengthSec', 'dataPointByteSize', 'dataPointCount', 'dataPointsPerMs', 'dataRate', 
        'dataSecPerPoint', 'fileGUID', 'headerHTML', 'headerLaunch', 'headerMarkdown', 'headerText', 
        'holdingCommand', 'launchInClampFit', 'protocol', 'protocolPath', 'saveABF1', 'setSweep', 
        'stimulusByChannel', 'stimulusFileFolder', 'sweepC', 'sweepChannel', 'sweepCount', 'sweepD', 
        'sweepEpochs', 'sweepIntervalSec', 'sweepLabelC', 'sweepLabelX', 'sweepLabelY', 'sweepLengthSec', 
        'sweepList', 'sweepNumber', 'sweepPointCount', 'sweepUnitsC', 'sweepUnitsX', 'sweepUnitsY', 
        'sweepX', 'sweepY', 'tagComments', 'tagSweeps', 'tagTimesMin', 'tagTimesSec']
        """
        try:
            self.abf = pyabf.ABF(abf_file_name)
        except (FileNotFoundError, OSError, TypeError) as e:
            print(f"Abf file not found: {abf_file_name}")
            return
        # raise Exception("NOT TODAY")
        self.abf.setSweep(sweepNumber=0, channel=frames_channel)
        timestamps_in_sec = self.abf.sweepX
        # timestamps_in_sec = np.arange(len(self.abf.sweepY)) * (1 / self.abf.dataRate)
        # to avoid issue with float approximation, we compute ourself the timestamps and in ms
        timestamps_in_ms = np.arange(len(self.abf.sweepY)) * (1 / self.abf.dataRate) * 1000
        self.frames_data = self.abf.sweepY
        # first frame corresponding at the first frame recorded in the calcium imaging movie
        self.first_frame_index = np.where(self.frames_data < 0.01)[0][0]
        self.frames_data = self.frames_data[self.first_frame_index:]
        self.timestamps_in_sec = timestamps_in_sec[:-self.first_frame_index]
        self.timestamps_in_ms = timestamps_in_ms[:-self.first_frame_index]
        # to avoid issue with float approximation, we compute ourself the timestamps
        # to avoid issue with float approximation, we compute ourself the timestamps
        # print(f"self.abf.dataSecPerPoint {self.abf.dataSecPerPoint}")
        # print(f"self.timestamps_in_ms[:10] {self.timestamps_in_ms[:10]}")

        # determining ci_frames_indices
        self.determine_ci_frames_indices()
        print(f"abf number of channels: {self.abf.channelCount}")
        print(f"channels_to_save_dict {channels_to_save_dict}")
        for current_channel in np.arange(1, self.abf.channelCount):
            if current_channel not in channels_to_save_dict:
                continue

            if channels_to_save_dict[current_channel][0] == "run":
                self.process_run_data(run_channel=run_channel)
                continue
            # so far this code only analyse run and lfp channel
            if (channels_to_save_dict[current_channel][0] != "LFP") and \
                    (not channels_to_save_dict[current_channel][0].startswith("piezo")):
                continue
            self.abf.setSweep(sweepNumber=0, channel=current_channel)
            # abf_current_channel_data == mvt_data from the previous version
            abf_current_channel_data = self.abf.sweepY
            if offset is not None:
                abf_current_channel_data = abf_current_channel_data + offset
            abf_current_channel_data = abf_current_channel_data[self.first_frame_index:]

            # for LFP we used in the past down_sampling at 1000 Hz and for piezo 50 Hz
            if len(channels_to_save_dict[current_channel]) > 1:
                down_sampling_hz = channels_to_save_dict[current_channel][1]
            else:
                down_sampling_hz = self.abf.dataRate

            sampling_step = int(self.abf.dataRate / down_sampling_hz)

            if (not self.fusion_movie_segments) or (len(self.gap_indices) == 0):
                last_index = min(len(abf_current_channel_data) - 1, self.ci_frames_indices[-1])
                abf_data_to_save = abf_current_channel_data[:last_index:sampling_step]
                abf_data_to_save = np.concatenate((abf_data_to_save, np.array([abf_current_channel_data[last_index]])))
                timestamps_to_save = self.timestamps_in_ms[:last_index:sampling_step]
                timestamps_to_save = np.concatenate((timestamps_to_save,
                                                     np.array([self.timestamps_in_ms[last_index]])))
            else:
                abf_data_to_save = np.zeros(0)
                timestamps_to_save = np.zeros(0)
                # +1 to get the first frame of the segment
                segments_indices = [0] + list(self.gap_indices + 1)
                # print(f"segments_indices {segments_indices}")
                for index_segt, segt_first_frame in enumerate(segments_indices):
                    if index_segt == len(segments_indices) - 1:
                        last_abf_frame = self.ci_frames_indices[-1]
                    else:
                        last_abf_frame = self.ci_frames_indices[segments_indices[index_segt + 1] - 1]
                    if last_abf_frame == len(abf_current_channel_data):
                        last_abf_frame -= 1
                    # sampling_step is produced according to a down_sampling_hz that changes
                    # according to the channel (lfp, piezzo etc...)
                    new_data = abf_current_channel_data[np.arange(self.ci_frames_indices[segt_first_frame],
                                                                  last_abf_frame, sampling_step)]
                    new_timestamps = self.timestamps_in_ms[self.ci_frames_indices[segt_first_frame]:last_abf_frame:
                                                            sampling_step]
                    # by adding the last_abf_frame we change the interval of time between the two last elements
                    # but this allow to keep the data well aligned
                    abf_data_to_save = np.concatenate((abf_data_to_save, new_data,
                                                       np.array([abf_current_channel_data[last_abf_frame]])))
                    timestamps_to_save = np.concatenate((timestamps_to_save, new_timestamps,
                                                       np.array([self.timestamps_in_ms[last_abf_frame]])))

            if (lfp_channel is not None) and (lfp_channel == current_channel):
                name_channel = "LFP"
            else:
                name_channel = "piezo_" + str(np.where(piezo_channels == current_channel)[0][0])

            # given the conversion factor to get the timestamps in sec
            # we record them in ms to have a better precision
            time_series = TimeSeries(
                name=name_channel,
                data=abf_data_to_save,
                timestamps=timestamps_to_save,
                conversion=0.001,
                unit='s')
            # record the data as an acquisition
            # to recover the data do: nwb_file.get_acquisition(name=name_channel)
            self.nwb_file.add_acquisition(time_series)

    def determine_ci_frames_indices(self):
        """
        Using the frames data channel, estimate the timestamps of each frame of the calcium imaging movie.
        If there are breaks between each recording (the movie being a concatenation of different movies), then
        there is an option to either skip those non registered frames that will be skept in all other data (lfp, piezzo,
        ...) or to determine how many frames to add in the movie and where so it matches the other data recording in
        the abf file

        """
        threshold_value = 0.02
        if self.abf.dataRate < 50000:
            # TODO: take in consideration the case when the sampling rate is less than 50k
            #  when it comes to  ci_frames_indices times_intervals
            # frames_data represent the content of the abf channel that contains the frames
            # the index stat at the first frame recorded, meaning the first value where the
            # value is < 0.01
            mask_frames_data = np.ones(len(self.frames_data), dtype="bool")
            # we need to detect the frames manually, but first removing data between movies
            selection = np.where(self.frames_data >= threshold_value)[0]
            mask_selection = np.zeros(len(selection), dtype="bool")
            pos = np.diff(selection)
            # looking for continuous data between movies
            to_keep_for_removing = np.where(pos == 1)[0] + 1
            mask_selection[to_keep_for_removing] = True
            selection = selection[mask_selection]
            # we remove the "selection" from the frames data
            mask_frames_data[selection] = False
            frames_data = self.frames_data[mask_frames_data]

            active_frames = np.linspace(0, len(frames_data), 12500).astype(int)
            mean_diff_active_frames = np.mean(np.diff(active_frames)) / self.abf.dataRate
            if mean_diff_active_frames < 0.09:
                raise Exception("mean_diff_active_frames < 0.09")
        else:
            binary_frames_data = np.zeros(len(self.frames_data), dtype="int8")
            binary_frames_data[self.frames_data >= threshold_value] = 1
            binary_frames_data[self.frames_data < threshold_value] = 0
            # +1 due to the shift of diff
            # contains the index at which each frame from the movie is matching the abf signal
            # length should be 12500
            self.ci_frames_indices = np.where(np.diff(binary_frames_data) == 1)[0] + 1
            # then we want to determine the size of the breaks between each movie segment if there are some
            diff_active_frames = np.diff(self.ci_frames_indices)
            # calculating the gap threshold above which we estimate the movie recording has been on hold
            median_bw_two_frames = np.median(diff_active_frames)
            frames_gap_threshold = median_bw_two_frames + 1 * np.std(diff_active_frames)
            # print(f"median_bw_two_frames in sec {median_bw_two_frames / self.abf.dataRate}: "
            #       f"{1 / (median_bw_two_frames / self.abf.dataRate)} Hz")
            self.gap_indices = np.where(diff_active_frames > frames_gap_threshold)[0]
            # first we calculate the sampling rate of the movie
            # print(f"self.ci_frames_indices[0] {self.ci_frames_indices[0]}")
            if len(self.gap_indices) == 0:
                self.sampling_rate_calcium_imaging = ((self.timestamps_in_ms[self.ci_frames_indices[-1]] - \
                                                       self.timestamps_in_ms[self.ci_frames_indices[0]]) / 1000) / len(
                    self.ci_frames_indices)
            else:
                # contains the sampling rate of each movie recorded
                movies_sampling_rate = []
                for i, gap_index in enumerate(self.gap_indices):
                    first_frame_segment = 0 if i == 0 else self.gap_indices[i - 1] + 1
                    # estimating the sampling rate of the movie
                    segment_time_in_ms = self.timestamps_in_ms[self.ci_frames_indices[gap_index]] - \
                                         self.timestamps_in_ms[self.ci_frames_indices[first_frame_segment]]
                    movies_sampling_rate.append(1 / ((segment_time_in_ms / 1000) / (gap_index - first_frame_segment + 1)))
                    # print(f"movie_sampling_rate {movie_sampling_rate} Hz")
                    # print(f"gap in frames {gap_in_sec*movie_sampling_rate}")

                # estimating the sampling rate of the movie on the last segment
                segment_time_in_ms = self.timestamps_in_ms[self.ci_frames_indices[-1]] - \
                                     self.timestamps_in_ms[self.ci_frames_indices[self.gap_indices[-1] + 1]]
                movies_sampling_rate.append(
                    1 / ((segment_time_in_ms / 1000) / (len(self.ci_frames_indices) - (self.gap_indices[-1] + 1))))
                self.sampling_rate_calcium_imaging = np.mean(movies_sampling_rate)
                print(f"movie_sampling_rate {self.sampling_rate_calcium_imaging} Hz")

                if not self.fusion_movie_segments:
                    # given the conversion factor to get the timestamps in sec
                    # we record them in ms to have a better precision
                    ci_frames_bool = np.zeros(len(self.timestamps_in_ms), dtype='bool')
                    ci_frames_bool[self.ci_frames_indices] = True
                    ci_frames_time_series = TimeSeries(
                        name="ci_frames",
                        data=ci_frames_bool,
                        timestamps=self.timestamps_in_sec,
                        # conversion=0.001,
                        unit='s')
                    # record the data as an acquisition
                    # to recover the data do: nwb_file.get_acquisition(name=name_channel)
                    self.nwb_file.add_acquisition(ci_frames_time_series)
                    # pause_time_intervals = TimeIntervals
                    columns_pause = []
                    columns_pause.append({"name": "start_time", "description": "Start time of epoch, in seconds"})
                    columns_pause.append({"name": "stop_time", "description": "Stop time of epoch, in seconds"})
                    columns_pause.append({"name": "start_original_frame",
                                          "description": "Frame after which the pause starts, using frames from the"
                                                         "original concatenated movie"})
                    columns_pause.append({"name": "stop_original_frame",
                                          "description": "Frame at which the pause ends, using frames from the "
                                                         "original concatenated movie"})
                    pause_time_intervals = self.nwb_file.create_time_intervals(name="ci_recording_on_pause",
                                                         description='Intervals that correspond to '
                                                                     'the time of last frame recorded '
                                                                     'before the pause, and stop_time '
                                                                     'is the time of the first frame '
                                                                     'recorded after the pause, during calcium imaging'
                                                                     'recording.', columns=columns_pause)
                    for i, gap_index in enumerate(self.gap_indices):
                        # print(f"gap_index {gap_index}")
                        # gap_in_ms = self.timestamps_in_ms[self.ci_frames_indices[gap_index + 1]] - \
                        #              self.timestamps_in_ms[self.ci_frames_indices[gap_index]]
                        # gap_in_frames = (gap_in_ms / 1000) * self.sampling_rate_calcium_imaging
                        # the gap in frames is rounded in the floor.

                        # we save as a TimeInterval the interval during which the calcium imaging movie recording
                        # is on pause. First value is the time of last frame recorded before the pause, and stop_time
                        # is the time of the first frame recorded after the pause
                        # print("self.nwb_file.add_epoch")
                        # issue with add_epoch, it does work but after saving, when loading the nwb_file, there is no
                        # epoch. Solution using add_time_intervals inspired by this issue
                        # https://github.com/NeurodataWithoutBorders/pynwb/issues/958
                        # TODO: See to report an issue on the github
                        # self.nwb_file.add_epoch(start_time=self.timestamps_in_sec[self.ci_frames_indices[gap_index]],
                        #                         stop_time=self.timestamps_in_sec[self.ci_frames_indices[gap_index + 1]],
                        #                         timeseries=ci_frames_time_series,
                        #                         tags=['ci_recording_on_pause'])
                        data_dict = {}
                        data_dict["start_time"] = self.timestamps_in_sec[self.ci_frames_indices[gap_index]]
                        data_dict["stop_time"] = self.timestamps_in_sec[self.ci_frames_indices[gap_index + 1]]
                        data_dict["start_original_frame"] = gap_index
                        data_dict["stop_original_frame"] = gap_index + 1
                        pause_time_intervals.add_row(data_dict)

                        # we add those intervals during which the CI recording is on pause as invalid_time
                        # so those time intervals will be removed from analysis'
                        self.nwb_file.add_invalid_time_interval(
                            start_time=self.timestamps_in_sec[self.ci_frames_indices[gap_index]],
                            stop_time=self.timestamps_in_sec[self.ci_frames_indices[gap_index + 1]])

    def detect_run_periods(self, run_data, min_speed):
        """
        Using the data from the abf regarding the speed of the animal on the treadmill, return the speed in cm/s
        at each timestamps as well as period when the animal is moving (using min_speed threshold)

        Args:
            run_data (list): Data from the subject run
            min_speed (int): Minimum speed

        Returns:
            mvt_periods (list): List of movements periods
            speed_during_movement_periods (list) : List of subject speed during movements
            speed_by_time (list) : List of subject speed by time

        """
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
            run_duration_s = run_duration / self.abf.dataRate
            # in cm/s
            speed = cm_by_period / run_duration_s
            if speed >= min_speed:
                speed_by_time[pos_times[index - 1]:pos] = speed
                is_running[pos_times[index - 1]:pos] = 1

        #  1024 cycle = 1 tour de roue (= 2 Pi 1.5) -> Vitesse (cm / temps pour 1024 cycles).
        # the period of time between two 1 represent a run
        mvt_periods = get_continous_time_periods(is_running)
        mvt_periods = merging_time_periods(time_periods=mvt_periods,
                                           min_time_between_periods=0.5 * self.abf.dataRate)

        speed_during_mvt_periods = []
        for period in mvt_periods:
            speed_during_mvt_periods.append(speed_by_time[period[0]:period[1] + 1])
        return mvt_periods, speed_during_mvt_periods, speed_by_time

    def process_run_data(self, run_channel):
        """
        Using the information in run_channel, will add to the nwb_file the speed of the subject at each acquisition
        frame of the movie in cm/s

        Args:
            run_channel (int) : Run channel

        """
        self.abf.setSweep(sweepNumber=0, channel=run_channel)
        run_data = self.abf.sweepY
        mvt_periods, speed_during_mvt_periods, speed_by_time = \
            self.detect_run_periods(run_data=run_data, min_speed=0.5)
        speed_by_time = speed_by_time[self.ci_frames_indices]
        """
        Source: https://pynwb.readthedocs.io/en/latest/tutorials/domain/brain_observatory.html#sphx-glr-tutorials-domain-brain-observatory-py
        Adding the speed at each frame acquisition in cm/s    
        """
        running_speed_time_series = TimeSeries(
            name='running_speed',
            data=speed_by_time,
            timestamps=self.timestamps_in_sec[self.ci_frames_indices],
            unit='cm/s')

        self.nwb_file.add_acquisition(running_speed_time_series)
