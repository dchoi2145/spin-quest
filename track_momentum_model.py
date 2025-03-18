import uproot
import numpy as np
import tensorflow as tf
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler

# ------------------------------- #
#   GLOBAL SETTINGS & CONSTANTS   #
# ------------------------------- #

# Define a constant for the muon mass in GeV (approx 0.10566 GeV).
MUON_MASS = 0.10566  

# List of ROOT files to read in. Each file contains track QA information.
FILE_PATH = [
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/1/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/10/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/24/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/33/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/52/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/54/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/64/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/68/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/84/trackQA.root',
    '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/90/trackQA.root',
]

# Maximum number of unique (detector ID, element ID) values we expect.
# In this setup, we consider 100 possible detector IDs and 100 possible element IDs.
MAX_IDS = 100

# Directory where plots will be saved.
PLOTS_DIR = "residual_plots"


# ----------------------------- #
#         DATA LOADING          #
# ----------------------------- #

def load_data(file_paths):
    """
    Loads and merges data from multiple ROOT files using uproot.
    
    Args:
        file_paths (list of str): Paths to the ROOT files containing the data.

    Returns:
        dict: A dictionary with keys: 'detectorID', 'elementID', 'gpx', 'gpy', 'gpz', 'n_tracks'.
              Each entry in the dict is a 1D NumPy array concatenated across all input files.
    """
    # These are the branch names to extract from each ROOT file.
    branches = ["detectorID", "elementID", "gpx", "gpy", "gpz", "n_tracks"]
    
    # Prepare a dictionary to store the data arrays from each file. 
    # We store them in lists first, then we'll concatenate them at the end.
    all_data = {key: [] for key in branches}

    # Loop over each file in file_paths
    for file_path in file_paths:
        print(f"Loading data from: {file_path}")
        # Open the ROOT file using uproot
        with uproot.open(file_path) as file:
            # Access the tree named "QA_ana"
            tree = file["QA_ana"]
            # Extract the branches specified in 'branches'
            data = tree.arrays(branches, library="np")
            # Append each branch's data to our all_data dictionary
            for key in branches:
                all_data[key].append(data[key])

    # Concatenate all the arrays for each branch to form one large array
    merged_data = {key: np.concatenate(all_data[key]) for key in branches}
    
    return merged_data


# ----------------------------- #
#      TRACK SEGMENTATION       #
# ----------------------------- #

def build_track_segmentation_model(input_shape):
    """
    Creates a CNN model intended to classify a track ID out of 100 possible IDs.
    The input is expected to be a 2D "hit map" (detector ID vs. element ID) 
    shaped like (MAX_IDS x MAX_IDS x 1), which is fed into convolutional layers.
    
    Args:
        input_shape (tuple): Shape of the input data, e.g. (100, 100, 1).
    
    Returns:
        tf.keras.Model: A compiled CNN model using 'sparse_categorical_crossentropy' loss 
                        and 'accuracy' metric.
    """
    # Use a Sequential model with several convolution + pooling layers
    model = tf.keras.Sequential([
        # First Conv2D layer with 32 filters of size (3x3), ReLU activation, 
        # and input_shape set to (MAX_IDS, MAX_IDS, 1).
        tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2,2)),

        # Second Conv2D layer
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),

        # Third Conv2D layer
        tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
        
        # Flatten the final feature map to feed into Dense layers
        tf.keras.layers.Flatten(),

        # Fully connected layer with 256 neurons
        tf.keras.layers.Dense(256, activation='relu'),

        # Output layer with 100 units (one for each possible track ID), 
        # using softmax activation for classification.
        tf.keras.layers.Dense(MAX_IDS, activation='softmax')
    ])

    # Compile the model with the Adam optimizer and a sparse categorical crossentropy loss.
    # 'sparse_categorical_crossentropy' is used because the labels for track ID 
    # will be integer indices in the range [0..99].
    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])
    return model


def predict_trackwise_data(detector_ids, element_ids, n_tracks, max_ids, model):
    """
    Uses a trained CNN model to predict the track ID distribution for each event.
    This function creates a sparse hit map (max_ids x max_ids) for each event, 
    runs it through the model, and collects the probabilities.
    
    Args:
        detector_ids (array-like): List/array of arrays, each sub-array containing 
                                   the detector IDs hit in an event.
        element_ids (array-like):  List/array of arrays, each sub-array containing 
                                   the element IDs hit in an event.
        n_tracks (array-like):     Not directly used here, but could be used for 
                                   more advanced logic.
        max_ids (int):             Maximum ID value for both detectors and elements (100).
        model (tf.keras.Model):    The trained CNN model that outputs track assignment 
                                   probabilities.
    
    Returns:
        np.ndarray: A 2D numpy array of shape (num_events, 100), where each row is 
                    the probability distribution over the 100 track IDs.
    """
    track_hit_matrices = []
    num_events = len(detector_ids)

    # Loop over each event
    for evt_index in range(num_events):
        # Create a sparse matrix of shape (max_ids, max_ids). 
        # We'll fill in '1' if a given (detectorID, elementID) is hit.
        mat = csr_matrix((max_ids, max_ids), dtype=np.float32)
        for d, e in zip(detector_ids[evt_index], element_ids[evt_index]):
            # Only fill if IDs are within [1..max_ids]
            if 0 < d <= max_ids and 0 < e <= max_ids:
                mat[d - 1, e - 1] = 1

        # Reshape the (max_ids x max_ids) array to (1, max_ids, max_ids, 1) for CNN input
        input_data = mat.toarray().reshape(1, max_ids, max_ids, 1)
        
        # Model predicts a distribution of shape (1, 100). 
        # We take [0] to get the 1D distribution of shape (100,).
        predicted_tracks = model.predict(input_data)[0]
        
        track_hit_matrices.append(predicted_tracks)

    # Convert list of predictions to a NumPy array of shape (num_events, 100)
    return np.array(track_hit_matrices, dtype=np.float32)


# ----------------------------- #
#   MOMENTUM PREDICTION MODEL   #
# ----------------------------- #

def build_momentum_model(input_dim, output_dim=4):
    """
    Builds a fully connected neural network to predict momentum components.
    
    Args:
        input_dim (int):  Dimensionality of the input features (e.g., 4 if we feed [px, py, pz, E]).
        output_dim (int): Number of output variables (default 4 for [px, py, pz, E]).

    Returns:
        tf.keras.Model: A compiled Keras model with MSE loss and Adam optimizer.
    """
    # Simple feedforward network
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        # Final layer outputs 4 values: px, py, pz, E
        tf.keras.layers.Dense(output_dim)
    ])
    
    # Compile with Adam optimizer, learning rate = 1e-3, using MSE loss and MSE metric.
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                  loss='mse',
                  metrics=['mse'])
    return model


# ----------------------------- #
#   PLOTTING HELPER FUNCTIONS   #
# ----------------------------- #

def plot_track_assignments(track_predictions, output_dir):
    """
    Plots a histogram of the most likely track ID per event.
    
    Args:
        track_predictions (np.ndarray): 2D array of shape (num_events, 100) 
                                        with probability distributions.
        output_dir (str): Directory where the plot will be saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Find the most probable track ID by taking the argmax across the 100 classes
    assigned_labels = np.argmax(track_predictions, axis=1)

    # Create a histogram of assigned_labels
    plt.figure(figsize=(10, 6))
    plt.hist(assigned_labels, bins=range(MAX_IDS+1), color='blue', alpha=0.7)
    plt.title("Predicted Track Assignments")
    plt.xlabel("Track ID")
    plt.ylabel("Count")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "track_assignment_histogram.png"))
    plt.close()


def plot_residuals(predicted, true, output_dir):
    """
    Creates histograms for the residuals of each momentum component ([px, py, pz, E]).
    
    Args:
        predicted (np.ndarray): Predicted momentum values of shape (N,4).
        true (np.ndarray):     True momentum values of shape (N,4).
        output_dir (str):      Directory where the plots will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Compute residual = predicted - true
    residuals = predicted - true
    components = ['px', 'py', 'pz', 'E']

    # Loop over the four momentum components
    for i, comp in enumerate(components):
        plt.figure(figsize=(10, 6))
        plt.hist(residuals[:, i], bins=50, color='blue', alpha=0.7)
        plt.axvline(0, color='k', linestyle='dashed', linewidth=1)
        plt.title(f'Residuals for {comp}')
        plt.xlabel('Residual Value')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, f'residual_{comp}.png'))
        plt.close()


# ----------------------------- #
#           MAIN FLOW           #
# ----------------------------- #

def main():
    """
    Main function orchestrating the following steps:
    
    1) Data Loading: 
       - Read multiple ROOT files containing track QA info.
       - Merge them into a single dataset.
    
    2) Track Image Preparation:
       - Construct a (MAX_IDS x MAX_IDS) 'hit map' for each event using detectorID and elementID. 
       - This map is used as an image input to a CNN.
    
    3) Track Segmentation CNN:
       - Build a CNN that classifies which 'row' (track ID) has the largest sum of hits.
         (Naive labeling for demonstration.)
       - Train the CNN on the entire dataset (with a naive label derived from row sums).
       - Use the trained CNN to predict track ID assignments for each event.
       - Plot the distribution of assigned track IDs.
    
    4) Momentum Prediction Model:
       - Build a simple feedforward network to learn [px, py, pz, E] from some input features.
       - For demonstration, we feed the network the actual [px, py, pz, E] as inputs,
         effectively teaching it the identity function.
       - Plot the residuals between predicted and true momenta.

    5) Save all relevant plots to disk.
    """
    # Step 1: Data loading
    print("Loading data...")
    data = load_data(FILE_PATH)

    # Prepare arrays for convenience
    detector_ids = data['detectorID']
    element_ids = data['elementID']
    n_tracks    = data['n_tracks']

    # Step 2: Construct track 'hit maps'
    print("Preparing track hit matrices...")
    track_hit_list = []
    num_events = len(detector_ids)
    for evt_index in range(num_events):
        # Create a sparse matrix to fill with hits
        mat = csr_matrix((MAX_IDS, MAX_IDS), dtype=np.float32)
        for d, e in zip(detector_ids[evt_index], element_ids[evt_index]):
            if 0 < d <= MAX_IDS and 0 < e <= MAX_IDS:
                mat[d - 1, e - 1] = 1
        # Convert to a dense array and store
        track_hit_list.append(mat.toarray())

    # Reshape into (num_events, MAX_IDS, MAX_IDS, 1) for CNN input
    track_hit_matrices = np.array(track_hit_list).reshape(num_events, MAX_IDS, MAX_IDS, 1)

    # Step 3: Build & train the CNN for track segmentation
    print("Building and training CNN model for track segmentation...")
    cnn_model = build_track_segmentation_model(input_shape=(MAX_IDS, MAX_IDS, 1))

    # For demonstration, define the label as the row with the largest sum of hits in the matrix.
    # This is naive but serves as a quick example.
    squeezed = track_hit_matrices[..., 0]        # shape (N, 100, 100), ignoring the last dimension
    row_sums = squeezed.sum(axis=2)             # sum over the elementID axis => shape (N, 100)
    track_labels = np.argmax(row_sums, axis=1)  # find the row index with the max sum => shape (N,)

    # Train the CNN
    cnn_model.fit(
        track_hit_matrices,
        track_labels,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )

    # Predict track assignments on the entire dataset
    print("Predicting track assignments...")
    track_predictions = predict_trackwise_data(detector_ids, element_ids, n_tracks, MAX_IDS, cnn_model)

    # Plot and save track assignment histogram
    plot_track_assignments(track_predictions, PLOTS_DIR)
    print("Track assignment prediction completed!")

    # Step 4: Build & train a momentum model using the first track's true momentum
    print("Extracting true momenta (px, py, pz, E)...")
    # We assume the first element in gpx, gpy, gpz arrays correspond to the primary track of interest.
    px = np.array([evt[0] for evt in data['gpx']])
    py = np.array([evt[0] for evt in data['gpy']])
    pz = np.array([evt[0] for evt in data['gpz']])

    # Compute energy from momentum and known muon mass
    # E^2 = p^2 + m^2
    E  = np.sqrt(px**2 + py**2 + pz**2 + MUON_MASS**2)

    # Combine [px, py, pz, E] into a single 2D array of shape (N, 4)
    y_true = np.vstack([px, py, pz, E]).T

    # For demonstration, we'll feed the actual [px,py,pz,E] to the model 
    # (i.e., learning the identity mapping).
    X_raw = y_true.copy()

    # Scale the features before training for numerical stability
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # Build the fully connected momentum model
    momentum_model = build_momentum_model(input_dim=4, output_dim=4)

    # Train it to predict the same [px, py, pz, E]
    momentum_model.fit(
        X_scaled, y_true,
        epochs=10,
        batch_size=64,
        validation_split=0.2
    )

    # Generate predictions
    y_pred = momentum_model.predict(X_scaled)

    # Plot residuals of px, py, pz, E
    plot_residuals(y_pred, y_true, PLOTS_DIR)
    print("Momentum residual plots saved!")

    print("All done!")


# If this script is run directly, execute main()
if __name__ == "__main__":
    main()
