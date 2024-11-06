import dash
import dash_bootstrap_components as dbc

from dash import dcc, html, Input, Output
from open_root_file import find_first_event_with_data
from plot import generate_combined_heatmap_figure

# CONSTANTS
SPILL_PATH = "run_005591_spill_001903474_sraw.root"

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Navbar with "Menu" dropdown
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Menu", className="me-auto"),
        dbc.DropdownMenu(
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Stations", href="#"),
                dbc.DropdownMenuItem("Hodoscopes", href="#"),
                dbc.DropdownMenuItem("Prop Detectors", href="#"),
                dbc.DropdownMenuItem("DP Detectors", href="#"),
            ],
            nav=True,
            in_navbar=True,
            toggle_style={"cursor": "pointer"},
            direction="down"  # Ensure dropdown opens downwards
        ),
    ]),
    color="dark",
    dark=True,
    className="mb-4"
)


# Set initial event number
initial_event_number = find_first_event_with_data(SPILL_PATH)

# Generate figure for the initial event
initial_heatmap = generate_combined_heatmap_figure(SPILL_PATH, initial_event_number)

# Layout with event selection, plot display, and Navbar
app.layout = html.Div([
    navbar,
    
    html.H1("Interactive Detector Hit Viewer", className="text-center my-4"),
    
    html.Div([
        html.Label("Select Event Number:", className="text-center font-weight-bold"),
        dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=1, step=1)
    ], className="text-center my-4"),

    html.Div(id="container", className="container-fluid", children=[
        dcc.Graph(
            figure=initial_heatmap, 
            id="heatmap-graph", 
            style={"width": "100%"},
            config={
                "displayModeBar": True,      # Keep mode bar for zoom/pan features
                "displaylogo": False         # Disable the Plotly logo (blue button)
            }
        )
    ]),

    # Interval component for live updating
    dcc.Interval(
        id="interval-component",
        interval=5*1000,  # Update every 5 seconds (adjust as needed)
        n_intervals=0
    )
])

# Callback to update the heatmap based on selected event number and interval
@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('event-number-input', 'value'),
     Input('interval-component', 'n_intervals')]  # Trigger on interval as well
)
def update_heatmap(event_number, n_intervals):
    if event_number is None:
        return dash.no_update
    
    heatmap_fig = generate_combined_heatmap_figure(SPILL_PATH, event_number)
    return heatmap_fig

if __name__ == "__main__":
    app.run_server(debug=False)
