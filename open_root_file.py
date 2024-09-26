import numpy as np 
import uproot
import time
import os

def is_file_still_writing(file_path, interval=2):

    initial_size = os.path.getsize(file_path)

    time.sleep(interval)

    new_size = os.path.getsize(file_path)

    return initial_size != new_size


def store_data(file_path):

    run_data = np.array([])

    if is_file_still_writing(file_path, 2):
        print("File is still being written to. Exiting the function.")
        return

    DY_tree = uproot.open(file_path)["save;1"]

    detID = DY_tree["rawEvent/fAllHits/fAllHits.detectorID"].array(library="np")
    elemID = DY_tree["rawEvent/fAllHits/fAllHits.elementID"].array(library="np")
    drift = DY_tree["rawEvent/fAllHits/fAllHits.driftDistance"].array(library="np")

    run_data = np.array([detID, elemID, drift])

if __name__ == "__main__":
    store_data('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')
    print(store_data)






