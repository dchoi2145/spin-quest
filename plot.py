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
    
    cols_per_row = max(1, (num_plots + ROWS - 1) // ROWS)
    
    fig = make_subplots(
        rows=ROWS, 
        cols=cols_per_row, 
        shared_yaxes=True, 
        horizontal_spacing=0.02,
        vertical_spacing=0.1
    )
    
    if num_plots == 0:
        return fig
    
    for idx, detector_id in enumerate(unique_detectors):
        current_row = (idx // cols_per_row) + 1
        current_col = (idx % cols_per_row) + 1
        
        detector_data = df[df['Detector'] == detector_id]
        detector_name = id_to_name[detector_id]
        num_elements = name_to_elements[detector_name]
        
        # Create hit matrix
        z_matrix = [[0] * 3 for _ in range(200)]  # Fixed height of 200
        
        # Calculate block height for this detector
        block_height = int(200 / num_elements)
        
        # Fill hits with proper block heights
        for _, row in detector_data.iterrows():
            element_idx = int(row['Element'])
            if 0 <= element_idx < num_elements:
                # Fill the entire block height for this element
                start_idx = element_idx * block_height
                end_idx = start_idx + block_height
                for i in range(start_idx, end_idx):
                    if i < 200:  # Ensure we don't exceed matrix bounds
                        z_matrix[i] = [1] * 3
        
        fig.add_trace(
            go.Heatmap(
                z=z_matrix,
                colorscale=[[0, 'blue'], [1, 'orange']],
                showscale=False,
                xgap=1,  # Add small gap between columns
                ygap=1,  # Add small gap between rows
                hoverongaps=False
            ),
            row=current_row, 
            col=current_col
        )

        # Update x-axis for detector names
        fig.update_xaxes(
            title_text=f"{detector_name}<br>({num_elements})",
            title_standoff=25,
            showgrid=False,
            showticklabels=False,
            row=current_row,
            col=current_col
        )

    # Update y-axes
    for row in range(1, ROWS + 1):
        fig.update_yaxes(
            title_text="Element ID" if row == 1 else None,
            range=[0, 200],  # This makes elements increase from bottom to top
            showticklabels=True,
            gridcolor="lightgray",
            dtick=20,
            row=row,
            col=1
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Detector Hit Heatmap by Detector",
            y=0.98,
            font=dict(size=16)
        ),
        height=2000,
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