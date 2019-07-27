import yaml
import os
import sys
import utils

def load_nwb_from_data(dir_path, default_convert_to_nwb_yml_file):

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
        # p is a placeholder until we know every yaml file name
        if "convert_to_nwb" in file :
            with open(os.path.join(dir_path, file, 'r')) as stream:
                home_data = yaml.safe_load(stream)

    # toto

    # If 2 files are provided, the one given by the user will take the priority
    if data is not None:
        difference = set(list(data.keys())) - set(list(home_data.keys()))
        for i in list(difference):
            home_data[i] = data[i]

    # First we create the nwb file because it will be needed for everything

