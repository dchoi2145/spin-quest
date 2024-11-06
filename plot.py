import pandas as pd
import plotly.graph_objects as go
import json

from plotly.subplots import make_subplots
from open_root_file import read_event

DETECTOR_MAP_PATH = "detector_map.json"
SPECTROMETER_INFO_PATH = "spectrometer.csv"

# Function for reading detector names from spectrometer CSV file
def get_detector_info(file_name):
    # two maps
    id_to_name = dict()
    name_to_elements = dict()

    with open(file_name, 'r') as infile:
        # skip first line
        infile.readline()

        for line in infile.readlines():
            split_line = line.split(",")
            detector_id = int(split_line[0])
            detector_name = split_line[1]
            num_elements = int(split_line[2])

            id_to_name[detector_id] = detector_name
            name_to_elements[detector_name] = num_elements

    id_to_name[29] = "PLACEHOLDER"
    name_to_elements["PLACEHOLDER"] = 200

    return id_to_name, name_to_elements

# Function to create individual heatmaps for each detector
def create_detector_heatmaps(detector_ids, element_ids, station_map, id_to_name, name_to_elements):
    # Convert data to a DataFrame for easier manipulation
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Calculate the number of detectors for subplot layout
    num_detectors = len(station_map)
    fig = make_subplots(rows=1, cols=num_detectors, shared_yaxes=True, horizontal_spacing=0.02)

    # Add a heatmap for each detector
    for i, (station, mapping) in enumerate(station_map.items(), start=1):
        min_detector, max_detector, color = mapping.split(" ")
        min_detector = int(min_detector)
        max_detector = int(max_detector)

        # Filter data for the current detector
        detector_data = df[(df['Detector'] >= min_detector) & (df['Detector'] <= max_detector)]

        # Create a matrix of hits
        z_matrix = [[0 for _ in range(max_detector - min_detector + 1)] for _ in range(200)]
        for _, row in detector_data.iterrows():
            z_matrix[int(row['Element'])][int(row['Detector']) - min_detector] = 1  # 1 for hits, 0 for no hits

        # Create a heatmap for this detector
        heatmap = go.Heatmap(
            z=z_matrix,
            colorscale=[[0, 'blue'], [1, 'orange']],  # Blue for no hit, yellow for hit
            showscale=False,  # Disable color scale
            colorbar=None,  # Ensure no color bar is displayed
            xgap=1,  # Gap between cells for x-axis (horizontal)
            ygap=1   # Gap between cells for y-axis (vertical)
        )

        # Add the heatmap to the subplot
        fig.add_trace(heatmap, row=1, col=i)

        # Update x-axis to use custom labels
        fig.update_xaxes(
            tickvals=list(range(max_detector - min_detector + 1)),  # Position for each custom label
            ticktext=[id_to_name[id] for id in range(min_detector, max_detector+1)],  # Custom labels slice
            tickangle=45,  # Rotate labels for readability
            showgrid=False,
            row=1,
            col=i
        )

        # Add annotation for each station label, precisely centered above each subplot
        fig.add_annotation(
            x=0.5,
            y=1.05,
            xref="x domain",
            yref="y domain",
            text=station,
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1,
            col=i
        )

    # Only add y-axis labels and title for the first plot in the row
    fig.update_yaxes(title_text="Element ID", range=[0, 200], showticklabels=True, gridcolor="lightgray", row=1, col=1)
    for col in range(2, num_detectors + 1):  # Hide y-axis labels for all other plots
        fig.update_yaxes(showticklabels=False, title_text=None, row=1, col=col)

    # Update layout for overall plot
    fig.update_layout(
        title=dict(
            text="Detector Hit Heatmap by Detector",
            y=0.95,  # Move the main title slightly up to create more space
            font=dict(size=16)
        ),
        height=700,  # Increase plot height to allow for the extra space
        margin=dict(t=100, b=40, l=40, r=20),
        plot_bgcolor="white",
    )

    return fig

# Function to load data for a specific event and generate the combined heatmap figure
def generate_combined_heatmap_figure(file_path, event_number):
    _, detector_ids, element_ids = read_event(file_path, event_number)
    detector_id_to_name, detector_name_to_num_elements = get_detector_info(SPECTROMETER_INFO_PATH)
    with open(DETECTOR_MAP_PATH, "r") as file:
        station_map = json.load(file)

    heatmap_fig = create_detector_heatmaps(detector_ids, element_ids, station_map, detector_id_to_name, detector_name_to_num_elements)
    return heatmap_fig