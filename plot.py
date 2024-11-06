import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from open_root_file import read_event

SPECTROMETER_INFO_PATH = "spectrometer.csv"
ROWS = 3

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
    
    # Ensure at least 1 column per row
    cols_per_row = max(1, (num_plots + ROWS - 1) // ROWS)
    
    # Create subplots
    fig = make_subplots(
        rows=ROWS, 
        cols=cols_per_row, 
        shared_yaxes=True, 
        horizontal_spacing=0.02,
        vertical_spacing=0.1
    )
    
    # If no detectors, return empty figure
    if num_plots == 0:
        return fig
    
    # Create heatmap for each unique detector
    for idx, detector_id in enumerate(unique_detectors):
        # Calculate current row and column
        current_row = (idx // cols_per_row) + 1
        current_col = (idx % cols_per_row) + 1
        
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
            row=current_row, 
            col=current_col
        )

        # Update x-axis labels
        fig.update_xaxes(
            tickvals=list(range(1)),
            ticktext=[id_to_name[id] for id in range(detector_id, detector_id+1)],
            tickangle=45,
            showgrid=False,
            row=current_row,
            col=current_col
        )

        # Add detector label annotation
        fig.add_annotation(
            x=0.5,
            y=1.05,
            xref="x domain" if idx == 0 else f"x{idx+1} domain",
            yref="y domain" if idx == 0 else f"y{idx+1} domain",
            text=id_to_name[detector_id],
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # Update y-axis labels
    for row in range(1, ROWS + 1):
        # Add y-axis label for first column of each row
        fig.update_yaxes(
            title_text="Element ID" if row == 1 else None,
            range=[0, 200],
            showticklabels=True,
            gridcolor="lightgray",
            row=row,
            col=1
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Detector Hit Heatmap by Detector",
            y=0.95,
            font=dict(size=16)
        ),
        height=1000,
        margin=dict(t=100, b=40, l=40, r=20),
        plot_bgcolor="white",
        showlegend=False
    )

    return fig

# Function to load data for a specific event and generate the combined heatmap figure
def generate_combined_heatmap_figure(file_path, event_number):
    _, detector_ids, element_ids = read_event(file_path, event_number)
    detector_id_to_name, detector_name_to_num_elements = get_detector_info(SPECTROMETER_INFO_PATH)

    heatmap_fig = create_detector_heatmaps(detector_ids, element_ids, detector_id_to_name, detector_name_to_num_elements)
    return heatmap_fig