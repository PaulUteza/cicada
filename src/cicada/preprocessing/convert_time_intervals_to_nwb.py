from cicada.preprocessing.convert_to_nwb import ConvertToNWB
from cicada.preprocessing.utils import get_continous_time_periods
import hdf5storage
import numpy as np
import yaml


class ConvertTimeIntervalsToNWB(ConvertToNWB):
    def __init__(self, nwb_file):
        ConvertToNWB.__init__(self, nwb_file)

    def convert(self, **kwargs):
        """Convert the data and add it to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """
        super().convert(**kwargs)

        if "name" not in kwargs:
            raise Exception(f"'name' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        name = kwargs["name"]

        if "description" not in kwargs:
            raise Exception(f"'description' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        description = kwargs["description"]


        # bool that indicated if the time intervals already takes into consideration the calcium imaging recording
        # pauses. If not, then they will be added so it matches the recording
        ci_recording_pause_included = False
        if "ci_recording_pause_included" in kwargs:
            if kwargs["ci_recording_pause_included"] == "True":
                ci_recording_pause_included = True

        if "intervals_data" not in kwargs:
            raise Exception(f"'intervals_data' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        intervals_data = kwargs["intervals_data"]
        # if True, means we add those intervals to the invalid times recorded in the nwb_file
        as_invalid_times = False

        if isinstance(intervals_data, str):
            # then we check if it's not a file_name
            if intervals_data.endswith(".yaml") or intervals_data.endswith(".yml"):
                with open(intervals_data, 'r') as stream:
                    intervals_yaml_data = yaml.safe_load(stream)
                    intervals_list = []
                    if "as_invalid_times" in intervals_yaml_data:
                        if intervals_yaml_data['as_invalid_times']:
                            as_invalid_times = True
                    if "frame_intervals" not in intervals_yaml_data:
                        print(f"'frame_intervals' not found in the file {intervals_data}, {name} intervals not created")
                        return
                    frame_intervals = intervals_yaml_data["frame_intervals"]
                    start_times_sorted = list(frame_intervals.keys())
                    start_times_sorted.sort()
                    # frame_intervals dict : key represent the frame of the start of the interval,
                    # and value the stop frame
                    for start_time in start_times_sorted:
                        intervals_list.append((start_time, frame_intervals[start_time]))
                    print(f"start_times_sorted {start_times_sorted}")
                    print(f"z_mvts {intervals_list}")
        else:
            # intervals_data so far is 1D array of boolean
            # intervals_list is a sequence of pair of integer representing the first and last frame (included)
            # part of the interval
            intervals_list = get_continous_time_periods(intervals_data.astype("int8"))

        # TODO: see to put option so intervals are not only array of boolean representing the frames
        #  at which action happens

        print(f"In ConvertTimeIntervalsToNWB {name} -> {description} -> {intervals_data}")

        # pause_intervals = None
        # if 'ci_recording_on_pause' in self.nwb_file.intervals:
        #     pause_intervals = self.nwb_file.intervals['ci_recording_on_pause']

        ci_frames_time_series = None
        try:
            ci_frames_time_series = self.nwb_file.get_acquisition("ci_frames")
            print(f"ci_frames_series {ci_frames_time_series}")
        except KeyError:
            print(f"No ci_frames_time_series found in the nwb file, we cannot create the time intervals {name}")
            return

        # we need the sampling rate to add the intervals
        image_series = self.nwb_file.acquisition["motion_corrected_ci_movie"]
        sampling_rate = image_series.rate

        columns_pause = list()
        columns_pause.append({"name": "start_time", "description": "Start time of epoch, in seconds"})
        columns_pause.append({"name": "stop_time", "description": "Stop time of epoch, in seconds"})
        columns_pause.append({"name": "start_original_frame",
                              "description": "Frame at which the epoch starts (included), using frames from the"
                                             "original concatenated movie"})
        columns_pause.append({"name": "stop_original_frame",
                              "description": "Frame at which the epoch stops (included), using frames from the "
                                             "original concatenated movie"})
        time_intervals = self.nwb_file.create_time_intervals(name=name, description=description,
                                                             columns=columns_pause)
        timestamps = None
        if (not ci_recording_pause_included) and (ci_frames_time_series is not None):
            # ci_frames_time_series is a 1d array of boolean, with True if the index correponds to the acquisition of
            # a frame during CI recording. Same length as timestamps, which contains all timestamps of the recording
            # based on the abf sampling_rate
            frames_indices = np.where(ci_frames_time_series.data)[0]
            timestamps = ci_frames_time_series.timestamps

        for interval in intervals_list:
            if timestamps is not None:
                start_time = timestamps[frames_indices[interval[0]]]
                stop_time = timestamps[frames_indices[interval[1]]]
            else:
                # time in seconds
                start_time = interval[0] * (1 / sampling_rate)
                stop_time = interval[1] * (1 / sampling_rate)

            data_dict = {}
            data_dict["start_time"] = start_time
            data_dict["stop_time"] = stop_time
            data_dict["start_original_frame"] = interval[0]
            data_dict["stop_original_frame"] = interval[1]
            time_intervals.add_row(data_dict)
            if as_invalid_times:
                # we add those intervals during which the CI recording is on pause as invalid_time
                # so those time intervals will be removed from analysis'
                self.nwb_file.add_invalid_time_interval(
                    start_time=start_time,
                    stop_time=stop_time)
