import yaml
import os
import sys
import importlib
from test_cicada import *

# TODO : Commenter

dir_path = sys.argv[1]

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

files = get_subfiles(dir_path)
dirs = get_subdirs(dir_path)
files = files + dirs
for file in files:
    if "yaml" not in file:
        continue
    # TODO : Identifier le bon yaml mieux que ça
    if "subject" not in file and "ophys" not in file and "data" not in file and "p" not in file:

        with open(dir_path + "\\" + file, 'r') as stream:
            home_data = yaml.safe_load(stream)

# Open YAML file with metadata if existing then dump all data in a dict
if os.path.isfile(dir_path + "\\" + "default.yaml"):
    with open(dir_path + "\\" + "default.yaml", 'r') as stream:
        data = yaml.safe_load(stream)
    files.remove("default.yaml")
    if data is not None:
        difference = set(list(data.keys())) - set(list(home_data.keys()))
        for i in list(difference):
            home_data[i] = data[i]

# TODO : A changer avec le code de Julien car pour le moment ca va chercher le yaml codé en dur dans son code

ok = home_data.pop("ConvertToNWB")

# TODO : Fonction test = couper collé de la partie qui crée le NWB file dans le code de Julien --> A changer

nwb_file = test()


for i in home_data:
    # TODO : Chercher si il existe pas quelque chose de mieux qu'eval car dangereux
    converter = eval(i+"(nwb_file)")
    arg_dict = {}
    print("Class name : " + str(i))
    for j in home_data[i]:
        # TODO : Meilleur manière pour gérer les arguments qui ne sont pas des chemins
        if j == "format":
            continue
        # print(i,j)
        counter = 0
        print(type(home_data[i][j]), home_data[i][j])
        if not home_data[i][j].get("extension"):
            filtered_list = [file for file in files if "." not in file]
        else :
            for extension in home_data[i][j].get("extension"):
                filtered_list = [file for file in files if extension in file]
                print("Filter result : " + str(filtered_list) + " by extension : " + str(extension))
        while counter < len(filtered_list):
            delete = False
            for keyword in home_data[i][j].get("keyword"):
                if keyword not in filtered_list[counter]:
                    print("Keyword not found in : " + str(filtered_list))
                    del filtered_list[counter]
                    print("New list : " + str(filtered_list))
                    delete = True
            if not delete:
                for keyword_to_exclude in home_data[i][j].get("keyword_to_exclude"):
                    if keyword_to_exclude in filtered_list[counter]:
                        print("Excluded keyword found in : " + str(filtered_list))
                        del filtered_list[counter]
                        print("New list : " + str(filtered_list))
                        delete = True
            if not delete:
                counter += 1
        print("Files to pass : " + str(filtered_list))
        if filtered_list:
            arg_dict[j] = os.path.join(dir_path, filtered_list[0])
        else:
            arg_dict[j] = None
    if i == "ConvertCIMovieToNWB":
        arg_dict["format"] = "tiff"

    print("Arguments to pass : " + str(arg_dict))
    converter.convert(**arg_dict)





