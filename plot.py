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
def create_grouped_heatmaps(detector_ids, element_ids, station_map, selected_stations):
    # Create a DataFrame for the hits
    data = {'Detector': detector_ids, 'Element': element_ids, 'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Dictionary to store grouped figures for each detector type
    figures = {}

    # Loop over each group in the defined detector groups
    for group_name, group_detectors in station_map.items():
        # Filter selected stations that belong to the current group
        group_selected_stations = [station for station in group_detectors if station in selected_stations]
        
        if not group_selected_stations:
            continue  # Skip if no detectors in this group are selected

        # Create a new figure for each group of detectors
        fig = go.Figure()
        
        for station in group_selected_stations:
            # Get the detector range and color for this station
            mapping = station_map[group_name][station].split(" ")
            min_detector = int(mapping[0])
            max_detector = int(mapping[1])
            color = mapping[2]

            # Filter data for the current station's range
            station_data = df[(df['Detector'] >= min_detector) & (df['Detector'] <= max_detector)]

            # Add a scatter trace for this station's data points in its unique color, forcing the legend to show
            fig.add_trace(go.Scatter(
                x=station_data['Detector'],  # Flip axes: x = Detector, y = Element
                y=station_data['Element'],
                mode='markers',
                marker=dict(color=color, size=5),
                name=station,
                showlegend=True  # Force legend display
            ))

        # Update layout for the current figure
        fig.update_layout(
            title=f"Hits for {group_name} Detectors",
            xaxis_title="Detector",
            yaxis_title="Element ID",
            xaxis=dict(range=[0, MAX_DETECTOR]),
            yaxis=dict(range=[0, MAX_ELEMENT]),
            plot_bgcolor="white"
        )

        # Store the figure
        figures[group_name] = fig

    return figures

# Function to display multiple heatmaps in GUI
def display_heatmaps(figures, content_frame):
    # Clear existing content
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Arrange figures side by side in a grid layout
    max_columns = 2  # Adjust to 2 columns for better layout with fewer plots
    row = 0
    col = 0

    for group_name, fig in figures.items():
        # Convert Plotly figure to image
        img_bytes = pio.to_image(fig, format='png')
        
        # Load image with PIL and convert to PhotoImage for Tkinter
        img = Image.open(io.BytesIO(img_bytes))
        photo = ImageTk.PhotoImage(img)
        
        # Display image in a Label widget
        label = tk.Label(content_frame, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, padx=20, pady=20)

        # Update row and column for the grid layout
        col += 1
        if col >= max_columns:
            col = 0
            row += 1
