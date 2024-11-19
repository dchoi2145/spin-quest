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
    # Convert data to a DataFrame
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Get unique detector IDs
    unique_detectors = sorted(df['Detector'].unique())
    num_plots = len(unique_detectors)
    
    # Create a single row of subplots
    fig = make_subplots(
        rows=1,  # one row 
        cols=num_plots,  
        shared_yaxes=True,
        horizontal_spacing=0, # no spacing between plots 
        vertical_spacing=0    
    )
    
    if num_plots == 0:
        return fig
    
    for idx, detector_id in enumerate(unique_detectors):
        current_col = idx + 1  # Column index (1-based)
        
        detector_data = df[df['Detector'] == detector_id]
        detector_name = id_to_name[detector_id]
        num_elements = name_to_elements[detector_name]
        
        # Create hit matrix
        z_matrix = [[0] for _ in range(200)]
        block_height = int(200 / num_elements)
        
        # Fill hits
        for _, row in detector_data.iterrows():
            element_idx = int(row['Element'])
            if 0 <= element_idx < num_elements:
                start_idx = element_idx * block_height
                end_idx = start_idx + block_height
                for i in range(start_idx, end_idx):
                    if i < 200:
                        z_matrix[i] = [1]
        
        fig.add_trace(
            go.Heatmap(
                z=z_matrix,
                colorscale=[[0, 'blue'], [1, 'orange']],
                showscale=False,
                xgap=0,  
                ygap=0,  
                hoverongaps=False
            ),
            row=1, 
            col=current_col
        )

        # Add vertical detector names
        fig.update_xaxes(
            title='',  
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,  
            tickmode='array', 
            tickvals=[0], 
            ticktext=[f"{detector_name} ({num_elements})"],  
            tickangle=270,  
            row=1,
            col=current_col
        )
        
    # Update only first plot y-axis
    fig.update_yaxes(
        title_text="Element ID",
        range=[0, 200],
        showticklabels=True,
        gridcolor="lightgray",
        dtick=20,
        row=1,
        col=1
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Detector Hit Heatmap by Detector",
            y=0.98,
            font=dict(size=16)
        ),
        height=800,
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