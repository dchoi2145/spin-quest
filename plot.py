import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import io
import tkinter as tk
from PIL import Image, ImageTk
from open_root_file import read_event

# Function for creating heatmap
def create_heatmap(detector_ids, element_ids, station_map, station):
    # Create a DataFrame
    data = {'Detector': detector_ids,
            'Element': element_ids,
            'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Get all unique detector IDs and element IDS
    all_detector_ids = list(range(56))
    all_element_ids = list(range(200))

    # Pivot the data to create a matrix for the heatmap
    heatmap_data = df.pivot_table(index='Element', columns='Detector', values='Hit', fill_value=0)
    heatmap_data = heatmap_data.reindex(index=all_element_ids, columns=all_detector_ids, fill_value=0)  # Reindex with all detector IDs and element IDs

    mapping = station_map[station].split(" ")
    min_detector = int(mapping[0])
    max_detector = int(mapping[1])
    mask = ~heatmap_data.columns.isin(range(min_detector, max_detector + 1))
    heatmap_data.loc[:, mask] = 0

    transposed = heatmap_data.T

    # Create heatmap
    fig = px.imshow(transposed,
                    labels=dict(x='Element ID', y='Detector', color='Hit'),
                    x=transposed.columns,
                    y=transposed.index,
                    color_continuous_scale='magenta')

    fig.update_layout(title='Hodoscope Hits by Detector',
                    xaxis_title='Element ID',
                    yaxis_title='Detector')
    
    return fig

# Function to display heatmap in GUI
def display_heatmap(fig, content_frame):
    # Convert Plotly figure to image
    img_bytes = pio.to_image(fig, format='png')
    
    # Load image with PIL and convert to PhotoImage for Tkinter
    img = Image.open(io.BytesIO(img_bytes))
    photo = ImageTk.PhotoImage(img)
    
    # Display image in a Label widget
    label = tk.Label(content_frame, image=photo)
    label.image = photo  # Keep a reference to avoid garbage collection
    label.pack(padx=20, pady=20)