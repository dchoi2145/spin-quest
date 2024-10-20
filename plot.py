import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import io
import tkinter as tk
from PIL import Image, ImageTk
from open_root_file import read_event

# Function for creating heatmap
def create_heatmap(detector_ids, element_ids):
    # Create a DataFrame
    data = {'Detector': detector_ids,
            'Element': element_ids,
            'Hit': [1] * len(detector_ids)}
    df = pd.DataFrame(data)

    # Pivot the data to create a matrix for the heatmap
    heatmap_data = df.pivot_table(index='Element', columns='Detector', values='Hit', fill_value=0)
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

if __name__ == "__main__":
    # Simulate data
    np.random.seed(0)
    num_detectors = 6
    num_slices = 200
    hits = np.random.randint(0, 2, size=(num_slices, num_detectors))  # 200 hodoscope slices, 6 detectors
    print(hits.shape)

    # Real data
    fp = '~/Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root'
    en = 3000
    d, e = read_event(fp, en)

    # Generate figure
    fig = create_heatmap(d, e)

    # Show the figure
    fig.write_image("fig1.png")