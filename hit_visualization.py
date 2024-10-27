import tkinter as tk
from open_root_file import read_event, get_total_spills
from plot import create_heatmap, display_heatmap
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

    # Generate a new heatmap with selected stations
    fig = create_heatmap(d, e, station_map, selected_stations)

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

def create_checkbox(frame, text, command):
    """Helper function to create a styled checkbox that is initially checked."""
    var = tk.IntVar(value=1)  # Set initial value to 1 (checked)
    checkbox = tk.Checkbutton(
        frame, text=text, variable=var, font=("Arial", 12), bg="#FFFFFF",
        fg="black", activebackground="#E8EAF6", activeforeground="black",
        selectcolor="#BBDEFB", anchor="w",
        command=command  # Add command parameter
    )
    checkbox.pack(fill=tk.X, padx=10, pady=2)
    return checkbox, var

if __name__ == "__main__":
    # Initialize the main application window
    root = tk.Tk()
    root.geometry("1920x1080")  # Set the window size
    root.title("Hodoscope Station")  # Set the window title
    root.configure(bg="#F0F2F5")  # Background color

    # Create the content frame for displaying information
    content_frame = tk.Frame(root, bg="#F0F2F5")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # Create the right frame for checkboxes and place it on the right
    right_frame = tk.Frame(root, bg="#FFFFFF", bd=2, relief="ridge", padx=15, pady=15)
    right_frame.place(relx=0.85, rely=0.5, anchor="center")

    # Parse stations json
    with open("detector_map.json", 'r') as infile:
        station_map = json.load(infile)

    # List of stations in the desired order
    stations = station_map.keys()

    # Dictionary to keep track of checkbox variables
    checkbox_vars = {}

    # Create checkboxes for each station
    for station in stations:
        # Pass a lambda function that calls load_and_display_spill
        checkbox, var = create_checkbox(
            right_frame, 
            station, 
            lambda station=station: load_and_display_spill(content_frame, current_event_number)
        )
        checkbox_vars[station] = var

    # Store the selected spill number
    spill_dropdown_var = tk.IntVar(value=current_event_number)

    # Create a frame to hold the spill dropdown and center it
    dropdown_frame = tk.Frame(root, bg="#F0F2F5")
    dropdown_frame.pack(pady=10)

    # Create a dropdown menu for selecting the spill number
    spill_dropdown = tk.OptionMenu(dropdown_frame, spill_dropdown_var, *range(MIN_EVENT_NUMBER, get_total_spills(fp)), command=lambda x: load_and_display_spill(content_frame, spill_dropdown_var.get()))
    spill_dropdown.config(font=("Arial", 12), width=2)
    spill_dropdown.pack()

    # Create a button frame to organize the buttons side by side
    button_frame = tk.Frame(root, bg="#F0F2F5")
    button_frame.pack(pady=20)

    # Create navigation buttons
    prev_spill_button = tk.Button(button_frame, text="Previous Spill", font=("Arial", 16), command=lambda: load_and_display_prev_spill(content_frame), bg="#BBDEFB", fg="black", relief="raised")
    prev_spill_button.grid(row=0, column=0, padx=10)

    next_spill_button = tk.Button(button_frame, text="Next Spill", font=("Arial", 16), command=lambda: load_and_display_next_spill(content_frame), bg="#BBDEFB", fg="black", relief="raised")
    next_spill_button.grid(row=0, column=1, padx=10)

    # Load and display the initial spill
    load_and_display_spill(content_frame, current_event_number)

    # Start the main loop for the Tkinter application
    root.mainloop()

