import os
import sys
from cicada.preprocessing.cicada_data_to_nwb import convert_data_to_nwb
from cicada.preprocessing.utils import path_leaf
import pathlib

"""
To excecute CICADA preprocessing module from command line
"""

if len(sys.argv) == 1:
    raise Exception("Please provide path to a directory containing sessions or to all paths leading "
                    "to sessions")

else:
    default_convert_to_nwb_yml_file = "pre_processing_default.yaml"
    for current_path in sys.argv[1:]:
        subfiles = []
        # Get all files in directories and subdirectories with their absolute path
        for filepath in pathlib.Path(current_path).glob('**/*'):
            file = (filepath.absolute())
            subfiles.append(str(file))
        dir_path = []
        # Find each default yaml and get its parent directory
        # The parent directory will be the path to pass to the load function
        for i in range(len(subfiles)-1):
            if "default" in subfiles[i]:
                found_yaml = subfiles[i]
                dir_path.append(os.path.abspath(os.path.join(found_yaml, os.pardir)))
        for dir in dir_path:
            # In case one of the directory is not complete/right we don't want the whole thing to stop
            try:
                print(f"Loading data for {path_leaf(dir)}")
                convert_data_to_nwb(dir, default_convert_to_nwb_yml_file=default_convert_to_nwb_yml_file)
            except:
                print(f"Error while loading {path_leaf(dir)}")
                continue
