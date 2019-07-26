import sys
import os
import re
import yaml
import utils


def sort_by_string(current_path, string, base_dir):
    # Sort all files in the corresponding directory

    subdirs = utils.get_subdirs(current_path)
    subfiles = utils.get_subfiles(current_path)
    for i in range(len(subfiles)):
        subfiles[i] = subfiles[i].lower()

    for j in range(len(subdirs)):
        subdirs[j] = subdirs[j].lower()

    # If directory doesn't exist, create it
    if True in [string in subfile for subfile in subfiles] and True not in [string in subdir for subdir in dir_path]:

        os.makedirs(dir_path + "\\" + string, exist_ok=True)
        subdirs.append(string)
        base_dir.append(string)

    # Move file to corresponding directory depending on a key in the file name
    while True in [string in subfile for subfile in subfiles]:

        os.replace(current_path + "\\" + str([subfile for subfile in subfiles if string in subfile][0]),
                   dir_path + "\\" + string + "\\" + str([subfile for subfile in subfiles if string in subfile][0]))
        subfiles.remove(str([subfile for subfile in subfiles if string in subfile][0]))

    # Recursivity stop condition
    if len(subdirs) == 0 and len(subfiles) == 0:
        pass
    # Look for files in all directories and subdirectories
    else:
        for i in subdirs:
            sort_by_string(current_path + "\\" + i, string, base_dir)


# Check if the directory passed as argument exist and ask to create it if it doesn't
if not os.path.isdir(sys.argv[1]):
    create = input("Folder does not exist, do you want to create it ? (yes/no)")
    if create == "yes":
        os.makedirs(sys.argv[1], exist_ok=True)
    else:
        exit()

print("Folder to build", sys.argv[1])
global dir_path
dir_path = sys.argv[1]

folder = os.path.basename(os.path.normpath(dir_path))
head, tail = os.path.split(os.path.normpath(dir_path))

id_dir = utils.get_subdirs(dir_path)
subfiles = utils.get_subfiles(dir_path)

for i in range(len(subfiles) - 1):
    if "data" in subfiles[i]:
        with open(dir_path + "\\" + subfiles[i], 'r') as stream:
            data_dict = yaml.safe_load(stream)
            if not data_dict.get("session_id"):
                id = data_dict.get("identifier")
            else:
                id = data_dict.get("session_id")
            stream.close()
            sort_by_string(dir_path, id, id_dir)



#
# region_list = ["a000", "a001", "a002"]
# region_dir = get_subdirs(dir_path)
# tmp_dir = dir_path
# for dir in id_dir:
#     dir_path = tmp_dir + "\\" + dir
#     for region in region_list:
#         sort_by_string(dir_path,region,region_dir)
#
# keyword_data = ["trace", "suite2p"]
# data_dir = get_subdirs(dir_path)
# dir_path = tmp_dir
# for id in id_list:
#     for dir in region_dir:
#         dir_path = tmp_dir + "\\" + id + "\\" + dir
#         for data in keyword_data:
#             sort_by_string(dir_path, data, data_dir)
#
