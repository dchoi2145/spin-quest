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

# Function for creating grouped heatmaps by detector type
def create_individual_heatmaps(detector_ids, element_ids, station_map, selected_stations):
    # Create a DataFrame for the hits
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Dictionary to store individual figures for each detector
    figures = {}

    # Loop through each selected station to create an individual plot
    for station in selected_stations:
        # Get the detector range and color for this station
        mapping = station_map[station].split(" ")
        min_detector = int(mapping[0])
        max_detector = int(mapping[1])
        color = mapping[2]

        # Filter data for the current station's range
        station_data = df[(df['Detector'] >= min_detector) & (df['Detector'] <= max_detector)]

        # Calculate the maximum element ID for this station to set the y-axis range dynamically
        max_element_id = station_data['Element'].max()

        # Create a new figure for each detector
        fig = go.Figure()

        # Add a scatter trace for this station's data points in its unique color
        fig.add_trace(go.Scatter(
            x=station_data['Detector'],  # x = Detector
            y=station_data['Element'],   # y = Element ID
            mode='markers',
            marker=dict(color=color, size=5),
            name=station,
            showlegend=True
        ))

        # Update layout for each individual detector figure
        fig.update_layout(
            title=f"Hits for {station} Detector",
            xaxis_title="Detector",
            yaxis_title="Element ID",
            xaxis=dict(range=[0, MAX_DETECTOR]),
            yaxis=dict(range=[0, max_element_id]),  # Set y-axis based on max element ID for the station
            plot_bgcolor="white"
        )

        # Store the figure for this detector
        figures[station] = fig

    return figures

def display_heatmaps(figures, content_frame):
    # Clear existing content
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Arrange figures in a grid layout
    max_columns = 5  # Adjust to fit more plots per row
    row = 0
    col = 0

    for detector_name, fig in figures.items():
        # Convert Plotly figure to image
        img_bytes = pio.to_image(fig, format='png')
        
        # Load image with PIL and convert to PhotoImage for Tkinter
        img = Image.open(io.BytesIO(img_bytes))
        img = img.resize((305, 275), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        
        # Display image in a Label widget
        label = tk.Label(content_frame, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, padx=10, pady=10)

        # Update row and column for the grid layout
        col += 1
        if col >= max_columns:
            col = 0
            row += 1

