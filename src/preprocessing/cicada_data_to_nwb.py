import yaml
import os
import sys
import test_cicada_test_paul
import utils

"""
https://stackoverflow.com/questions/8790003/dynamically-import-a-method-in-a-file-from-a-string
importlib.import_module('abc.def.ghi.jkl.myfile.mymethod')

__import__ et exec sont plutôt pour Python2
"""


def load_nwb_from_data(dir_path):

    # Get all files and directories present in the path
    files = utils.get_subfiles(dir_path)
    dirs = utils.get_subdirs(dir_path)
    files = files + dirs

    # Open YAML file with keywords, extension and keywords to exclude if existing then dump all data in a dict
    if os.path.isfile(dir_path + "\\" + [subfile for subfile in files if "default" in subfile][0]):
        with open(dir_path + "\\" + [subfile for subfile in files if "default" in subfile][0], 'r') as stream:
            data = yaml.safe_load(stream)
        # Remove the file from the list of files and directories so it isn't found twice
        files.remove([subfile for subfile in files if "default" in subfile][0])
    else:
        data = None

    home_data = dict()
    # Look for another YAML file containing the keywords, extensions and keywords to exclude
    for file in files:
        if "yaml" not in file:
            continue
        # p is a placeholder until we know every yaml file name
        if "subject" not in file and "ophys" not in file and "data" not in file and "p" not in file:
            with open(dir_path + "\\" + file, 'r') as stream:
                home_data = yaml.safe_load(stream)

    # If 2 files are provided, the one given by the user will take the priority
    if data is not None:
        difference = set(list(data.keys())) - set(list(home_data.keys()))
        for i in list(difference):
            home_data[i] = data[i]
    # First we create the nwb file because it will be needed for everything
    converttonwb = home_data.pop("ConvertToNWB")

    filtered_list = []
    for i in converttonwb:
        # If no extension is provided it means we are looking for a directory, so we filter the list of files and
        # directory to only contain directories
        if not converttonwb[i].get("extension"):
            filtered_list = [file for file in files if "." not in file]
        # Filter the file list depending on the extension provided in the YAML file
        else:
            for extension in converttonwb[i].get("extension"):
                filtered_list.extend([file for file in files if extension in file])
            # print("Filter result : " + str(filtered_list) + " by extension : " + str(converttonwb[i].get("extension")))
        # Conditional loop to remove all files or directories not containing the keywords
        # or containing excluded keywords
        counter = 0
        while counter < len(filtered_list):
            delete = False
            for keyword in converttonwb[i].get("keyword"):
                if keyword not in filtered_list[counter]:
                    # print("Keyword not found in : " + str(filtered_list))
                    del filtered_list[counter]
                    # print("New list : " + str(filtered_list))
                    delete = True
            if not delete:
                for keyword_to_exclude in converttonwb[i].get("keyword_to_exclude"):
                    if keyword_to_exclude in filtered_list[counter]:
                        # print("Excluded keyword found in : " + str(filtered_list))
                        del filtered_list[counter]
                        # print("New list : " + str(filtered_list))
                        delete = True
            if not delete:
                counter += 1
        print("Files to pass for " + i + ": " + str(filtered_list))
        # If files were found respecting every element, add the whole path to pass them as arguments
        yaml_path = os.path.join(dir_path, filtered_list[0])

    nwb_file = test_cicada_test_paul.create_nwb_file(yaml_path)

    order_list = []
    if home_data.get("order"):
        order_list = home_data.pop("order")

    while order_list:
        next_class = order_list.pop(0)
        # Get classname then instantiate it
        classname = getattr(test_cicada_test_paul, next_class)
        converter = classname(nwb_file)
        # Initialize a dict to contain the arguments to call convert
        arg_dict = {}
        print("Class name : " + str(next_class))
        # Loop through all arguments of the convert of the corresponding class
        for j in home_data[next_class]:
            filtered_list = []
            # If value if found it means the argument is not a file but a string/int/etc
            if home_data[next_class][j].get("value") and not home_data[next_class][j].get("extension") and \
                    (not home_data[next_class][j].get("keyword") or not home_data[next_class][j].get("keyword_to_exclude")):
                print(home_data[next_class][j].get("value")[0])
                arg_dict[j] = home_data[next_class][j].get("value")[0]
            else:
                # If no extension is provided it means we are looking for a directory, so we filter the list of files and
                # directory to only contain directories
                if not home_data[next_class][j].get("extension"):
                    filtered_list = [file for file in files if "." not in file]
                # Filter the file list depending on the extension provided in the YAML file
                else:
                    for extension in home_data[next_class][j].get("extension"):
                        filtered_list.extend([file for file in files if extension in file])
                    # print("Filter result : " + str(filtered_list) + " by extension : " +
                    # str(home_data[i][j].get("extension")))

                # Conditional loop to remove all files or directories not containing the keywords
                # or containing excluded keywords
                counter = 0
                while counter < len(filtered_list):
                    delete = False
                    for keyword in home_data[next_class][j].get("keyword"):
                        if keyword not in filtered_list[counter]:
                            # print("Keyword not found in : " + str(filtered_list))
                            del filtered_list[counter]
                            # print("New list : " + str(filtered_list))
                            delete = True
                    if not delete:
                        for keyword_to_exclude in home_data[next_class][j].get("keyword_to_exclude"):
                            if keyword_to_exclude in filtered_list[counter]:
                                # print("Excluded keyword found in : " + str(filtered_list))
                                del filtered_list[counter]
                                # print("New list : " + str(filtered_list))
                                delete = True
                    if not delete:
                        counter += 1
                print("Files to pass for " + j + ": " + str(filtered_list))
                # If files were found respecting every element, add the whole path to pass them as arguments
                if filtered_list:
                    arg_dict[j] = os.path.join(dir_path, filtered_list[0])
                    if "mat" in home_data[next_class][j].get("extension") and home_data[next_class][j].get("value"):
                        arg_dict[j] = [arg_dict[j]] + list(home_data[next_class][j].get("value"))

                # If no file found, put the argument at None
                else:
                    arg_dict[j] = None
        # print("Arguments to pass : " + str(arg_dict))
        converter.convert(**arg_dict)
        # Delete once it's done
        del home_data[next_class]

    # Loop through all the remaining classes in the dict to instantiate them
    for i in home_data:
        # Get classname then instantiate it
        classname = getattr(test_cicada_test_paul, i)
        converter = classname(nwb_file)
        # Initialize a dict to contain the arguments to call convert
        arg_dict = {}
        print("Class name : " + str(i))
        # Loop through all arguments of the convert of the corresponding class
        for j in home_data[i]:
            filtered_list = []
            # If value if found it means the argument is not a file but a string/int/etc
            if home_data[i][j].get("value") and not home_data[i][j].get("extension") and \
                    (not home_data[i][j].get("keyword") or not home_data[i][j].get("keyword_to_exclude")):
                print(home_data[i][j].get("value")[0])
                arg_dict[j] = home_data[i][j].get("value")[0]
            else:
                # If no extension is provided it means we are looking for a directory, so we filter the list of files and
                # directory to only contain directories
                if not home_data[i][j].get("extension"):
                    filtered_list = [file for file in files if "." not in file]
                # Filter the file list depending on the extension provided in the YAML file
                else:
                    for extension in home_data[i][j].get("extension"):
                        filtered_list.extend([file for file in files if extension in file])
                    # print("Filter result : " + str(filtered_list) + " by extension : " +
                          # str(home_data[i][j].get("extension")))
                # Conditional loop to remove all files or directories not containing the keywords
                # or containing excluded keywords
                counter = 0
                while counter < len(filtered_list):
                    delete = False
                    for keyword in home_data[i][j].get("keyword"):
                        if keyword not in filtered_list[counter]:
                            # print("Keyword not found in : " + str(filtered_list))
                            del filtered_list[counter]
                            # print("New list : " + str(filtered_list))
                            delete = True
                    if not delete:
                        for keyword_to_exclude in home_data[i][j].get("keyword_to_exclude"):
                            if keyword_to_exclude in filtered_list[counter]:
                                # print("Excluded keyword found in : " + str(filtered_list))
                                del filtered_list[counter]
                                # print("New list : " + str(filtered_list))
                                delete = True
                    if not delete:
                        counter += 1
                print("Files to pass for " + j + ": " + str(filtered_list))
                # If files were found respecting every element, add the whole path to pass them as arguments
                if filtered_list:
                    arg_dict[j] = os.path.join(dir_path, filtered_list[0])
                    if "mat" in home_data[i][j].get("extension") and home_data[i][j].get("value"):
                        arg_dict[j] = [arg_dict[j]] + list(home_data[i][j].get("value"))

                # If no file found, put the argument at None
                else:
                    arg_dict[j] = None

        #print("Arguments to pass : " + str(arg_dict))
        converter.convert(**arg_dict)

    # Create NWB file in the data folder
    nwb_name = utils.path_leaf(dir_path) + ".nwb"
    with test_cicada_test_paul.NWBHDF5IO(os.path.join(dir_path, nwb_name), 'w') as io:
        io.write(nwb_file)

    print("NWB file created at : " + str(os.path.join(dir_path, nwb_name)))
