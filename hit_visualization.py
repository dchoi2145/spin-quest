import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
from open_root_file import read_event
from open_root_file import get_total_spills

# Global variable for the current event number
current_event_number = 0

fp = '~/Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root'

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

def load_and_display_spill(content_frame, event_number):
    global current_event_number
    # Update the current event number
    current_event_number = event_number

    # Read the spill data
    d, e = read_event(fp, current_event_number)

    # Generate a new heatmap
    fig = create_heatmap(d, e)

    # Clear the existing content in the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Display the new heatmap
    display_heatmap(fig, content_frame)

    # Update the dropdown to reflect the current event number
    spill_dropdown_var.set(current_event_number)

def load_and_display_next_spill(content_frame):
    global current_event_number
    # Increment the event number
    current_event_number += 1
    load_and_display_spill(content_frame, current_event_number)

def load_and_display_prev_spill(content_frame):
    global current_event_number
    # Decrement the event number with a lower bound check
    if current_event_number > 1:
        current_event_number -= 1
    load_and_display_spill(content_frame, current_event_number)

if __name__ == "__main__":
    # Initialize the main application window
    root = tk.Tk()
    root.geometry("1920x1080")  # Set the window size
    root.title("Hodoscope Station")  # Set the window title
    root.configure(bg="#F0F2F5")  # Background color

    # Create the content frame for displaying information
    content_frame = tk.Frame(root, bg="#F0F2F5")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # Store the selected spill number
    spill_dropdown_var = tk.IntVar(value=current_event_number)

    # Create a dropdown menu for selecting the spill number
    spill_dropdown = tk.OptionMenu(root, spill_dropdown_var, *range(1, get_total_spills(fp)), command=lambda x: load_and_display_spill(content_frame, spill_dropdown_var.get()))
    spill_dropdown.config(font=("Arial", 12), width=2)
    spill_dropdown.pack(pady=0)

    # Create a button frame to organize the buttons side by side
    button_frame = tk.Frame(root, bg="#F0F2F5")
    button_frame.pack(pady=20)

    # Create navigation buttons
    button_frame = tk.Frame(root, bg="#F0F2F5")
    button_frame.pack(pady=20)

    next_spill_button = tk.Button(button_frame, text="Next Spill", font=("Arial", 16), command=lambda: load_and_display_next_spill(content_frame))
    next_spill_button.grid(row=0, column=1, padx=10)

    prev_spill_button = tk.Button(button_frame, text="Previous Spill", font=("Arial", 16), command=lambda: load_and_display_prev_spill(content_frame))
    prev_spill_button.grid(row=0, column=0, padx=10)

    # Load and display the initial spill
    load_and_display_next_spill(content_frame)

    # Start the main loop for the Tkinter application
    root.mainloop()
