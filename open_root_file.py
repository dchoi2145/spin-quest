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
    # Open the ROOT file
    file = uproot.open(file_path + ":save")

    # Print the number of events during run
    print(len(file["fAllHits.detectorID"].array(library="np")))

    # Get the array of detector IDs for the given event number
    detectorid = file["fAllHits.detectorID"].array(library="np")[event_number]

    # Get the array of element IDs for the given event number
    elementid = file["fAllHits.elementID"].array(library="np")[event_number]

    # Manually close the file
    file.close()

    # Return both arrays: detector IDs and element IDs
    return detectorid, elementid


if __name__ == "__main__":
    # store_data('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')
    #print(store_data)
    
    # Call the read_event function, passing the file path and event number
    file_path = 'Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root'
    event_number = 3000

    # Read and print the event data
    detectorid, elementid = read_event(file_path, event_number)
    print(f"Detector IDs: {detectorid}")
    print(f"Element IDs: {elementid}")


    
        








