import dash
import dash_bootstrap_components as dbc

from dash import dcc, html, Input, Output, State
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

# Layout with event selection, update button, and plot display
app.layout = html.Div([
    navbar,
    
    html.H1("Interactive Detector Hit Viewer", className="text-center my-4"),
    
    html.Div([
        html.Label("Select Event Number:", className="text-center font-weight-bold me-3"),
        dcc.Input(
            id="event-number-input", 
            type="number", 
            value=initial_event_number, 
            min=1, 
            step=1,
            className="me-3"
        ),
        dbc.Button(
            "Update Plot", 
            id="update-button", 
            color="primary", 
            n_clicks=0
        )
    ], className="text-center my-4"),

    html.Div(id="container", className="container-fluid", children=[
        dcc.Graph(
            figure=initial_heatmap, 
            id="heatmap-graph", 
            style={"width": "100%"},
            config={
                "displayModeBar": True,
                "displaylogo": False
            }
        )
    ])
])

# Callback to update the heatmap only when the button is clicked
@app.callback(
    Output('heatmap-graph', 'figure'),
    Input('update-button', 'n_clicks'),
    State('event-number-input', 'value')
)
def update_heatmap(n_clicks, event_number):
    if n_clicks is None:
        return dash.no_update
    
    if event_number is None:
        return dash.no_update
    
    heatmap_fig = generate_combined_heatmap_figure(SPILL_PATH, event_number)
    return heatmap_fig

if __name__ == "__main__":
    app.run_server(debug=False)
