import os
import pathlib
from pynwb import NWBHDF5IO
from convertcimovietonwb import ConvertCIMovieToNWB
from convertsuite2proistonwb import ConvertSuite2PRoisToNWB
from convertabftonwb import ConvertAbfToNWB
from cicada_data_to_nwb import load_nwb_from_data
import utils

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
    io = NWBHDF5IO(os.path.join(path_data, 'p6_18_02_07_a001.nwb'), 'r')
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
    if 'ci_recording_on_pause' in nwb_file.intervals:
        pause_intervals = nwb_file.intervals['ci_recording_on_pause']
        print(f"data_frame: {pause_intervals.to_dataframe()}")

    ps = mod['ImageSegmentation'].get_plane_segmentation()

    rrs = mod['Fluorescence'].get_roi_response_series()

    # get the data...
    rrs_data = rrs.data
    rrs_timestamps = rrs.timestamps
    rrs_rois = rrs.rois


    print(f"rrs_data.shape {rrs_data.shape}")
    # plt.plot(rrs_data[0])
    # plt.show()


def cicada_pre_processing_main():
    # interesting page: https://nwb-schema.readthedocs.io/en/latest/format.html#sec-labmetadata
    # IntervalSeries: used for interval periods
    test_paul_code = False

    if not test_paul_code:
        # create_nwb_file(format_movie="tiff")  # "tiff"

        load_nwb_file()
    else:
        # root_path = "/media/julien/Not_today/hne_not_today/"
        root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
        path_data = os.path.join(root_path, "data_cicada_format")
        default_convert_to_nwb_yml_file = "default.yaml"
        p = pathlib.Path(path_data)
        # subject_dirs = []
        # for (dirpath, dirnames, local_filenames) in os.walk(path_data):
        #     subject_dirs = [dir for dir in dirnames if (not dir.startswith("."))]
        #     break
        subject_dirs = [x for x in p.iterdir() if (x.is_dir()) and (not x.as_posix().startswith("."))]

        for subject_dir in subject_dirs:
            # In case one of the directory is not complete/right we don't want the whole thing to stop
            # try:
            print(f"Loading data for {os.path.split(subject_dir)[1]}")
            load_nwb_from_data(subject_dir,
                                                     default_convert_to_nwb_yml_file=default_convert_to_nwb_yml_file)
            # except:
            #     print(f"Error while loading {utils.path_leaf(dir)}")
            #     continue


cicada_pre_processing_main()
