import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to create individual heatmaps for each detector
def create_detector_heatmaps(detector_ids, element_ids, name_to_id_elements, max_element_id):
    # Convert data to a DataFrame
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)
    
    # Create a single row of subplots
    fig = make_subplots(
        rows=1,  # one row 
        cols=len(name_to_id_elements),  
        shared_yaxes=True,
        horizontal_spacing=0,  # No spacing between plots
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
        z_matrix = [[0] for _ in range(max_element_id)]
        block_height = int(max_element_id / num_elements)
        hover_text = [[f"Element ID: {i//block_height}, -"] for i in range(max_element_id)]
        
        # Fill hits
        for _, row in detector_data.iterrows():
            element_idx = int(row['Element'])
            if 0 <= element_idx < num_elements:
                start_idx = element_idx * block_height
                end_idx = start_idx + block_height
                for i in range(start_idx, end_idx):
                    if i < max_element_id:
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
        range=[0, max_element_id],
        showticklabels=True,
        gridcolor="lightgray",
        dtick=20,
        row=1,
        col=1
    )

    # Update layout
    fig.update_layout(
        height=800,
        margin=dict(t=0, b=0, l=0, r=0),  # Remove margins
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background for the plot
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background for the paper
        showlegend=False
    )

    return fig
