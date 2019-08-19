import os
import pathlib
from pynwb import NWBHDF5IO
from cicada.preprocessing.cicada_data_to_nwb import convert_data_to_nwb
import cicada.preprocessing.utils

"""
To excecute CICADA preprocessing module using pycharm
"""

"""
Reusing timestamps
When working with multi-modal data, it can be convenient and efficient to store timestamps once 
and associate multiple data with the single timestamps instance. PyNWB enables this by letting 
you reuse timestamps across TimeSeries objects. To reuse a TimeSeries timestamps in a new TimeSeries, 
pass the existing TimeSeries as the new TimeSeries timestamps:

data = list(range(101, 201, 10))
reuse_ts = TimeSeries('reusing_timeseries', data, 'SIunit', timestamps=test_ts)
"""

"""
https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
https://stackoverflow.com/questions/51142320/how-to-instantiate-class-by-its-string-name-in-python-from-current-file
To import module using string:
https://stackoverflow.com/questions/9806963/how-to-use-pythons-import-function-properly-import
"""


def load_nwb_file():
    root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
    # root_path = "/media/julien/Not_today/hne_not_today/"
    path_data = os.path.join(root_path, "data/nwb_files/")
    io = NWBHDF5IO(os.path.join(path_data, 'p6_18_02_07_a001_2019_08_14.20-38-27.nwb'), 'r')
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
    print(f"nwb_file.processing {nwb_file.processing}")

    print(f"nwb_file.acquisition : {list(nwb_file.acquisition.keys())}")
    try:
        piezo_0_time_series = nwb_file.get_acquisition("piezo_0")
        print(f"piezo_0_time_series {piezo_0_time_series}")
        # print(f"piezo_0_time_series.timestamps {piezo_0_time_series.timestamps[:3]}")
    except KeyError:
        pass

    try:
        ci_frames_time_series = nwb_file.get_acquisition("ci_frames")
        print(f"ci_frames_series {ci_frames_time_series}")
    except KeyError:
        pass

    print(f"nwb_file.epoch_tags {nwb_file.epoch_tags}")

    # time_intervals = nwb_file.get_time_intervals(name="ci_recording_on_pause")
    print(f"intervals {nwb_file.intervals}")
    # if 'ci_recording_on_pause' in nwb_file.intervals:
    #     pause_intervals = nwb_file.intervals['ci_recording_on_pause']
    #     print(f"data_frame: {pause_intervals.to_dataframe()}")

    if nwb_file.intervals is not None:
        for name_interval, time_interval in nwb_file.intervals.items():
            print(f"{name_interval}: {time_interval.to_dataframe()}")

    if nwb_file.invalid_times is not None:
        print(f"nwb_file.invalid_times {nwb_file.invalid_times.to_dataframe()}")
    else:
        print("No invalid times")

    if nwb_file.invalid_times is not None:
        print(f"nwb_file.invalid_times {nwb_file.invalid_times.to_dataframe()}")
    else:
        print("No invalid times")

    ps = mod['segmentation_suite2p'].get_plane_segmentation('my_plane_seg')

    rrs = mod['fluorescence_suite2p'].get_roi_response_series()

    # get the data...
    rrs_data = rrs.data
    rrs_timestamps = rrs.timestamps
    rrs_rois = rrs.rois


    print(f"rrs_data.shape {rrs_data.shape}")
    # plt.plot(rrs_data[0])
    # plt.show()


def cicada_pre_processing_main():
    """
    Main function to be called in order to start the pre_processing
    Returns:

    """
    # interesting page: https://nwb-schema.readthedocs.io/en/latest/format.html#sec-labmetadata
    # IntervalSeries: used for interval periods
    test_paul_code = True

    if not test_paul_code:
        # create_nwb_file(format_movie="tiff")  # "tiff"

        load_nwb_file()
    else:
        # root_path = "/media/julien/Not_today/hne_not_today/"
        root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
        dir_to_explore = os.path.join(root_path, "data")
        default_convert_to_nwb_yml_file = "pre_processing_default.yaml"

        session_dirs = find_dir_to_convert(dir_to_explore=dir_to_explore,
                                           keywords=[["session_data"], ["subject_data"]],
                                           extensions=("yaml", "yml"))
        print(f"session_dirs {session_dirs}")

        nwb_files_dir = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/data/nwb_files/"
        # nwb_files_dir = "H:/Documents/Data/julien/data/nwb_files"
        # nwb_files_dir = "/media/julien/Not_today/hne_not_today/data/nwb_files/"

        for session_dir in session_dirs:
            print(f"Loading data for {os.path.split(session_dir)[1]}")
            convert_data_to_nwb(data_to_convert_dir=session_dir,
                                default_convert_to_nwb_yml_file=default_convert_to_nwb_yml_file,
                                nwb_files_dir=nwb_files_dir)


def find_dir_to_convert(dir_to_explore, keywords, extensions=("yaml", "yml")):
    """
    Recursivefunction that will go through all subdirectories in dir_to_explore
    and look for directories that contains 2 yaml files that contains the keywords "session_data" and "
    Args:
        dir_to_explore:

        key_words: list of list. each list is composed of strings representing the keywords the file should made of

        extensions: extensions of the files we're looking for

    Returns:

    """
    dirs_found = []
    for (dir_path, dir_names, local_filenames) in os.walk(dir_to_explore):

        n_files_found = 0

        for file_name in local_filenames:
            valid_extension = False
            for extension in extensions:
                if file_name.endswith(extension):
                    valid_extension = True
                    continue
            if not valid_extension:
                continue
            for sub_keywords in keywords:
                n_keywords_found = 0
                for keyword in sub_keywords:
                    if keyword in file_name:
                        n_keywords_found += 1
                        continue
                if n_keywords_found == len(sub_keywords):
                    n_files_found += 1
        if n_files_found == len(keywords):
            dirs_found.append(dir_path)

        dirs_to_explore = [dir_name for dir_name in dir_names if (not dir_name.startswith("."))]

        for new_dir_to_explore in dirs_to_explore:
            new_dir_to_explore = os.path.join(dir_path, new_dir_to_explore)
            dirs_found.extend(find_dir_to_convert(dir_to_explore=new_dir_to_explore,
                                                  keywords=keywords,
                                                  extensions=extensions))
        # we could avoid the break, as the loop goes deep in the subdirectories.
        # but by using a recursive function we allows ourselves to filter some directories
        # such as the hidden ones, which starts with a dot.
        break

    return dirs_found


cicada_pre_processing_main()
