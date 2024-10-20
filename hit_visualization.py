import tkinter as tk
from open_root_file import read_event
from plot import create_heatmap, display_heatmap
import matplotlib.pyplot as plt
import sys

# CONSTANTS
TOGGLE_MENU_OFFSET = 50
BTN_HEIGHT = 40
STATION_MAPPINGS = {
    "Station1": (0, 5),
    "Hodoscope1": (6, 9),
    "DP-1": (10, 13),
    "Station2": (14, 19),
    "Hodoscope2": (20, 23),
    "DP-2": (24, 27),  # Corrected range
    "Station3 +": (28, 33),
    "Station3 -": (34, 39),
    "Hodoscope3": (40, 41),
    "Prop1": (42, 43),
    "Hodoscope4": (44, 45),
    "Prop2": (46, 47),
    "Hodoscope5": (48, 51),
    "Prop3": (52, 55)
}
EN = 3000

# Initialize the main application window
root = tk.Tk()
root.geometry("1920x1080")  # Set the window size to 1920x1080 pixels
root.title("Station")  # Set the window title
root.configure(bg="#F0F2F5")  # Set the background color to light gray

selected_button = None  # Variable to keep track of the currently selected button
content_frame = None    # Frame for displaying the content

def organize_hits_by_station(detector_ids, element_ids):
    station_hits = {}
    for station, (start, end) in STATION_MAPPINGS.items():
        station_detector_ids = detector_ids[(detector_ids >= start) & (detector_ids <= end)]
        station_element_ids = element_ids[(detector_ids >= start) & (detector_ids <= end)]
        station_hits[station] = (station_detector_ids, station_element_ids)
    return station_hits

def display_content(content_text=None):
    """Updates the content frame with new information or a graph."""
    global content_frame

    # Clear the previous content
    for widget in content_frame.winfo_children():
        widget.destroy()

    if content_text:
        # Display text content
        content_label = tk.Label(content_frame, text=content_text, font=("Arial", 16), bg="#F0F2F5", fg="black")
        content_label.pack(padx=20, pady=20)

def highlight_button(button, content_text=None):
    """Highlights the selected button, resets the previous selection, and displays new content."""
    global selected_button
    # Reset the previous selected button's background if there is one
    if selected_button is not None:
        selected_button.config(bg="#546E7A", borderwidth=0)  # Reset to the default style

    # Set the new selected button's background color and add a border for highlighting
    button.config(bg="#5D9CEC", borderwidth=2)  # Slightly lighter blue with a border effect
    selected_button = button  # Update the selected button variable

    # Display the content for the selected button
    display_content(content_text)

def toggle_menu():
    """Displays or hides the toggle menu when the menu button is clicked."""
    def collapse_toggle_menu():
        """Hides the toggle menu, resets selected_button, and restores the menu button functionality."""
        global selected_button
        toggle_menu_fm.destroy()  # Remove the toggle menu frame
        selected_button = None  # Reset the selected button since the menu is closed
        toggle_btn.config(text="☰")  # Reset the button text to "☰"
        toggle_btn.config(command=toggle_menu)  # Set the button command to show the menu

    # Create a frame for the toggle menu with a slate blue background color
    toggle_menu_fm = tk.Frame(root, bg="#6A89CC")

    # Button styles for padding and rounded corners
    button_style = {"font": ("Bold", 16), "bd": 0, "bg": "#546E7A", "fg": "white",
                    "activebackground": "#546E7A", "activeforeground": "white",
                    "relief": "flat", "highlightthickness": 0}

    # List of button labels and associated content or graphs
    fp = sys.argv[1]
    d, e = read_event(fp, EN)
    organized = organize_hits_by_station(d, e)
    button_info = [
        (station, station) for station in STATION_MAPPINGS.keys()
    ]

    # Create buttons dynamically and add padding
    window_height = root.winfo_height() - TOGGLE_MENU_OFFSET # Get the current window height
    gap = (window_height - len(button_info) * BTN_HEIGHT) / (len(button_info) + 1)
    y_position = gap
    for label, content in button_info:
        # Create the button first
        button = tk.Button(toggle_menu_fm, text=label, **button_style)
        # Set the command separately to capture the button reference and content/graph correctly
        button.config(command=lambda b=button, c=content, label=label: (
            highlight_button(b, c),
            display_heatmap(create_heatmap(organized[label][0], organized[label][1]), content_frame)
        ))
        button.place(x=20, y=y_position, width=160, height=BTN_HEIGHT)  # Increased height for better spacing
        y_position += BTN_HEIGHT + gap  # Increase y-position for the next button to add spacing

    # Position the menu frame on the left side of the window
    toggle_menu_fm.place(x=0, y=TOGGLE_MENU_OFFSET, height=window_height, width=200)

    # Update the toggle button to close the menu when clicked again
    toggle_btn.config(text="☰")
    toggle_btn.config(command=collapse_toggle_menu)

if __name__ == "__main__":
    # Create a frame for the header at the top of the window
    head_frame = tk.Frame(root, bg="#2C3E50", 
                        highlightbackground="white", highlightthickness=1)

    # Create the toggle button to open the menu
    toggle_btn = tk.Button(head_frame, text="☰", bg="#2C3E50", fg="white",
                        font=("Bold", 20), bd=0, 
                        activebackground="#2C3E50", activeforeground="white",
                        command=toggle_menu)
    toggle_btn.pack(side=tk.LEFT, padx=10)  # Add some padding to the left

    # Create a label to display the title
    title_lb = tk.Label(head_frame, text="Stations", bg="#2C3E50", fg="white",
                        font=("Bold", 20))
    title_lb.pack(side=tk.LEFT, padx=10)  # Add padding between the toggle button and the title

    # Configure the header frame and add it to the top of the window
    head_frame.pack(side=tk.TOP, fill=tk.X)
    head_frame.pack_propagate(False) 
    head_frame.configure(height=50)

    # Create the content frame for displaying information
    content_frame = tk.Frame(root, bg="#F0F2F5")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # Start the main loop for the Tkinter application
    root.mainloop()
