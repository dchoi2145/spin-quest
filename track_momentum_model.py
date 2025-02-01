import uproot
import numpy as np
import tensorflow as tf
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler

# Muon mass in GeV (adjust if needed)
MUON_MASS = 0.10566  # Adding mass of muon for calculating E

# Constants
FILE_PATH = '/Users/davidchoi/Documents/GitHub/spin-quest/trial4/1/trackQA.root'  
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

# Replacing manual track splitting with a machine learning model
def build_track_segmentation_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(MAX_IDS, activation='softmax')  # Predict track assignments
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def predict_trackwise_data(detector_ids, element_ids, n_tracks, max_ids, model):
    track_hit_matrices = []  # List to hold matrices of hits for each track
    num_events = len(detector_ids)  # Number of events in the dataset

    for evt_index in range(num_events):
        event_det = detector_ids[evt_index]
        event_elem = element_ids[evt_index]
        num_tracks = n_tracks[evt_index]

        # Create a sparse matrix to represent hits
        mat = csr_matrix((max_ids, max_ids), dtype=np.float32)
        for d, e in zip(event_det, event_elem):
            if 0 < d <= max_ids and 0 < e <= max_ids:
                mat[d - 1, e - 1] = 1
        
        # Convert sparse matrix to dense format and reshape for input
        input_data = mat.toarray().reshape(1, max_ids, max_ids, 1)
        predicted_tracks = model.predict(input_data)[0]  # Predict track assignments

        # Store predicted track hit matrices
        track_hit_matrices.append(predicted_tracks)
    
    return np.array(track_hit_matrices, dtype=np.float32)

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
    
    # Filter events with at least one track to align X and y
    valid_events = data['n_tracks'] >= 1
    detector_ids = data['detectorID'][valid_events]
    element_ids = data['elementID'][valid_events]
    n_tracks = data['n_tracks'][valid_events]
    
    # Extract true momenta (using first track in each event)
    px = np.array([evt[0] for evt in data['gpx'][valid_events]])
    py = np.array([evt[0] for evt in data['gpy'][valid_events]])
    pz = np.array([evt[0] for evt in data['gpz'][valid_events]])
    E = np.sqrt(px**2 + py**2 + pz**2 + MUON_MASS**2)
    y = np.vstack([px, py, pz, E]).T  # Target array [px, py, pz, E]
    
    print("Building and training the track segmentation model...")
    input_shape = (MAX_IDS, MAX_IDS, 1)
    track_segmentation_model = build_track_segmentation_model(input_shape)
    
    print("Predicting track assignments...")
    track_hit_matrices = predict_trackwise_data(
        detector_ids, element_ids, n_tracks, MAX_IDS, track_segmentation_model
    )
    
    print("Flattening track-level hit matrices...")
    flattened_hits = track_hit_matrices.reshape(len(track_hit_matrices), -1)
    
    print("Scaling inputs with StandardScaler...")
    input_scaler = StandardScaler()
    X_scaled = input_scaler.fit_transform(flattened_hits)
    
    print("Building the momentum model (4 outputs => px, py, pz, E)...")
    input_dim = X_scaled.shape[1]
    momentum_model = build_momentum_model(input_dim=input_dim, output_dim=4)

    print("Training the momentum model on track-level data...")
    # Train with true momenta as targets
    history = momentum_model.fit(
        X_scaled, y,  # Use y (true momenta) as targets
        epochs=20,
        batch_size=64,
        verbose=1,
        validation_split=0.2
    )

    print("Generating predictions and residual plots...")
    predictions = momentum_model.predict(X_scaled)
    plot_residuals(predictions, y, PLOTS_DIR)

    print("Done!")

if __name__ == "__main__":
    main()