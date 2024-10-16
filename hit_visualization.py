import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from open_root_file import read_event
from plot import create_heatmap, display_heatmap
import matplotlib.pyplot as plt
import sys

# Initialize the main application window
root = tk.Tk()
root.geometry("1920x1080")  # Set the window size to 1920x1080 pixels
root.title("Station")  # Set the window title
root.configure(bg="#F0F2F5")  # Set the background color to light gray

selected_button = None  # Variable to keep track of the currently selected button
content_frame = None    # Frame for displaying the content

def display_content(content_text=None, graph=None):
    """Updates the content frame with new information or a graph."""
    global content_frame

    # Clear the previous content
    for widget in content_frame.winfo_children():
        widget.destroy()

    if content_text:
        # Display text content
        content_label = tk.Label(content_frame, text=content_text, font=("Arial", 16), bg="#F0F2F5", fg="black")
        content_label.pack(padx=20, pady=20)

    if graph:
        # Display the graph using Matplotlib's FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(graph, master=content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=20, pady=20)

def plot_sample_graph():
    """Creates a sample Matplotlib graph and returns the figure."""
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30])  # Sample data
    ax.set_title("Sample Graph")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    return fig

def highlight_button(button, content_text=None, graph=None):
    """Highlights the selected button, resets the previous selection, and displays new content."""
    global selected_button
    # Reset the previous selected button's background if there is one
    if selected_button is not None:
        selected_button.config(bg="#546E7A", borderwidth=0)  # Reset to the default style

    # Set the new selected button's background color and add a border for highlighting
    button.config(bg="#5D9CEC", borderwidth=2)  # Slightly lighter blue with a border effect
    selected_button = button  # Update the selected button variable

    # Display the content for the selected button
    display_content(content_text, graph)

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
    #fp = '~/Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root'
    en = 3000
    d, e = read_event(fp, en)
    fig = create_heatmap(d, e)
    button_info = [
        ("Station1", "Information about Station 1", None),
        ("Station2", "Details of Station 2", None),
        ("Station3 +", "Data related to Station 3 +", None),
        ("Station3 -", "Information for Station 3 -", None),
        ("Hodoscope1", "Hodoscope 1 analysis", None),
        ("Hodoscope2", "Hodoscope 2 details", None),
        ("Hodoscope3", "Hodoscope 3 description", None),
        ("DP-1", "Details about DP-1", None),
        ("DP-2", "Information for DP-2", None),
        ("Prop1", "Properties related to Prop 1", None),
        ("Prop2", "Explanation for Prop 2", None),
        ("Prop3", "Summary of Prop 3", None),
        ("Graph Example", "Yay", None)  # Displays a graph
    ]

    # Create buttons dynamically and add padding
    y_position = 20
    for label, content, graph in button_info:
        # Create the button first
        button = tk.Button(toggle_menu_fm, text=label, **button_style)
        # Set the command separately to capture the button reference and content/graph correctly
        button.config(command=lambda b=button, c=content, g=graph: (highlight_button(b, c, g), display_heatmap(create_heatmap(d, e), content_frame)))
        button.place(x=20, y=y_position, width=160, height=40)  # Increased height for better spacing
        y_position += 60  # Increase y-position for the next button to add spacing

    window_height = root.winfo_height()  # Get the current window height

    # Position the menu frame on the left side of the window
    toggle_menu_fm.place(x=0, y=50, height=window_height, width=200)

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
