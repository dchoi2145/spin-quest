import numpy as np 
import uproot
import time
import os

# Function that checks if a file is still has data being written into it
def is_file_still_writing(file_path, interval=2):
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

    # Checks to see if the file size has changed in the last 2 seconds to make sure that the file is not being written into
    if is_file_still_writing(file_path, 2):
        print("File is still being written to. Exiting the function.")
        # If the file is currently being written into, exit the function
        return

    # Open the Root file
    DY_tree = uproot.open(file_path)["save;1"]
    
    # Store these values into the variables so we can put them into the Array
    detID = DY_tree["rawEvent/fAllHits/fAllHits.detectorID"].array(library="np")
    elemID = DY_tree["rawEvent/fAllHits/fAllHits.elementID"].array(library="np")
    drift = DY_tree["rawEvent/fAllHits/fAllHits.driftDistance"].array(library="np")

    # Store these values into the NumPy Array that we created earlier
    run_data = np.array([detID, elemID, drift])

# Function that reads event data from a ROOT file
def read_event(file_path, event_number):
    # Open the ROOT file and access the relevant tree
    file = uproot.open(file_path + ":save")

    # Get the array of detector IDs for the given event number
    detector_id = file["fAllHits.detectorID"].array(library="np")[event_number]

    # Get the array of element IDs for the given event number
    element_id = file["fAllHits.elementID"].array(library="np")[event_number]

    # Initialize lists to store hits
    hits_detector_ids = []
    hits_element_ids = []

    # Iterate over unique detectors in the current event
    for detector in np.unique(detector_id):
        # Get the elements for this specific detector
        elements_for_detector = element_id[detector_id == detector]

        # Iterate over elements actually recorded for this detector
        for element in elements_for_detector:
            # Since each element in 'elements_for_detector' is part of a hit, we log it as a hit
            hits_detector_ids.append(detector)
            hits_element_ids.append(element)
            print(f"Hit detected for detector ID {detector} at element {element}")

    # Manually close the file
    file.close()

    # Convert lists to numpy arrays for returning
    hits_detector_ids = np.array(hits_detector_ids)
    hits_element_ids = np.array(hits_element_ids)

    # Return both arrays: detected hits for detector IDs and element IDs
    return hits_detector_ids, hits_element_ids

def get_total_spills(file_path):
    # Open the ROOT file and access the relevant tree
    file = uproot.open(file_path)
    tree = file["save"]  # Replace "save" with the actual tree name if different

    # Get the number of entries in the tree
    total_spills = tree.num_entries

    # Close the file
    file.close()

    return total_spills


if __name__ == "__main__":
    # store_data('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')
    #print(store_data)
    
    # Call the read_event function, passing the file path and event number
    file_path = '~/Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root'

    event_number = 1

    # Read and print the event data
    detector_id, element_id = read_event(file_path, event_number)
    print(f"Processed Event Number {event_number}")
    print(f"Detector IDs: {detector_id}")
    print(f"Element IDs: {element_id}")
