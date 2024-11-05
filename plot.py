import pandas as pd
import plotly.graph_objects as go
import json

from plotly.subplots import make_subplots
from open_root_file import read_event

# Custom labels for each detector
custom_labels = [
    'D0V', 'D0Vp', 'D0Xp', 'D0X', 'D0U', 'D0Up', 'H1L', 'H1R', 'H1B', 'H1T',
    'DP1TL', 'DP1TR', 'DP1BL', 'DP1BR', 'D2V', 'D2Vp', 'D2Xp', 'D2X', 'D2U', 'D2Up',
    'H2R', 'H2L', 'H2T', 'H2B', 'DP2TL', 'DP2TR', 'DP2BL', 'DP2BR', 'D3pVp', 'D3pV',
    'D3pXp', 'D3pX', 'D3pUp', 'D3pU', 'D3mVp', 'D3mV', 'D3mXp', 'D3mX', 'D3mUp', 'D3mU',
    'H3T', 'H3B', 'P1Y1', 'P1Y2', 'H4Y1R', 'H4Y1L', 'P1X1', 'P1X2', 'H4Y2R', 'H4Y2L',
    'H4T', 'H4B', 'P2X1', 'P2X2', 'P2Y1', 'P2Y2'
]

DETECTOR_MAP_PATH = "detector_map.json"

# Load station_map from JSON file
with open(DETECTOR_MAP_PATH, "r") as file:
    station_map = json.load(file)

# Function to create individual heatmaps for each detector
def create_detector_heatmaps(detector_ids, element_ids, station_map):
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
            ticktext=custom_labels[min_detector:max_detector + 1],  # Custom labels slice
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
    heatmap_fig = create_detector_heatmaps(detector_ids, element_ids, station_map)
    return heatmap_fig