import sys
import os
from pynwb import NWBHDF5IO
import utils
import pathlib

"""
key=lambda x: (x is None, x) dans un sorted pour mettre les None au fond
"""

# Get all NWB files in absolute path
subfiles = []
current_path = sys.argv[1]
for filepath in pathlib.Path(current_path).glob('**/*'):
    file = (filepath.absolute())
    subfiles.append(str(file))
nwb_path_list = []
for i in range(len(subfiles) - 1):
    if "nwb" in subfiles[i]:
        found_nwb = subfiles[i]
        nwb_path_list.append(found_nwb)

# Dict containing all parameters and data that can be used to sort
param_map = {"age": "nwb_file.subject", "sex": "nwb_file.subject", "genotype": "nwb_file.subject",
             "species": "nwb_file.subject", "subject_id": "nwb_file.subject", "weight": "nwb_file.subject",
             "date_of_birth": "nwb_file.subject",
             "session_start_time": "nwb_file", "file_create_date": "nwb_file", "experimenter": "nwb_file",
             "session_id": "nwb_file", "institution": "nwb_file", "keywords": "nwb_file", "pharmacology": "nwb_file",
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
    for arg in sys.argv[2:]:
        param = arg
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
print(sorted(result, key=lambda x: (x is None, x)))
