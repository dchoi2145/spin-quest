import numpy as np 
import uproot
import time
import os

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


def store_data(file_path):
    # Creates NumPy Array that will store the data we are looking for
    run_data = np.array([])

    # make sure the file is not being written into
    while is_file_still_writing(file_path, 0.1):
        print("File is still being written to. Exiting the function.")

    # Open the Root file
    DY_tree = uproot.open(file_path)["save;1"]
    
    # Store these values into the variables so we can put them into the Array
    detID = DY_tree["rawEvent/fAllHits/fAllHits.detectorID"].array(library="np")
    elemID = DY_tree["rawEvent/fAllHits/fAllHits.elementID"].array(library="np")
    drift = DY_tree["rawEvent/fAllHits/fAllHits.driftDistance"].array(library="np")

    # Store these values into the NumPy Array that we created earlier
    run_data = np.array([detID, elemID, drift])

# Function that reads event data from a ROOT file
def read_event(file, event_number, quick_check=False):
    # Adjust event_number to zero-based indexing
    entry_number = event_number - 1

    # Access the relevant tree
    tree = file["save"]  # Adjust 'save' to match your tree name if different

    # Define the branches to read
    branches = ["fAllHits.detectorID", "fAllHits.elementID"]

    # Use uproot's arrays method to read only the desired entry
    data = tree.arrays(branches, entry_start=entry_number, entry_stop=entry_number + 1, library="np")

    # Extract the arrays for this event
    detector_id = data["fAllHits.detectorID"][0]
    element_id = data["fAllHits.elementID"][0]

    # Check if data is present for quick_check
    if quick_check:
        has_data = len(detector_id) > 0
        return has_data, None, None

    # Return the detector IDs and element IDs directly
    return None, detector_id, element_id

def get_total_spills(file_path):
    with uproot.open(file_path) as file:
        tree = file["save"]  # Adjust 'save' to match your tree name if different
        return tree.num_entries


# Function that reads event data from a ROOT file
def get_total_detectors(file_path, event_number):
    # Open the ROOT file and access the relevant tree
    file = uproot.open(file_path + ":save")

    # Get the array of detector IDs for the given event number
    detector_id = file["fAllHits.detectorID"].array(library="np")[event_number]
    # Get the array of element IDs for the given event number
    element_id = file["fAllHits.elementID"].array(library="np")[event_number]

    # Initialize lists to store hits
    hits_detector_ids = []

    # Iterate over unique detectors in the current event
    for detector in np.unique(detector_id):
        # Get the elements for this specific detector
        elements_for_detector = element_id[detector_id == detector]

        # Iterate over elements actually recorded for this detector
        for element in elements_for_detector:
            # Since each element in 'elements_for_detector' is part of a hit, we log it as a hit
            hits_detector_ids.append(detector)
    return len(hits_detector_ids)

# Function that reads event data from a ROOT file
def get_total_elements(file_path, event_number):
    # Open the ROOT file and access the relevant tree
    file = uproot.open(file_path + ":save")

    # Get the array of detector IDs for the given event number
    detector_id = file["fAllHits.detectorID"].array(library="np")[event_number]
    # Get the array of element IDs for the given event number
    element_id = file["fAllHits.elementID"].array(library="np")[event_number]

    # Initialize lists to store hits
    hits_element_ids = np.array(element_id)

    for detector in np.unique(detector_id):
        # Get the elements for this specific detector
        elements_for_detector = element_id[detector_id == detector]

        # Iterate over elements actually recorded for this detector
        for element in elements_for_detector:
            # Since each element in 'elements_for_detector' is part of a hit, we log it as a hit
            hits_element_ids.append(element)
    return len(hits_element_ids)

def find_first_event_with_data(file_path, starting_event=1):
    total_events = get_total_spills(file_path)
    with uproot.open(file_path) as file:
        for event_number in range(starting_event, total_events + 1):
            has_data, _, _ = read_event(file, event_number, quick_check=True)
            if has_data:
                return event_number
    return None  # Return None if no event with data is found

if __name__ == "__main__":
    # store_data('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')
    #print(store_data)
    
    # Call the read_event function, passing the file path and event number
    file_path = 'D:\Documents\GitHub\spin-quest\run_data\run_005591\run_005591_spill_001903474_sraw.root'


    event_number = 300

    DY_tree = uproot.open('D:\Documents\GitHub\spin-quest\run_data\run_005591\run_005591_spill_001903474_sraw.root')["save;1"]
    print("Branches:", DY_tree.keys())

    # Read and print the event data
    #detector_id, element_id = read_event(file_path, event_number)
    #print(f"Processed Event Number {event_number}")
    #print(f"Detector IDs: {detector_id}")
    #print(f"Element IDs: {element_id}")
