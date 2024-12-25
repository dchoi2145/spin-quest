import uproot
from file_read import get_detector_info, read_events, choose_root, find_tree

# CONSTANTS
SPECTROMETER_INFO_PATH = "spectrometer.csv"

# read momentum values from root file
def read_momentum(file_path):
    with uproot.open(file_path) as file:
        # get tree 
        tree = find_tree(file)

        # get gpx, gpy, gpz
        keys = tree.keys() 
        if "gpx" not in keys or "gpy" not in keys or "gpz" not in keys:
            raise Exception("Momentum values missing from ROOT file.")
        
        momentum_arrays = tree.arrays(["gpx", "gpy", "gpz"], library="np")
    
    return momentum_arrays["gpx"], momentum_arrays["gpy"], momentum_arrays["gpz"]
    
if __name__ == "__main__":
    root_file = choose_root()
    print("Reading in hit matrix...")
    detector_ids, element_ids = read_events(root_file)
    print("Reading momentum matrices...")
    gpx, gpy, gpz = read_momentum(root_file)

    # process spectrometer file and get max detector/element id
    detector_name_to_id_elements = get_detector_info(SPECTROMETER_INFO_PATH)
    max_detector_id = max([detector_name_to_id_elements[name][0] for name in detector_name_to_id_elements])
    max_element_id = max([detector_name_to_id_elements[name][1] for name in detector_name_to_id_elements])

    # process root data into hit matrices
    