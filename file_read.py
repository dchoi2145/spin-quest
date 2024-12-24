import numpy as np 
import uproot
import time
import os
import json 

# Function for reading detector names from spectrometer CSV file
def get_detector_info(file_name):
    name_to_id_elements = dict()
    ids = set()
    max_elements = 0

    with open(file_name, 'r') as infile:
        # skip first line
        infile.readline()

        for line in infile.readlines():
            split_line = line.split(",")
            detector_id = int(split_line[0])
            detector_name = split_line[1]
            num_elements = int(split_line[2])
            max_elements = max(max_elements, num_elements)

            if detector_id not in ids:
                name_to_id_elements[detector_name] = [detector_id, num_elements, True]
                ids.add(detector_id)

    return name_to_id_elements, max_elements

# Function for reading json file
def read_json(file_name):
    with open(file_name, 'r') as infile:
        config = json.load(infile)

    return config

# Function that checks if a file is still has data being written into it
def is_file_still_writing(file_path, interval=0.1):
    # Checks the size of the file when the function is ran
    initial_size = os.path.getsize(file_path)

    # Waits desired time before checking the file size again
    time.sleep(interval)
    
    # Checks the size of the file after a desired duration
    new_size = os.path.getsize(file_path)

    # Returns False if the file size didn't change, and True if the file size did change
    return initial_size != new_size

# Function for finding first non-empty array
def find_first_non_empty(arr):
    for first_non_empty in range(len(arr)):
        if len(arr[first_non_empty]) > 0:
            return first_non_empty
        
    return -1

# Function for asking for user input
def choose_option(options):
    while True:
        response = input("Please select an option by number: ")
        if response.isnumeric():
            choice = int(response) - 1
            if choice >= 0 and choice < len(options):
                break
    
    return choice

# Function that reads events from ROOT file
def read_events(file_path):
    detector_ids = []
    element_ids = []

    with uproot.open(file_path) as file:
        # use user input to find tree
        tree_names = file.keys()
        if len(tree_names) == 0:
            raise Exception("No trees found in ROOT file.")
        
        print("Trees found in file: ")
        for i, tree_name in enumerate(tree_names, 1):
            print("{}. ".format(i) + tree_name)
        choice = choose_option(tree_names)
        
        # get tree 
        tree = file[tree_names[choice]]

        # get branches
        detector_id_branches, element_id_branches = [], []
        detector_id_choice, element_id_choice = 0, 0
        for key in tree.keys():
            if "detectorID" in key:
                detector_id_branches.append(key)
            if "elementID" in key:
                element_id_branches.append(key)

        # select specific branches if there are too many 
        if len(detector_id_branches) == 0 or len(element_id_branches) == 0:
            raise Exception("Error: Not enough branches found.")
        if len(detector_id_branches) > 1:
            print("More than 2 valid branches found for detectorID. Please select the one you want.")
            for i, branch in enumerate(detector_id_branches, 1):
                print("{}. ".format(i) + branch)
            detector_id_choice = choose_option(detector_id_branches)
        if len(element_id_branches) > 1:
            print("More than 2 valid branches found for elementID. Please select the one you want.")
            for i, branch in enumerate(element_id_branches, 1):
                print("{}. ".format(i) + branch)
            element_id_choice = choose_option(element_id_branches)

        # get detector and element ids 
        possible_detector_ids = tree.arrays(detector_id_branches, library="np")
        possible_element_ids = tree.arrays(element_id_branches, library="np")
        detector_ids = possible_detector_ids[detector_id_branches[detector_id_choice]]
        element_ids = possible_element_ids[element_id_branches[element_id_choice]]
    
    return detector_ids, element_ids

# Function for choosing which root file to read
def choose_root(directory="./root_files"):
    root_files = os.listdir(directory)
    if len(root_files) == 0:
        raise Exception("No root files found on system.")

    print("Root files found on system:")
    for i, file in enumerate(root_files, 1):
        print("{}. ".format(i) + file)

    choice = choose_option(root_files)

    return os.path.join(directory, root_files[choice])