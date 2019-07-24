import os
import sys
import ntpath

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