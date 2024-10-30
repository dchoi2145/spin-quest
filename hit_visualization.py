import tkinter as tk
from tkinter import ttk
from open_root_file import read_event, get_total_spills
from plot import create_grouped_heatmaps, display_heatmaps
import sys
import json

# File path
fp = sys.argv[1]

# Global variable for the current event number
MIN_EVENT_NUMBER = int(sys.argv[2])
current_event_number = MIN_EVENT_NUMBER

def load_and_display_spill(content_frame, event_number):
    global current_event_number
    # Update the current event number
    current_event_number = event_number

    # Read the spill data
    d, e = read_event(fp, current_event_number)

    # Get list of selected stations (where checkbox is checked)
    selected_stations = [station for station, var in checkbox_vars.items() if var.get() == 1]

    # Generate new heatmaps for each selected station group
    figures = create_grouped_heatmaps(d, e, station_map, selected_stations)

    # Display the new heatmaps
    display_heatmaps(figures, content_frame)

    # Update the dropdown to reflect the current event number
    spill_dropdown_var.set(str(current_event_number))

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

def on_spill_entry(event):
    """Handles manual entry in the combobox."""
    try:
        new_value = int(spill_dropdown_var.get())
        # Check if the entered value is within the valid range
        if MIN_EVENT_NUMBER <= new_value <= get_total_spills(fp):
            load_and_display_spill(content_frame, new_value)
        else:
            spill_dropdown_var.set(str(current_event_number))  # Reset if out of range
    except ValueError:
        spill_dropdown_var.set(str(current_event_number))  # Reset if input is invalid

def create_checkbox_with_color(frame, text, color, command):
    """Helper function to create a styled checkbox with a color indicator."""
    var = tk.IntVar(value=1)  # Set initial value to 1 (checked)
    
    # Create a frame for the color and checkbox
    container = tk.Frame(frame, bg="#F5F5F5")
    container.pack(fill=tk.X, padx=10, pady=3, anchor="w")

    # Create a label with the color
    color_label = tk.Label(container, bg=color, width=2, height=1, relief="solid")
    color_label.pack(side=tk.LEFT, padx=5)
    
    # Create the checkbox
    checkbox = tk.Checkbutton(
        container, text=text, variable=var, font=("Helvetica", 12), bg="#F5F5F5",
        fg="#333333", activebackground="#E8EAF6", activeforeground="black",
        selectcolor="#E0E0E0", anchor="w", command=command
    )
    checkbox.pack(side=tk.LEFT)
    
    return checkbox, var

if __name__ == "__main__":
    # Initialize the main application window
    root = tk.Tk()
    root.geometry("2560x1440")  # Set the window size for a larger display
    root.title("Detector Hit Viewer")  # Set the window title
    root.configure(bg="#E9ECEF")  # Background color

    # Create the main frame for better layout control and centering
    main_frame = tk.Frame(root, bg="#E9ECEF")
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # Create the right frame for checkboxes and align it next to the plot
    right_frame = tk.Frame(main_frame, bg="#F5F5F5", bd=1, relief="solid", padx=15, pady=15)
    right_frame.pack_propagate(False)
    right_frame.config(width=300, height=750)
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20, anchor="center")

    # Center wrapper frame to align both heatmaps and control buttons
    center_wrapper = tk.Frame(main_frame, bg="#E9ECEF")
    center_wrapper.pack(expand=True, fill=tk.BOTH, anchor="center")

    # Frame for heatmaps
    center_frame = tk.Frame(center_wrapper, bg="#E9ECEF")
    center_frame.pack(expand=True, anchor="center")

    content_frame = tk.Frame(center_frame, bg="#FFFFFF", width=1600, height=1000, relief="ridge", bd=2)
    content_frame.pack(anchor="center", pady=10)

    # Frame for control buttons
    control_frame = tk.Frame(center_frame, bg="#E9ECEF")
    control_frame.pack(anchor="center", pady=20)

    # Parse stations JSON
    with open("detector_map.json", 'r') as infile:
        station_map = json.load(infile)

    # Dictionary to keep track of checkbox variables
    checkbox_vars = {}

    # Create checkboxes with color indicators for each station group
    for group_name, detectors in station_map.items():
        # Create group label
        group_label_frame = tk.Frame(right_frame, bg="#F5F5F5")
        group_label_frame.pack(fill=tk.X, padx=5, pady=(15, 5))
        group_label = tk.Label(group_label_frame, text=group_name, font=("Helvetica", 13, "bold"), bg="#F5F5F5", fg="#333333")
        group_label.pack(side=tk.LEFT, padx=5)

        # Add separator
        separator = tk.Frame(right_frame, height=1, bd=0, bg="#D3D3D3")
        separator.pack(fill=tk.X, padx=10, pady=5)

        for station in detectors:
            # Extract color from station_map
            color = station_map[group_name][station].split(" ")[2]
            
            # Pass a lambda function that calls load_and_display_spill
            checkbox, var = create_checkbox_with_color(
                right_frame,
                station,
                color,
                lambda station=station: load_and_display_spill(content_frame, current_event_number)
            )
            checkbox_vars[station] = var

    # Store the selected spill number
    spill_dropdown_var = tk.StringVar(value=str(current_event_number))

    # Create a dropdown menu for selecting the spill number
    spill_dropdown = ttk.Combobox(control_frame, textvariable=spill_dropdown_var, font=("Helvetica", 12), width=6)
    spill_dropdown['values'] = list(map(str, range(MIN_EVENT_NUMBER, get_total_spills(fp))))
    spill_dropdown.bind("<<ComboboxSelected>>", lambda event: load_and_display_spill(content_frame, int(spill_dropdown_var.get())))
    spill_dropdown.bind("<Return>", on_spill_entry)
    spill_dropdown.grid(row=0, column=1, padx=10)

    # Create navigation buttons
    prev_spill_button = tk.Button(control_frame, text="Previous Spill", font=("Helvetica", 14), command=lambda: load_and_display_prev_spill(content_frame), bg="#4CAF50", fg="white", relief="ridge", borderwidth=2, padx=10)
    prev_spill_button.grid(row=0, column=0, padx=10)

    next_spill_button = tk.Button(control_frame, text="Next Spill", font=("Helvetica", 14), command=lambda: load_and_display_next_spill(content_frame), bg="#4CAF50", fg="white", relief="ridge", borderwidth=2, padx=10)
    next_spill_button.grid(row=0, column=2, padx=10)

    # Load and display the initial spill
    load_and_display_spill(content_frame, current_event_number)

    # Start the main loop for the Tkinter application
    root.mainloop()
