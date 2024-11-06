import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from open_root_file import read_event

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
def create_detector_heatmaps(detector_ids, element_ids, id_to_name, name_to_elements):
    # Convert data to a DataFrame for easier manipulation
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Get unique detector IDs and calculate number of plots
    unique_detectors = sorted(df['Detector'].unique())
    num_plots = len(unique_detectors)
    
    # Create subplots
    fig = make_subplots(rows=1, cols=num_plots, shared_yaxes=True, horizontal_spacing=0.02)
    
    # Create heatmap for each unique detector
    for i, detector_id in enumerate(unique_detectors, start=1):
        detector_data = df[df['Detector'] == detector_id]
        
        # Create hit matrix
        z_matrix = [[0] for _ in range(200)]
        for _, row in detector_data.iterrows():
            z_matrix[int(row['Element'])][0] = 1
            
        # Add heatmap
        fig.add_trace(
            go.Heatmap(
                z=z_matrix,
                colorscale=[[0, 'blue'], [1, 'orange']],
                showscale=False,
                xgap=1,
                ygap=1
            ),
            row=1, col=i
        )

        # Update x-axis to use custom labels
        fig.update_xaxes(
            tickvals=list(range(1)),  # Position for each custom label
            ticktext=[id_to_name[id] for id in range(detector_id, detector_id+1)],  # Custom labels slice
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
            text=id_to_name[detector_id],
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1,
            col=i
        )

    # Only add y-axis labels and title for the first plot in the row
    fig.update_yaxes(title_text="Element ID", range=[0, 200], showticklabels=True, gridcolor="lightgray", row=1, col=1)
    for col in range(2, num_plots + 1):  # Hide y-axis labels for all other plots
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

    heatmap_fig = create_detector_heatmaps(detector_ids, element_ids, detector_id_to_name, detector_name_to_num_elements)
    return heatmap_fig