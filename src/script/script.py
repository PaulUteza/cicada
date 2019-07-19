import sys
import os
import re

def get_subdirs(current_path):
    
    # Get all directories in the last directory of the path
    # with depth=1
    subdirs = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        subdirs.extend(dirnames)
        break
    return subdirs

def get_subfiles(current_path):
    # Get all files in the last directory of the path
    # with depth=1
    subfiles = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        subfiles.extend(filenames)
        break
    return subfiles


def sort_by_string(current_path, string, base_dir):
    # Sort all files in the corresponding directory

    subdirs = get_subdirs(current_path)
    subfiles = get_subfiles(current_path)

    # If directory doesn't exist, create it
    if True in [string in subfile for subfile in subfiles] and True not in [string in subdir for subdir in dir_path]:

        os.makedirs(dir_path + "\\" + string, exist_ok=True)
        subdirs.append(string)
        base_dir.append(string)

    # Move file to corresponding directory depending on a key in the file name
    while True in [string in subfile for subfile in subfiles]:

        os.replace(current_path + "\\" + str([subfile for subfile in subfiles if string in subfile][0]),
                   dir_path + "\\" + string + "\\" +str([subfile for subfile in subfiles if string in subfile][0]))
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

# TODO : identifier par ID
folder = os.path.basename(os.path.normpath(dir_path))
head,tail = os.path.split(os.path.normpath(dir_path))

if folder != "id":
    os.replace(dir_path,head + "\\id")
    print("Renamed directory to " + str(head) + "\\id")
    dir_path = str(head)+"\\id"


region_list = ["a000","a001","a002"]
region_dir = get_subdirs(dir_path)

for region in region_list:
    sort_by_string(dir_path,region,region_dir)

keyword_data = ["trace","suite2p"]
data_dir = get_subdirs(dir_path)
tmp_dir = dir_path
for dir in region_dir:
    dir_path = tmp_dir + "\\" + dir
    for data in keyword_data:
        sort_by_string(dir_path,data,data_dir)

