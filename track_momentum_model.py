import uproot
import numpy as np
import tensorflow as tf
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
import os

# NEW: For scaling
from sklearn.preprocessing import StandardScaler

# Muon mass in GeV (adjust if needed)
MUON_MASS = 0.10566  # Adding mass of muon for calculating E

# Constants
FILE_PATH = r"C:\Users\dchoi\Documents\GitHub\spin-quest\runs\trackQA1.root"  
OUTPUT_FILE = "processed_data_per_track.npz"  # File where processed data will be saved
MAX_IDS = 100  # Max value for detector and element IDs
PLOTS_DIR = "residual_plots"  # Directory to save residual plots

def load_data(file_path):
    # Function to load data from the ROOT file using uproot
    # Extracting only the required branches to save memory and processing time
    branches = ["detectorID", "elementID", "gpx", "gpy", "gpz", "n_tracks"]
    with uproot.open(file_path) as file:
        tree = file["QA_ana"]  # The tree we are working with
        data = tree.arrays(branches, library="np")
    return data

# This function splits data from each event into tracks. For each track, it creates:
# A sparse hit matrix (detector vs. element) and Average momentum values (px, py, pz) and energy (E).
def create_trackwise_data(detector_ids, element_ids, n_tracks, gpx, gpy, gpz, max_ids):

    track_hit_matrices = []  # List to hold matrices of hits for each track
    track_momenta = []  # List to hold momenta for each track

    num_events = len(detector_ids)  # Number of events in the dataset

    for evt_index in range(num_events):
        # Extracting data for the current event
        event_det = detector_ids[evt_index]  # detector IDs for the event
        event_elem = element_ids[evt_index]  # element IDs for the event
        num_tracks = n_tracks[evt_index]  # number of tracks in the event
        event_gpx = gpx[evt_index]  # x-component of momentum
        event_gpy = gpy[evt_index]  # y-component of momentum
        event_gpz = gpz[evt_index]  # z-component of momentum

        # Handle cases where there are no tracks by treating the whole event as one track
        hits_per_track = len(event_det) // num_tracks if num_tracks > 0 else len(event_det)

        for t in range(num_tracks):
            # Slicing hits for the current track
            start_idx = t * hits_per_track
            end_idx = (t + 1) * hits_per_track

            # Skip empty or invalid slices
            if end_idx <= start_idx:
                continue

            det_for_t = event_det[start_idx:end_idx]
            elem_for_t = event_elem[start_idx:end_idx]
            if len(det_for_t) == 0:
                continue

            # Create a sparse matrix to represent hits
            mat = csr_matrix((max_ids, max_ids), dtype=np.float32)
            for d, e in zip(det_for_t, elem_for_t):
                if 0 < d <= max_ids and 0 < e <= max_ids:
                    mat[d - 1, e - 1] = 1

            # Calculate average px, py, pz for the current track
            px_slice = event_gpx[start_idx:end_idx]
            py_slice = event_gpy[start_idx:end_idx]
            pz_slice = event_gpz[start_idx:end_idx]
            if len(px_slice) == 0:
                continue

            px_avg = np.mean(px_slice)
            py_avg = np.mean(py_slice)
            pz_avg = np.mean(pz_slice)

            # Skip if the averages are NaN
            if np.isnan(px_avg) or np.isnan(py_avg) or np.isnan(pz_avg):
                continue

            # Compute energy (E) using the muon mass and momentum components
            p_sq = px_avg**2 + py_avg**2 + pz_avg**2
            E = np.sqrt(p_sq + MUON_MASS**2)

            # Add to the lists
            track_hit_matrices.append(mat)
            track_momenta.append([px_avg, py_avg, pz_avg, E])  # Store 4-momentum

    return track_hit_matrices, np.array(track_momenta, dtype=np.float32)

# Create a neural network to predict 4 outputs: px, py, pz, E.
def build_momentum_model(input_dim, output_dim=4):
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(input_dim,)),  # Input layer
        tf.keras.layers.Dense(256, activation='relu'),  # Hidden layer with 256 units
        tf.keras.layers.Dense(128, activation='relu'),  # Another hidden layer
        tf.keras.layers.Dense(64, activation='relu'),  # Another hidden layer
        tf.keras.layers.Dense(output_dim)  # Output layer: 4 values (px, py, pz, E)
    ])
    # Compile the model with MSE as the loss function
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                  loss='mse', metrics=['mse'])
    return model

# Plot residual histograms for each component: px, py, pz, and E.
# Residuals are calculated as (predicted - true).
def plot_residuals(predicted, true, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    residuals = predicted - true  # Calculate residuals
    components = ['px', 'py', 'pz', 'E']  # Names of the components

    for i, component in enumerate(components):
        plt.figure(figsize=(10, 6))
        col_data = residuals[:, i]
        col_data = col_data[~np.isnan(col_data)]  # Remove NaNs
        if len(col_data) == 0:
            print(f"All NaN or no data for {component}, skipping plot.")
            plt.close()
            continue

        plt.hist(col_data, bins=50, color='blue', alpha=0.7, label=f'Residuals for {component}')
        plt.axvline(0, color='k', linestyle='dashed', linewidth=1, label='Zero Residual')

        plt.title(f'Residuals for {component}')
        plt.xlabel('Residual Value')
        plt.ylabel('Frequency')
        plt.legend(loc='upper right')
        plt.grid(True)

        plot_path = os.path.join(output_dir, f'residual_{component}.png')
        plt.savefig(plot_path)  # Save the plot
        plt.close()

    print(f"Residual plots saved in '{output_dir}'.")

def main():
    print("Loading data from the file...")
    data = load_data(FILE_PATH)

    # Check for NaNs or empty branches in the data
    for key, value in data.items():
        try:
            has_nans = np.isnan(value).any() if np.issubdtype(value.dtype, np.number) else False
        except Exception as e:
            has_nans = f"Error: {e}"
        is_empty = (len(value) == 0)
        print(f"{key}: NaNs present: {has_nans}, Empty: {is_empty}")

    print("Splitting each event into per-track hits...")
    track_hit_matrices, track_momenta = create_trackwise_data(
        data['detectorID'], data['elementID'], data['n_tracks'],
        data['gpx'], data['gpy'], data['gpz'],
        MAX_IDS
    )
    print(f"Number of valid (non-empty) track samples: {len(track_hit_matrices)}")

    print("Converting sparse matrices to dense format...")
    dense_mats = np.array([m.toarray() for m in track_hit_matrices], dtype=np.float32)

    print("Flattening track-level hit matrices...")
    flattened_hits = dense_mats.reshape(len(dense_mats), -1)

    print("Saving processed track-level data for reference...")
    np.savez(OUTPUT_FILE, hits=flattened_hits, momenta=track_momenta)

    # Remove rows with NaNs from inputs and outputs
    is_nan_input = np.isnan(flattened_hits).any(axis=1)
    is_nan_label = np.isnan(track_momenta).any(axis=1)
    valid_mask = ~(is_nan_input | is_nan_label)

    flattened_hits_clean = flattened_hits[valid_mask]
    track_momenta_clean = track_momenta[valid_mask]
    print(f"After final cleaning: {len(flattened_hits_clean)} samples remain.")

    # Scale inputs and outputs
    print("Scaling inputs and outputs with StandardScaler...")
    input_scaler = StandardScaler()
    X_scaled = input_scaler.fit_transform(flattened_hits_clean)

    output_scaler = StandardScaler()
    Y_scaled = output_scaler.fit_transform(track_momenta_clean)

    print("Building the momentum model (4 outputs => px, py, pz, E)...")
    input_dim = X_scaled.shape[1]
    momentum_model = build_momentum_model(input_dim=input_dim, output_dim=4)

    print("Training the momentum model on scaled track-level data...")
    history = momentum_model.fit(
        X_scaled, Y_scaled,
        epochs=20,
        batch_size=64,
        verbose=1,
        validation_split=0.2
    )

    # Evaluate in scaled space
    scaled_loss, scaled_mse = momentum_model.evaluate(X_scaled, Y_scaled, verbose=1)
    print(f"\nMSE in scaled space: {scaled_mse}")

    print("Converting predictions back to original momentum units...")
    predictions_scaled = momentum_model.predict(X_scaled)
    predictions_phys = output_scaler.inverse_transform(predictions_scaled)

    residuals = predictions_phys - track_momenta_clean
    raw_mse = np.mean((residuals)**2)
    print(f"MSE in original (unscaled) space: {raw_mse}")

    print("Plotting residuals for each component (px, py, pz, E)...")
    plot_residuals(predictions_phys, track_momenta_clean, PLOTS_DIR)

    print("Done!")

if __name__ == "__main__":
    main()
