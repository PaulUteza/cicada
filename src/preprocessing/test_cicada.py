from datetime import datetime
from dateutil.tz import tzlocal
import yaml
from pynwb import NWBFile
from pynwb.file import Subject
import os
import pathlib
from pynwb import NWBHDF5IO
from convertcimovietonwb import ConvertCIMovieToNWB
from convertsuite2proistonwb import ConvertSuite2PRoisToNWB
from convertabftonwb import ConvertAbfToNWB
import cicada_data_to_nwb_jd
import utils

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

def create_nwb_file(format_movie):
    # root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
    root_path = "/media/julien/Not_today/hne_not_today/"
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

    abf_converter = ConvertAbfToNWB(nwb_file)
    abf_file_name = os.path.join(path_data, "p6_18_02_07_a001", "p6_18_02_07_001.abf")
    abf_yaml_file_name = os.path.join(path_data, "p6_18_02_07_a001", "p6_18_02_07_a001_abf.yaml")
    abf_converter.convert(abf_file_name=abf_file_name, abf_yaml_file_name=abf_yaml_file_name)
    # TODO: if yaml file stating which file to open with which instance of ConvertToNWB,
    #  use it, otherwise read a directory and depending on extension of the file and keywords
    #  using a yaml file that map those to an instance ConvertToNWB. There should be a default
    #  yaml file for this mapping and use could make its own that will override the default one.
    #  the yaml file should associated for each argument of the convert function the keyword +
    #  extension allowing to find the file_name to give as argument.
    ci_movie_converter = ConvertCIMovieToNWB(nwb_file, ci_sampling_rate=abf_converter.sampling_rate_calcium_imaging)
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

    print(f"Before NWBHDF5IO write: nwb_file.epoch_tags {nwb_file.epoch_tags}")
    with NWBHDF5IO(os.path.join(path_data, 'ophys_example.nwb'), 'w') as io:
        io.write(nwb_file)


def load_nwb_file():
    # root_path = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/"
    root_path = "/media/julien/Not_today/hne_not_today/"
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


def test_main():
    # interesting page: https://nwb-schema.readthedocs.io/en/latest/format.html#sec-labmetadata
    # IntervalSeries: used for interval periods
    test_paul_code = True

    if not test_paul_code:
        create_nwb_file(format_movie="tiff")  # "tiff"

        load_nwb_file()
    else:
        root_path = "/media/julien/Not_today/hne_not_today/"
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
            cicada_data_to_nwb_jd.load_nwb_from_data(subject_dir,
                                                     default_convert_to_nwb_yml_file=default_convert_to_nwb_yml_file)
            # except:
            #     print(f"Error while loading {utils.path_leaf(dir)}")
            #     continue


test_main()
