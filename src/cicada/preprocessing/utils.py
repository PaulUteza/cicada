import os
import sys
import ntpath
from itertools import groupby
from operator import itemgetter
from pynwb import NWBHDF5IO

def get_subfiles(current_path, depth=1):
    # Get all files in the last directory of the path
    subfiles = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        subfiles.extend(filenames)
        depth -= 1
        if depth == 0:
            break
    return subfiles


def get_subdirs(current_path, depth=1):
    # Get all directories in the last directory of the path
    subdirs = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        subdirs.extend(dirnames)
        depth -= 1
        if depth == 0:
            break
    return subdirs

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_continous_time_periods(binary_array):
    """
    take a binary array and return a list of tuples representing the first and last position(included) of continuous
    positive period
    :param binary_array:
    :return:
    """
    binary_array = np.copy(binary_array).astype("int8")
    n_times = len(binary_array)
    d_times = np.diff(binary_array)
    # show the +1 and -1 edges
    pos = np.where(d_times == 1)[0] + 1
    neg = np.where(d_times == -1)[0] + 1

    if (pos.size == 0) and (neg.size == 0):
        if len(np.nonzero(binary_array)[0]) > 0:
            return [(0, n_times-1)]
        else:
            return []
    elif pos.size == 0:
        # i.e., starts on an spike, then stops
        return [(0, neg[0])]
    elif neg.size == 0:
        # starts, then ends on a spike.
        return [(pos[0], n_times-1)]
    else:
        if pos[0] > neg[0]:
            # we start with a spike
            pos = np.insert(pos, 0, 0)
        if neg[-1] < pos[-1]:
            #  we end with aspike
            neg = np.append(neg, n_times - 1)
        # NOTE: by this time, length(pos)==length(neg), necessarily
        h = np.matrix([pos, neg])
        # print(f"len(h[1][0]) {len(h[1][0])} h[1][0] {h[1][0]} h.size {h.size}")
        if np.any(h):
            result = []
            for i in np.arange(h.shape[1]):
                if h[1, i] == n_times-1:
                    result.append((h[0, i], h[1, i]))
                else:
                    result.append((h[0, i], h[1, i]-1))
            return result
    return []

def merging_time_periods(time_periods, min_time_between_periods):
    """
    Take a list of pair of values representing intervals (periods) and a merging thresholdd represented by
    min_time_between_periods. If the time between 2 periods are under this threshold, then we merge those periods.
    It returns a new list of periods.
    :param time_periods: list of list of 2 integers or floats. The second value represent the end of the period,
    the value being included in the period.
    :param min_time_between_periods: a float or integer value
    :return: a list of pair of list.
    """
    n_periods = len(time_periods)
    merged_time_periods = []
    index = 0
    while index < n_periods:
        time_period = time_periods[index]
        if len(merged_time_periods) == 0:
            merged_time_periods.append([time_period[0], time_period[1]])
            index += 1
            continue
        # we check if the time between both is superior at min_time_between_periods
        last_time_period = time_periods[index - 1]
        beg_time = last_time_period[1]
        end_time = time_period[0]
        if (end_time - beg_time) <= min_time_between_periods:
            # then we merge them
            merged_time_periods[-1][1] = time_period[1]
            index += 1
            continue
        else:
            merged_time_periods.append([time_period[0], time_period[1]])
        index += 1
    return merged_time_periods


def class_name_to_file_name(class_name):
    """
    Transform the string representing a class_name, by removing the upper case letters, and inserting
    before them an underscore if 2 upper case letters don't follow. Underscore are also inserted before numbers
    ex: ConvertAbfToNWB -> convert_abf_to_nwb
    :param class_name: string
    :return:
    """

    if len(class_name) == 1:
        return class_name.lower()

    new_class_name = class_name[0]
    for index in range(1, len(class_name)):
        letter = class_name[index]
        if letter.isdigit():
            # first we check if the previous letter was not a digit
            if class_name[index - 1].isupper():
                new_class_name = new_class_name + letter
                continue
            new_class_name = new_class_name + "_" + letter
            continue
        if not letter.isupper():
            new_class_name = new_class_name + letter
            continue
        # first we check if the previous letter was not upper
        if class_name[index - 1].isupper():
            new_class_name = new_class_name + letter
            continue
        new_class_name = new_class_name + "_" + letter

    return new_class_name.lower()


def group_by_param(nwb_path_list, param_list):

    """
    Group NWB files depending on a list of parameters

    Args:
        nwb_path_list (list): List of absolute path to NWB files
        param_list (list): List of parameters to group by

    Returns:
        grouped_list (list): List of NWB files grouped
        param_value_list (list) : List of values of the parameter that decided each group

    """

    # Dict containing all parameters and data that can be used to sort
    param_map = {"age": "nwb_file.subject", "sex": "nwb_file.subject", "genotype": "nwb_file.subject",
                 "species": "nwb_file.subject", "subject_id": "nwb_file.subject", "weight": "nwb_file.subject",
                 "date_of_birth": "nwb_file.subject",
                 "session_start_time": "nwb_file", "file_create_date": "nwb_file", "experimenter": "nwb_file",
                 "session_id": "nwb_file", "institution": "nwb_file", "keywords": "nwb_file",
                 "pharmacology": "nwb_file",
                 "protocol": "nwb_file", "related_pulication": "nwb_file",
                 "surgery": "", "virus": "nwb_file", "lab": "nwb_file"}

    data_map = {"fluorescence": "nwb_file.modules['ophys']['Fluorescence']",
                "imagesegmentation": "nwb_file.modules['ophys']['ImageSegmentation']",
                "rasterplot": "nwb_file.modules['ophys']['Rasterplot']"
                }

    # Extract data from NWB and then sort it
    result = []
    for nwb_path in nwb_path_list:
        nwb_result = []
        io = NWBHDF5IO(nwb_path, 'r')
        nwb_file = io.read()
        for param in param_list:
            if param in param_map.keys():
                try:
                    nwb_object = eval(param_map[param])
                    attrib = getattr(nwb_object, param)
                except KeyError:
                    attrib = None
            elif param in data_map.keys():
                try:
                    if eval(data_map[param]):
                        attrib = True
                except KeyError:
                    attrib = False
            else:
                attrib = None
            nwb_result.append(attrib)
        nwb_result.append(nwb_file.identifier)
        io.close()
        result.append(nwb_result)
    grouped_list = []
    param_value_list = []
    sorted_list = sorted(result, key=lambda x: (x is None, x))
    for k, g in groupby(sorted_list, itemgetter(0)):
        t = list(zip(*g))
        param_value_list.append(t[0][0])
        grouped_list.append(list(t[len(t)-1]))
    return grouped_list, param_value_list



def sort_by_param(nwb_path_list, param_list):

    """
    Sort NWB files depending on a list of parameters

    Args:
        nwb_path_list (list): List of absolute path to NWB files
        param_list (list): List of parameters to sort by

    Returns:
        nwb_sorted_list (list): List of NWB files sorted

    """

    # Dict containing all parameters and data that can be used to sort
    param_map = {"age": "nwb_file.subject", "sex": "nwb_file.subject", "genotype": "nwb_file.subject",
                 "species": "nwb_file.subject", "subject_id": "nwb_file.subject", "weight": "nwb_file.subject",
                 "date_of_birth": "nwb_file.subject",
                 "session_start_time": "nwb_file", "file_create_date": "nwb_file", "experimenter": "nwb_file",
                 "session_id": "nwb_file", "institution": "nwb_file", "keywords": "nwb_file",
                 "pharmacology": "nwb_file",
                 "protocol": "nwb_file", "related_pulication": "nwb_file",
                 "surgery": "", "virus": "nwb_file", "lab": "nwb_file"}

    data_map = {"fluorescence": "nwb_file.modules['ophys']['Fluorescence']",
                "imagesegmentation": "nwb_file.modules['ophys']['ImageSegmentation']",
                "rasterplot": "nwb_file.modules['ophys']['Rasterplot']"
                }

    # Extract data from NWB and then sort it
    result = []
    for nwb_path in nwb_path_list:
        nwb_result = []
        io = NWBHDF5IO(nwb_path, 'r')
        nwb_file = io.read()
        for param in param_list:
            if param in param_map.keys():
                try:
                    nwb_object = eval(param_map[param])
                    attrib = getattr(nwb_object, param)
                except KeyError:
                    attrib = None
            elif param in data_map.keys():
                try:
                    if eval(data_map[param]):
                        attrib = True
                except KeyError:
                    attrib = False
            else:
                attrib = None
            nwb_result.append(attrib)
        nwb_result.append(nwb_file.identifier)
        io.close()
        result.append(nwb_result)
    sorted_list = sorted(result, key=lambda x: (x is None, x))
    nwb_sorted_list = [nwb[len(sorted_list[0])-1] for nwb in sorted_list]
    return nwb_sorted_list
