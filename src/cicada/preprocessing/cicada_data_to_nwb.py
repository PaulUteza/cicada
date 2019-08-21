import yaml
import os
from cicada.preprocessing.utils import class_name_to_file_name, get_subfiles, get_subdirs
import importlib
from pynwb import NWBHDF5IO
from pynwb import NWBFile
from pynwb.file import Subject
from pynwb.epoch import TimeIntervals
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
        files = get_subfiles(os.path.join(dir_path, *directory))

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
            if keyword.lower() not in list_to_filter[counter].lower():
                # print("Keyword not found in : " + str(filtered_list))
                del list_to_filter[counter]
                # print("New list : " + str(filtered_list))
                delete = True
        if (not delete) and keywords_to_exclude:
            for keyword_to_exclude in keywords_to_exclude:
                # we lower both, to make them insensible to case
                if keyword_to_exclude.lower() in list_to_filter[counter].lower():
                    # print("Excluded keyword found in : " + str(filtered_list))
                    del list_to_filter[counter]
                    # print("New list : " + str(filtered_list))
                    delete = True
        if not delete:
            counter += 1


def create_nwb_file(subject_data_yaml_file, session_data_yaml_file):
    """
    Create an NWB file object using all metadata containing in YAML file

    Args:
        subject_data_yaml_file (str): Absolute path to YAML file containing the subject metadata
        session_data_yaml_file (str): Absolute path to YAML file containing the session metadata

    """

    subject_data_yaml = None
    with open(subject_data_yaml_file, 'r') as stream:
        subject_data_yaml = yaml.safe_load(stream)
    if subject_data_yaml is None:
        print(f"Issue while reading the file {subject_data_yaml}")
        return None

    session_data_yaml = None
    with open(session_data_yaml_file, 'r') as stream:
        session_data_yaml = yaml.safe_load(stream)
    if session_data_yaml is None:
        print(f"Issue while reading the file {session_data_yaml}")
        return None

    keys_kwargs_subject = ["age", "weight", "genotype", "subject_id", "species", "sex", "date_of_birth"]
    kwargs_subject = dict()
    for key in keys_kwargs_subject:
        kwargs_subject[key] = subject_data_yaml.get(key)
        if kwargs_subject[key] is not None:
            kwargs_subject[key] = str(kwargs_subject[key])
    if "date_of_birth" in kwargs_subject:
        kwargs_subject["date_of_birth"] = datetime.strptime(kwargs_subject["date_of_birth"], '%m/%d/%Y')
    print(f'kwargs_subject {kwargs_subject}')
    subject = Subject(**kwargs_subject)

    #####################################
    # ###    creating the NWB file    ###
    #####################################
    keys_kwargs_nwb_file = ["session_description", "identifier", "session_id", "session_start_time",
                            "experimenter", "experiment_description", "institution", "keywords",
                            "notes", "pharmacology", "protocol", "related_publications",
                            "source_script", "source_script_file_name",  "surgery", "virus",
                            "stimulus_notes", "slices", "lab_meta_data"]

    kwargs_nwb_file = dict()
    for key in keys_kwargs_nwb_file:
        kwargs_nwb_file[key] = session_data_yaml.get(key)
        if kwargs_nwb_file[key] is not None:
            kwargs_nwb_file[key] = str(kwargs_nwb_file[key])
    if "session_description" not in kwargs_nwb_file:
        print(f"session_description is needed in the file {session_data_yaml_file}")
        return
    if "identifier" not in kwargs_nwb_file:
        print(f"identifier is needed in the file {session_data_yaml_file}")
        return
    if "session_start_time" not in kwargs_nwb_file:
        print(f"session_start_time is needed in the file {session_data_yaml_file}")
        return
    else:
        kwargs_nwb_file["session_start_time"] = datetime.strptime(kwargs_nwb_file["session_start_time"],
                                                                  '%m/%d/%Y %H:%M:%S')
        print(f"kwargs_nwb_file['session_start_time'] {kwargs_nwb_file['session_start_time']}")

    if "session_id" not in kwargs_nwb_file:
        kwargs_nwb_file["session_id"] = kwargs_nwb_file["identifier"]

    # #### arguments that are not in the yaml file (yet ?)
    # file_create_date, timestamps_reference_time=None, acquisition=None, analysis=None, stimulus=None,
    # stimulus_template=None, epochs=None, epoch_tags=set(), trials=None, invalid_times=None,
    # time_intervals=None, units=None, modules=None, electrodes=None,
    # electrode_groups=None, ic_electrodes=None, sweep_table=None, imaging_planes=None,
    # ogen_sites=None, devices=None

    kwargs_nwb_file["subject"] = subject
    kwargs_nwb_file["file_create_date"] = datetime.now(tzlocal())
    # TODO: See how to load invalid_times, from yaml file ?
    # kwargs_nwb_file["invalid_times"] = invalid_times
    print(f'kwargs_nwb_file {kwargs_nwb_file}')
    nwb_file = NWBFile(**kwargs_nwb_file)

    # nwb_file.invalid_times = TimeIntervals(name="invalid_times",
    #                                        description="Time intervals to be removed from analysis'")


    return nwb_file

def convert_data_to_nwb(data_to_convert_dir, default_convert_to_nwb_yml_file, nwb_files_dir):
    """
    Convert all default_config_data_for_conversion located in dir_path and put it in NWB format then create the file.
    Use the yaml file contains in dir_path to convert the default_config_data_for_conversion.
    A yaml file with in its name session_data and one with subject_data must be in directory.
    Otherwise nothing will happend.
    A yaml file with abf in its name will need to be present to convert the abf default_config_data_for_conversion.

    Args:
        data_to_convert_dir (str): Absolute path to the directory containing all data
        default_convert_to_nwb_yml_file (str): Absolute path to the default YAML file to convert an NWB file
        nwb_files_dir (str): Absolute path to the directory where to save the nwb file created

    """
    # Get all files and directories present in the path
    files = get_subfiles(data_to_convert_dir)
    dirs = get_subdirs(data_to_convert_dir)
    files = files + dirs

    default_config_data_for_conversion = None
    with open(default_convert_to_nwb_yml_file, 'r') as stream:
        default_config_data_for_conversion = yaml.safe_load(stream)

    config_data_for_conversion = dict()
    # Look for another YAML file containing the keywords, extensions and keywords to exclude
    for file in files:
        if not(file.endswith(".yaml") or file.endswith(".yml")):
            continue
        if "create_nwb_data" in file:
            with open(os.path.join(data_to_convert_dir, file), 'r') as stream:
                config_data_for_conversion = yaml.safe_load(stream)

    # If 2 files are provided, the one given by the user will take the priority
    if default_config_data_for_conversion is not None:
        difference = set(list(default_config_data_for_conversion.keys())) - set(list(config_data_for_conversion.keys()))
        for arg in list(difference):
            config_data_for_conversion[arg] = default_config_data_for_conversion[arg]

    # First we create the nwb file because it will be needed for everything

    # The class ConvertToNWB will create the nwb file, based on the 2 yaml file
    create_nwb_data = config_data_for_conversion.pop("CreateNWB")

    session_data_yaml_file = None
    subject_data_yaml_file = None
    for arg in create_nwb_data:
        # If no extension is provided it means we are looking for a directory, so we filter the list of files and
        # directory to only contain directories
        filtered_list = filter_list_of_files(dir_path=data_to_convert_dir, files=files,
                                             extensions=create_nwb_data[arg].get("extension"))
        # Conditional loop to remove all files or directories not containing the keywords
        # or containing excluded keywords
        filter_list_according_to_keywords(list_to_filter=filtered_list,
                                          keywords=create_nwb_data[arg].get("keyword"),
                                          keywords_to_exclude=create_nwb_data[arg].get("keyword_to_exclude"))
        print("Files to pass for " + arg + ": " + str(filtered_list))
        if len(filtered_list) == 0:
            continue
        # If files were found respecting every element, add the whole path to pass them as arguments
        if arg == "session_data_yaml":
            session_data_yaml_file = os.path.join(data_to_convert_dir, filtered_list[0])
        elif arg == "subject_data_yaml":
            subject_data_yaml_file = os.path.join(data_to_convert_dir, filtered_list[0])

    if subject_data_yaml_file is None:
        print(f"Conversion of data in {data_to_convert_dir} not possible, no yaml file found with 'subject_data' in its name.")
        return
    if session_data_yaml_file is None:
        print(f"Conversion of data in {data_to_convert_dir} not possible, no yaml file found with 'session_data' in its name.")
        return
    nwb_file = create_nwb_file(subject_data_yaml_file=subject_data_yaml_file,
                               session_data_yaml_file=session_data_yaml_file)
    # raise Exception("NOT TODAY")
    if nwb_file is None:
        return

    converter_dict = dict()
    order_list = []
    if config_data_for_conversion.get("order"):
        order_list = config_data_for_conversion.pop("order")
    class_names_list = list(config_data_for_conversion.keys())
    # putting them on the right order
    class_names_list = order_list + list(set(class_names_list) - set(order_list))
    for class_name in class_names_list:
        if class_name not in config_data_for_conversion:
            # in a class in order would not have been added to the yaml file
            continue
        keys = list(config_data_for_conversion[class_name].keys())
        if len(keys) == 0:
            continue
        first_key = keys[0]
        if isinstance(first_key, int):
            # means we need to create more than one instance of this class
            for key, config_dict in config_data_for_conversion[class_name].items():
                create_convert_class(class_name, config_dict, converter_dict, nwb_file,
                                     default_convert_to_nwb_yml_file, files, data_to_convert_dir)
        else:
            create_convert_class(class_name, config_data_for_conversion[class_name], converter_dict, nwb_file,
                                 default_convert_to_nwb_yml_file, files, data_to_convert_dir)

    # Create NWB file in the data folder
    # nwb_name = path_leaf(data_to_convert_dir) + ".nwb"
    # adding the time of creation of the file, to make sure we don't erase another one
    time_str = datetime.now().strftime("%Y_%m_%d.%H-%M-%S")
    nwb_name = nwb_file.identifier + "_" + time_str + ".nwb"
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
        nwb_file:
        yaml_path:
        files:
        dir_path:
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
        if not isinstance(config_dict[arg], dict):
            # in this case we keep the actual value
            continue
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
        # If value if found, and no extension is given, it means the argument is not a file but a string/int/etc
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
                file_name = filtered_list[0]
                if config_dict[arg].get("dir"):
                    directory = config_dict[arg].get("dir")
                    arg_dict[arg] = os.path.join(dir_path, *directory, file_name)
                else:
                    arg_dict[arg] = os.path.join(dir_path, file_name)
                if (file_name.endswith("mat") or file_name.endswith("npz")) and \
                        config_dict[arg].get("value"):
                    if file_name.endswith("npz"):
                        arg_dict[arg] = np.load(arg_dict[arg])
                        arg_dict[arg] = arg_dict[arg][config_dict[arg].get("value")]
                    else:
                        arg_dict[arg] = hdf5storage.loadmat(arg_dict[arg])
                        arg_dict[arg] = arg_dict[arg][config_dict[arg].get("value")][0]
                    # another option will be to pass the file_name + the value field like this:
                    # arg_dict[arg] = [arg_dict[arg]] + list(config_dict[arg].get("value"))
                    arg_dict[arg] = arg_dict[arg]
            # If no file found, put the argument at None
            else:
                arg_dict[arg] = None

    converter.convert(**arg_dict)

