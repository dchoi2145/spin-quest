import tensorflow as tf
import numpy as np
from file_read import read_events, get_detector_info
from reconstruct import read_momentum, convert_to_hit_matrices, join_momentum_arrays
import matplotlib.pyplot as plt

# CONSTANTS
SPECTROMETER_INFO_PATH = "spectrometer.csv"
MODEL_PATH = "models/hit_to_momentum_model.keras"

# Load the model
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully!")

# Prepare test data 
test_root_files = [
    "runs/trackQA10.root"
]

# Process test files 
all_test_detector_ids = []
all_test_element_ids = []
all_test_gpx = []
all_test_gpy = []
all_test_gpz = []

for test_file in test_root_files:
    detector_ids, element_ids = read_events(test_file)
    all_test_detector_ids.append(detector_ids)
    all_test_element_ids.append(element_ids)

    gpx, gpy, gpz = read_momentum(test_file)
    all_test_gpx.append(gpx)
    all_test_gpy.append(gpy)
    all_test_gpz.append(gpz)

# Concatenate test data
all_test_detector_ids = np.concatenate(all_test_detector_ids)
all_test_element_ids = np.concatenate(all_test_element_ids)
all_test_gpx = np.concatenate(all_test_gpx)
all_test_gpy = np.concatenate(all_test_gpy)
all_test_gpz = np.concatenate(all_test_gpz)

# Get max IDs from spectrometer file
detector_name_to_id_elements = get_detector_info(SPECTROMETER_INFO_PATH)
max_detector_id = max([detector_name_to_id_elements[name][0] for name in detector_name_to_id_elements])
max_element_id = max([detector_name_to_id_elements[name][1] for name in detector_name_to_id_elements])

# Filter and process test data
all_test_detector_ids = np.where(all_test_detector_ids <= max_detector_id, all_test_detector_ids, 0)
all_test_element_ids = np.where(all_test_element_ids <= max_element_id, all_test_element_ids, 0)

test_hit_matrices = convert_to_hit_matrices(all_test_detector_ids, all_test_element_ids, max_detector_id, max_element_id)
test_labels = join_momentum_arrays(all_test_gpx, all_test_gpy, all_test_gpz)

# Evaluate the model
print("Evaluating model...")
loss, mse = model.evaluate(test_hit_matrices, test_labels)
print(f"Test Loss: {loss}")
print(f"Mean Squared Error: {mse}")

# Predictions
predictions = model.predict(test_hit_matrices)
print(f"Predictions: {predictions[:5]}")
print(f"Actual: {test_labels[:5]}")

# Calculate residuals for gpx, gpy, gpz
residuals_gpx = test_labels[:, :len(test_labels[0])//3] - predictions[:, :len(predictions[0])//3]
residuals_gpy = test_labels[:, len(test_labels[0])//3:2*len(test_labels[0])//3] - predictions[:, len(predictions[0])//3:2*len(predictions[0])//3]
residuals_gpz = test_labels[:, 2*len(test_labels[0])//3:] - predictions[:, 2*len(predictions[0])//3:]

# Plot histograms of residuals
def plot_residual_histogram(residuals, component_name):
    plt.hist(residuals.flatten(), bins=50, alpha=0.7, label=f"{component_name} Residuals")
    plt.axvline(0, color='red', linestyle='--', label='Zero Error')
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title(f"Residual Histogram for {component_name}")
    plt.legend()
    plt.show()

plot_residual_histogram(residuals_gpx, "gpx")
plot_residual_histogram(residuals_gpy, "gpy")
plot_residual_histogram(residuals_gpz, "gpz")


