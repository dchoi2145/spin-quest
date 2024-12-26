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
    # List of all .root files to process
    root_files = [
        "runs/trackQA1.root",
        "runs/trackQA2.root",
        "runs/trackQA3.root",
        "runs/trackQA4.root",
        "runs/trackQA5.root",
        "runs/trackQA6.root",
        "runs/trackQA7.root",
        "runs/trackQA8.root",
        "runs/trackQA9.root"
    ]

    all_detector_ids = []
    all_element_ids = []
    all_gpx = []
    all_gpy = []
    all_gpz = []

    # Loop through each file and aggregate data
    for root_file in root_files:
        print(f"Processing file: {root_file}")
        
        # Read detector and element IDs from the file
        detector_ids, element_ids = read_events(root_file)
        all_detector_ids.append(detector_ids)
        all_element_ids.append(element_ids)
        
        # Read momentum values from the file
        gpx, gpy, gpz = read_momentum(root_file)
        all_gpx.append(gpx)
        all_gpy.append(gpy)
        all_gpz.append(gpz)

    # Concatenate all the data
    print("Concatenating data...")
    all_detector_ids = np.concatenate(all_detector_ids)
    all_element_ids = np.concatenate(all_element_ids)
    all_gpx = np.concatenate(all_gpx)
    all_gpy = np.concatenate(all_gpy)
    all_gpz = np.concatenate(all_gpz)

    # process spectrometer file and get max detector/element id
    print("Processing spectrometer file...")
    detector_name_to_id_elements = get_detector_info(SPECTROMETER_INFO_PATH)
    max_detector_id = max([detector_name_to_id_elements[name][0] for name in detector_name_to_id_elements])
    max_element_id = max([detector_name_to_id_elements[name][1] for name in detector_name_to_id_elements])

    # filter out data beyond max detector id and max element id
    print("Filtering data...")
    all_detector_ids = np.where(all_detector_ids <= max_detector_id, all_detector_ids, 0)
    all_element_ids = np.where(all_element_ids <= max_element_id, all_element_ids, 0)

    # process root data into hit matrices\
    print("Converting to hit matrices...")
    hit_matrices = convert_to_hit_matrices(all_detector_ids, all_element_ids, max_detector_id, max_element_id)

    # process momentum lists into one big array (labels)
    print("Joining momentum arrays...")
    labels = join_momentum_arrays(all_gpx, all_gpy, all_gpz)

    # create and compile the TensorFlow model
    print("Creating model...")
    model = create_model()
    model_loss = tf.keras.losses.MeanSquaredError()
    model.compile(optimizer='adam', loss=model_loss, metrics=["mean_squared_error"])

    # train the model
    print("Training model...")
    model.fit(hit_matrices, labels, epochs=5)

    print("Training complete!")

    model_save_path = "models/hit_to_momentum_model.keras"
    model.save(model_save_path)
    print(f"Model saved at {model_save_path}")