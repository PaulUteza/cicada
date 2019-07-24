import yaml
import os
import sys
import test_cicada_test_paul
import utils


# Pass path to files when calling the script
dir_path = sys.argv[1]

# Get all files and directories present in the path
files = utils.get_subfiles(dir_path)
dirs = utils.get_subdirs(dir_path)
files = files + dirs


# Open YAML file with keywords, extension and keywords to exclude if existing then dump all data in a dict
if os.path.isfile(dir_path + "\\" + "default.yaml"):
    with open(dir_path + "\\" + "default.yaml", 'r') as stream:
        data = yaml.safe_load(stream)
    # Remove the file from the list of files and directories so it isn't found twice
    files.remove("default.yaml")
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
        print("Filter result : " + str(filtered_list) + " by extension : " + str(converttonwb[i].get("extension")))
    # Conditional loop to remove all files or directories not containing the keywords
    # or containing excluded keywords
    counter = 0
    while counter < len(filtered_list):
        delete = False
        for keyword in converttonwb[i].get("keyword"):
            if keyword not in filtered_list[counter]:
                print("Keyword not found in : " + str(filtered_list))
                del filtered_list[counter]
                print("New list : " + str(filtered_list))
                delete = True
        if not delete:
            for keyword_to_exclude in converttonwb[i].get("keyword_to_exclude"):
                if keyword_to_exclude in filtered_list[counter]:
                    print("Excluded keyword found in : " + str(filtered_list))
                    del filtered_list[counter]
                    print("New list : " + str(filtered_list))
                    delete = True
        if not delete:
            counter += 1
    print("Files to pass : " + str(filtered_list))
    # If files were found respecting every element, add the whole path to pass them as arguments
    yaml_path = os.path.join(dir_path, filtered_list[0])

nwb_file = test_cicada_test_paul.create_nwb_file(yaml_path)
# Loop through all the classes in the dict to instantiate them
for i in sorted(home_data):
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
        if home_data[i][j].get("value"):
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
                print("Filter result : " + str(filtered_list) + " by extension : " +
                      str(home_data[i][j].get("extension")))
            # Conditional loop to remove all files or directories not containing the keywords
            # or containing excluded keywords
            counter = 0
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
            # If files were found respecting every element, add the whole path to pass them as arguments
            if filtered_list:
                arg_dict[j] = os.path.join(dir_path, filtered_list[0])

            # If no file found, put the argument at None
            else:
                arg_dict[j] = None

    print("Arguments to pass : " + str(arg_dict))
    converter.convert(**arg_dict)

# Create NWB file in the data folder
with test_cicada_test_paul.NWBHDF5IO(os.path.join(dir_path, 'ophys_example.nwb'), 'w') as io:
    io.write(nwb_file)

print("NWB file created at : " + str(os.path.join(dir_path, 'ophys_example.nwb')))