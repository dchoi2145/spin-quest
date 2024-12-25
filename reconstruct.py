import uproot
import tensorflow as tf 
import numpy as np 
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
    
# convert detector and element id matrices into hit matrices
def convert_to_hit_matrices(detector_events, element_events, max_detector_id, max_element_id):
    num_events = detector_events.shape[0]
    print(num_events)
    hit_matrices = np.zeros((num_events, max_detector_id, max_element_id), dtype=int)

    for event_idx in range(num_events):
        detectors = detector_events[event_idx] - 1  # convert to 0-indexed
        elements = element_events[event_idx] - 1 
        hit_matrices[event_idx, detectors, elements] = 1

    return hit_matrices

# create tensorflow model for training on hit data
def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(6)
    ])

    return model

def join_momentum_arrays(gpx, gpy, gpz):
    joined_events = []
    for px, py, pz in zip(gpx, gpy, gpz):
        joined_event = np.concatenate((px, py, pz))
        joined_events.append(joined_event)
    return np.array(joined_events)

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

    # filter out data beyond max detector id and max element id
    detector_ids = np.where(detector_ids <= max_detector_id, detector_ids, 0) 
    element_ids = np.where(element_ids <= max_element_id, element_ids, 0)

    # process root data into hit matrices\
    hit_matrices = convert_to_hit_matrices(detector_ids, element_ids, max_detector_id, max_element_id)

    # process momentum lists into one big array
    labels = join_momentum_arrays(gpx, gpy, gpz)

    # create DNN
    model = create_model()
    model_loss = tf.keras.losses.MeanSquaredError()
    model.compile(optimizer='adam', loss=model_loss, metrics=["mean_squared_error"])

    # train DNN
    model.fit(hit_matrices, labels, epochs=5)