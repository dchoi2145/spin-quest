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

# Function that reads events from ROOT file
def read_events(file_path):
    detector_ids = []
    element_ids = []
    with uproot.open(file_path) as file:
        # get tree 
        tree = file["QA_ana;1"]

        # get branches
        branches = ["detectorID", "elementID"]

        # get detector and element ids 
        data = tree.arrays(branches, library="np")
        detector_ids = data[branches[0]]
        element_ids = data[branches[1]]
    
    return detector_ids, element_ids

# Function for choosing which root file to read
def choose_root(directory="./root_files"):
    root_files = os.listdir(directory)
    if len(root_files) == 0:
        raise Exception("No root files found on system.")

    print("Root files found on system:")
    for i, file in enumerate(root_files, 1):
        print("{}. ".format(i) + file)

    while True:
        response = input("Please select a file by number: ")
        if response.isnumeric():
            choice = int(response) - 1
            if choice >= 0 and choice < len(root_files):
                break

    return os.path.join(directory, root_files[choice])