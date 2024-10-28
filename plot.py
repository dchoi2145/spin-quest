import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import io
import tkinter as tk
from PIL import Image, ImageTk
from open_root_file import read_event

MAX_DETECTOR = 56
MAX_ELEMENT = 200 

# Function for creating heatmap with individual station colors
def create_heatmap(detector_ids, element_ids, station_map, selected_stations):
    # Create a DataFrame for the hits
    data = {'Detector': detector_ids,
            'Element': element_ids,
            'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Initialize an empty figure with a white background
    fig = go.Figure()
    fig.update_layout(
        title="Hodoscope Hits by Detector",
        xaxis_title="Element ID",
        yaxis_title="Detector",
        xaxis=dict(range=[0, MAX_ELEMENT]),
        yaxis=dict(range=[0, MAX_DETECTOR]),
        plot_bgcolor="white"
    )

    # Plot each selected station in its unique color
    for station in selected_stations:
        # Get the detector range and color for this station
        mapping = station_map[station].split(" ")
        min_detector = int(mapping[0])
        max_detector = int(mapping[1])
        color = mapping[2]

        # Filter data for the current station's range
        station_data = df[(df['Detector'] >= min_detector) & (df['Detector'] <= max_detector)]

        # Add a scatter trace for this station's data points in its unique color
        fig.add_trace(go.Scatter(
            x=station_data['Element'],
            y=station_data['Detector'],
            mode='markers',
            marker=dict(color=color, size=5),
            name=station
        ))

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
