import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from open_root_file import read_event

# CONSTANTS
MAX_ELEMENT_ID = 400

# Function for reading detector names from spectrometer CSV file
def get_detector_info(file_name):
    name_to_id_elements = dict()
    ids = set()

    with open(file_name, 'r') as infile:
        # skip first line
        infile.readline()

        for line in infile.readlines():
            split_line = line.split(",")
            detector_id = int(split_line[0])
            detector_name = split_line[1]
            num_elements = int(split_line[2])

            if detector_id not in ids:
                name_to_id_elements[detector_name] = [detector_id, num_elements, True]
                ids.add(detector_id)

    return name_to_id_elements

# Function to create individual heatmaps for each detector
def create_detector_heatmaps(detector_ids, element_ids, name_to_id_elements):
    # Convert data to a DataFrame
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)
    
    # Create a single row of subplots
    fig = make_subplots(
        rows=1,  # one row 
        cols=len(name_to_id_elements),  
        shared_yaxes=True,
        horizontal_spacing=0, # no spacing between plots 
        vertical_spacing=0    
    )
    
    offset = 0
    for idx, [detector_name, (detector_id, num_elements, display)] in enumerate(name_to_id_elements.items()):
        if not display:
            offset += 1
            continue
        
        idx = idx - offset
        current_col = idx + 1  # Column index (1-based)
        
        detector_data = df[df['Detector'] == detector_id]
        
        # Create hit matrix
        z_matrix = [[0] for _ in range(MAX_ELEMENT_ID)]
        block_height = int(MAX_ELEMENT_ID / num_elements)
        hover_text = [[f"Element ID: {i//block_height}, -"] for i in range(MAX_ELEMENT_ID)]
        
        # Fill hits
        for _, row in detector_data.iterrows():
            element_idx = int(row['Element'])
            if 0 <= element_idx < num_elements:
                start_idx = element_idx * block_height
                end_idx = start_idx + block_height
                for i in range(start_idx, end_idx):
                    if i < MAX_ELEMENT_ID:
                        z_matrix[i] = [1]
                        hover_text[i] = [f"Element ID: {element_idx}, Hit"]
        
        fig.add_trace(
            go.Heatmap(
                z=z_matrix,
                hovertemplate=f"Detector: {detector_name}<br>" +
                             "Element ID: %{y}<br>" +
                             "Status: %{z:d}<extra></extra>",
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
        range=[0, MAX_ELEMENT_ID],
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
def generate_combined_heatmap_figure(file_path, event_number, detector_name_to_id_elements):
    _, detector_ids, element_ids = read_event(file_path, event_number)

    heatmap_fig = create_detector_heatmaps(detector_ids, element_ids, detector_name_to_id_elements)
    return heatmap_fig