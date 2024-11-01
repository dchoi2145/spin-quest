import dash
from dash import dcc, html
import plotly.graph_objects as go
import json
from open_root_file import read_event, get_total_spills 
from plot import create_individual_heatmaps

# Load Bootstrap and initialize Dash app
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Load station_map from JSON file
with open("detector_map.json", "r") as file:
    station_map = json.load(file)

file_path = r"D:\Documents\GitHub\spin-quest\run_data\run_005591\run_005591_spill_001903474_sraw.root"

# Function to find the first event with data
def find_first_event_with_data(starting_event=1):
    for event_number in range(starting_event, get_total_spills(file_path)): 
        detector_ids, element_ids = read_event(file_path, event_number)
        if len(detector_ids) > 0 and len(element_ids) > 0:  # Check if data is non-empty
            return event_number
    return starting_event  # Default to starting_event if no data is found

# Set initial event number to the first event with data
initial_event_number = find_first_event_with_data()

# Function to load data for a specific event and generate figures
def generate_figures(event_number):
    # Fetch detector_ids and element_ids for the specified event
    detector_ids, element_ids = read_event(file_path, event_number)
    
    print("Detector IDs:", detector_ids)
    print("Element IDs:", element_ids)
    
    # Selected stations for visualization
    selected_stations = ["Station1", "Station2", "Station3 +", "Station3 -",
                         "Hodoscope1", "Hodoscope2", "Hodoscope3", "Hodoscope4",
                         "Hodoscope5", "DP-1", "DP-2", "Prop1", "Prop2", "Prop3"]

    # Generate figures
    figures = create_individual_heatmaps(detector_ids, element_ids, station_map, selected_stations)
    return figures

# Generate figures for the initial event
figures = generate_figures(initial_event_number)

# Layout with event selection and plot display
app.layout = html.Div([
    html.H1("Interactive Detector Hit Viewer", className="text-center my-4"),
    html.P("Explore detector hit data interactively. Hover over the points to get details on element and detector numbers.", className="text-center text-muted"),
    
    html.Div([
        html.Label("Select Event Number:", className="text-center font-weight-bold"),
        dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=1, step=1)
    ], className="text-center my-4"),

    html.Div(id="container", className="container"),

    # Interval component for live updating
    dcc.Interval(
        id="interval-component",
        interval=5*1000,  # Update every 5 seconds (adjust as needed)
        n_intervals=0
    )
])

# Callback to update plots based on selected event number and interval
@app.callback(
    dash.Output('container', 'children'),
    [dash.Input('event-number-input', 'value'),
     dash.Input('interval-component', 'n_intervals')]  # Trigger on interval as well
)
def update_event_data(event_number, n_intervals):
    if event_number is None:
        return dash.no_update
    
    # Generate figures for the selected event
    figures = generate_figures(event_number)
    
    # Create new plot components with updated figures
    rows = []
    row = []
    for index, fig in enumerate(figures.values()):
        row.append(html.Div(className="col-md-6 mb-4 graph-container", children=[
            dcc.Graph(figure=fig, className="dash-graph")
        ]))
        if (index + 1) % 2 == 0:  # Every two figures, create a new row
            rows.append(html.Div(className="row", children=row))
            row = []
    
    # Add any remaining figures if total count is odd
    if row:
        rows.append(html.Div(className="row", children=row))

    return rows

if __name__ == "__main__":
    app.run_server(debug=False)