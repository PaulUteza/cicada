import yaml
import os
import utils
from utils import class_name_to_file_name
import importlib
from pynwb import NWBHDF5IO
from pynwb import NWBFile
from pynwb.file import Subject
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
import hdf5storage

"""
Load data files and create the NWB file
"""

def filter_list_of_files(dir_path, files, extensions, directory=None):
    """
    Take a list of file names and either no extensions (empty list or None) and remove the directory that starts by
    "." or a list of extension and remove the files that are not with this extension. It returns a new list

    Args:
        dir_path (str): path in which the files ares
        files (list): List of files to be filtered
        extensions (str) : File extension to use as a filter
        directory (str): directory in which looking for files with a given extensions or return files in this directory

    Exemples:
        >>> print(filter_list_of_files(["file1.py", "file2.c", "file3.h"],"py"))
        ["file1.py"]
    """
    """
    Args:
        test (int) : Ok
    """
    filtered_list = []

    if directory:
        # if directory is a list, it means we're going though a list of directory, following the depth order
        if isinstance(directory, str):
            directory = [directory]
        files = utils.get_subfiles(os.path.join(dir_path, *directory))

    if not extensions:
        filtered_list = [file for file in files if not file.startswith(".")]
        return filtered_list

    for extension in extensions:
        filtered_list.extend([file for file in files if file.endswith("." + extension)])

    return filtered_list

def filter_list_according_to_keywords(list_to_filter, keywords, keywords_to_exclude):
    """
    Conditional loop to remove all files or directories not containing the keywords
    # or containing excluded keywords. Inplace list modification

    Args:
        list_to_filter (list): List containing all files/directories to be filtered
        keywords (str): If the list doesn't contain the keyword, remove it from list
        keywords_to_exclude (str): If the list contains the keyword, remove it from list

    Exemples:
        >>> print(filter_list_of_files(["file1.py", "file2.c", "file2.h"],"2","h"))
        ["file2.c"]
    """
    counter = 0
    while counter < len(list_to_filter):
        delete = False
        for keyword in keywords:
            if keyword not in list_to_filter[counter]:
                # print("Keyword not found in : " + str(filtered_list))
                del list_to_filter[counter]
                # print("New list : " + str(filtered_list))
                delete = True
        if (not delete) and keywords_to_exclude:
            for keyword_to_exclude in keywords_to_exclude:
                if keyword_to_exclude in list_to_filter[counter]:
                    # print("Excluded keyword found in : " + str(filtered_list))
                    del list_to_filter[counter]
                    # print("New list : " + str(filtered_list))
                    delete = True
        if not delete:
            counter += 1


def create_nwb_file(yaml_path):
    """
    Create an NWB file object using all metadata containing in YAML file

    Args:
        yaml_path (str): Absolute path to YAML file

    """

    # Weight SI unit is newton
    yaml_data = None
    with open(yaml_path, 'r') as stream:
        yaml_data = yaml.safe_load(stream)
    if yaml_data is None:
        raise Exception(f"Issue while reading the file {yaml_path}")

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
        raise Exception(f"session_description is needed in the file {yaml_path}")
    if "identifier" not in kwargs_nwb_file:
        raise Exception(f"identifier is needed in the file {yaml_path}")
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

    return nwb_file

    # abf_converter = ConvertAbfToNWB(nwb_file)
    # abf_file_name = os.path.join(path_data, "p6_18_02_07_a001", "p6_18_02_07_001.abf")
    # abf_yaml_file_name = os.path.join(path_data, "p6_18_02_07_a001", "p6_18_02_07_a001_abf.yaml")
    # abf_converter.convert(abf_file_name=abf_file_name, abf_yaml_file_name=abf_yaml_file_name)
    # # TODO: if yaml file stating which file to open with which instance of ConvertToNWB,
    # #  use it, otherwise read a directory and depending on extension of the file and keywords
    # #  using a yaml file that map those to an instance ConvertToNWB. There should be a default
    # #  yaml file for this mapping and use could make its own that will override the default one.
    # #  the yaml file should associated for each argument of the convert function the keyword +
    # #  extension allowing to find the file_name to give as argument.
    # ci_movie_converter = ConvertCIMovieToNWB(nwb_file, ci_sampling_rate=abf_converter.sampling_rate_calcium_imaging)
    # ci_movie_converter.convert(format=format_movie,
    #                            motion_corrected_file_name=os.path.join(path_data, tiff_file_name),
    #                            non_motion_corrected_file_name=None,
    #                            xy_translation_file_name=None,
    #                            yaml_file_name=os.path.join(path_data, yaml_file_name))
    #
    # suite2p_dir = os.path.join(path_data, "p6_18_02_07_a001", "suite2p")
    # suite2p_rois_converter = ConvertSuite2PRoisToNWB(nwb_file)
    # suite2p_rois_converter.convert(suite2p_dir=suite2p_dir)

    # TODO: use create_time_intervals(name, description='experimental intervals', id=None, columns=None, colnames=None)
    #  to create time_intervals using npy files or other file in which intervals are contained through a
    #  an instance of ConvertToNWB and the yaml_file for extension and keywords


def convert_data_to_nwb(dir_path, default_convert_to_nwb_yml_file):
    """
    Convert all data and put it in NWB format then create the file

    Args:
        dir_path (str): Absolute path to the directory containing all data
        default_convert_to_nwb_yml_file (str): Absolute path to the default YAML file to convert an NWB file

    """
    # Get all files and directories present in the path
    files = utils.get_subfiles(dir_path)
    dirs = utils.get_subdirs(dir_path)
    files = files + dirs

    data = None
    with open(default_convert_to_nwb_yml_file, 'r') as stream:
        data = yaml.safe_load(stream)

    home_data = dict()
    # Look for another YAML file containing the keywords, extensions and keywords to exclude
    for file in files:
        if not(file.endswith(".yaml") or file.endswith(".yml")):
            continue
        if "convert_to_nwb" in file:
            with open(os.path.join(dir_path, file, 'r')) as stream:
                home_data = yaml.safe_load(stream)

    # If 2 files are provided, the one given by the user will take the priority
    if data is not None:
        difference = set(list(data.keys())) - set(list(home_data.keys()))
        for arg in list(difference):
            home_data[arg] = data[arg]

    # First we create the nwb file because it will be needed for everything
    converttonwb = home_data.pop("ConvertToNWB")

    for arg in converttonwb:
        # If no extension is provided it means we are looking for a directory, so we filter the list of files and
        # directory to only contain directories
        filtered_list = filter_list_of_files(dir_path=dir_path, files=files,
                                             extensions=converttonwb[arg].get("extension"))
        # Conditional loop to remove all files or directories not containing the keywords
        # or containing excluded keywords
        filter_list_according_to_keywords(list_to_filter=filtered_list,
                                          keywords=converttonwb[arg].get("keyword"),
                                          keywords_to_exclude=converttonwb[arg].get("keyword_to_exclude"))
        if len(filtered_list) == 0:
            raise Exception(f"No yaml data file was found in {dir_path}")
        print("Files to pass for " + arg + ": " + str(filtered_list))
        # If files were found respecting every element, add the whole path to pass them as arguments
        yaml_path = os.path.join(dir_path, filtered_list[0])

    nwb_file = create_nwb_file(yaml_path)

    converter_dict = dict()
    order_list = []
    if home_data.get("order"):
        order_list = home_data.pop("order")
    class_names_list = list(home_data.keys())
    # putting them on the right order
    class_names_list = order_list + list(set(class_names_list) - set(order_list))
    for class_name in class_names_list:
        if class_name not in home_data:
            # in a class in order would not have been added to the yaml file
            continue
        keys = list(home_data[class_name].keys())
        if len(keys) == 0:
            continue
        first_key = keys[0]
        if isinstance(first_key, int):
            # means we need to create more than one instance of this class
            for key, config_dict in home_data[class_name].items():
                create_convert_class(class_name, config_dict, converter_dict, nwb_file,
                                     yaml_path, files, dir_path)
        else:
            create_convert_class(class_name, home_data[class_name], converter_dict, nwb_file,
                                 yaml_path, files, dir_path)

    # Create NWB file in the data folder
    nwb_files_dir = "/Users/pappyhammer/Documents/academique/these_inmed/robin_michel_data/data/nwb_files/"
    # nwb_files_dir = "H:/Documents/Data/julien/data/nwb_files"
    # nwb_files_dir = "/media/julien/Not_today/hne_not_today/data/nwb_files/"
    nwb_name = utils.path_leaf(dir_path) + ".nwb"
    print(f"Before NWBHDF5IO write: nwb_file.epoch_tags {nwb_file.epoch_tags}")
    with NWBHDF5IO(os.path.join(nwb_files_dir, nwb_name), 'w') as io:
        io.write(nwb_file)

    print("NWB file created at : " + str(os.path.join(nwb_files_dir, nwb_name)))


def create_convert_class(class_name, config_dict, converter_dict, nwb_file, yaml_path, files, dir_path):
    """

    Args:
        class_name:
        config_dict:
        converter_dict:

    Returns:

    """

    # Get classname then instantiate it
    module_name = class_name_to_file_name(class_name=class_name)
    module_imported = importlib.import_module(module_name)
    class_instance = getattr(module_imported, class_name)
    converter = class_instance(nwb_file)
    # if there is more than one instance of class_name, the last_one will be the one kept in memory in converter_dict
    # useful if another class as a field "from_other_converter"
    converter_dict[class_name] = converter
    # Initialize a dict to contain the arguments to call convert
    arg_dict = {}
    print("Class name : " + str(class_name))
    # Loop through all arguments of the convert of the corresponding class
    for arg in config_dict:
        if config_dict[arg].get("from_other_converter"):
            # means we get the argument value from an instance of a converter, a value should be indicated
            attribute_name = config_dict[arg].get("value")
            if attribute_name is None:
                raise Exception(f"A value argument should be indicated for {class_name} argument {arg} "
                                f"in the yaml file {yaml_path}")
            converter_name = config_dict[arg].get("from_other_converter")
            if converter_name not in converter_dict:
                raise Exception(f"No convert class by the name {converter_name} has been instanciated")
            if isinstance(attribute_name, list):
                attribute_name = attribute_name[0]
            if not isinstance(attribute_name, str):
                raise Exception(f"{attribute_name} is not a string for {class_name} argument {arg} "
                                f"in the yaml file {yaml_path}")
            arg_dict[arg] = getattr(converter_dict[converter_name], attribute_name)
        # If value if found it means the argument is not a file but a string/int/etc
        elif config_dict[arg].get("value") and not config_dict[arg].get("extension") and \
                (not config_dict[arg].get("keyword") or
                 (not config_dict[arg].get("keyword_to_exclude"))):
            # print(config_dict[arg].get("value")[0])
            value = config_dict[arg].get("value")
            if isinstance(value, list):
                value = value[0]
            arg_dict[arg] = value
        else:
            # If no extension is provided it means we are looking for a directory,
            # so we filter the list of files and
            # directory to only contain directories
            filtered_list = filter_list_of_files(files=files,
                                                 dir_path=dir_path,
                                                 extensions=config_dict[arg].get("extension"),
                                                 directory=config_dict[arg].get("dir"))

            # Conditional loop to remove all files or directories not containing the keywords
            # or containing excluded keywords
            filter_list_according_to_keywords(list_to_filter=filtered_list,
                                              keywords=config_dict[arg].get("keyword"),
                                              keywords_to_exclude=config_dict[arg].get("keyword_to_exclude"))

            print("Files to pass for " + arg + ": " + str(filtered_list))
            # If files were found respecting every element, add the whole path to pass them as arguments
            if filtered_list:
                if config_dict[arg].get("dir"):
                    directory = config_dict[arg].get("dir")
                    arg_dict[arg] = os.path.join(dir_path, *directory, filtered_list[0])
                else:
                    arg_dict[arg] = os.path.join(dir_path, filtered_list[0])
                if config_dict[arg].get("extension") in ["mat", "npz"] and \
                        config_dict[arg].get("value"):
                    # TODO: decide if we load the value first or if we pass the file and the argument
                    #  to the function
                    # if home_data[class_name][arg].get("extension") == "npz":
                    #     arg_dict[arg] = np.load(arg_dict[arg], )
                    arg_dict[arg] = [arg_dict[arg]] + list(config_dict[arg].get("value"))
            # If no file found, put the argument at None
            else:
                arg_dict[arg] = None

    converter.convert(**arg_dict)

