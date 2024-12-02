import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from file_read import read_json, get_detector_info, find_first_non_empty, read_events
from plot import create_detector_heatmaps

# CONSTANTS
SPILL_PATH = "run_005591_spill_001903474_sraw.root"
SPECTROMETER_INFO_PATH = "spectrometer.csv"
DETECTOR_MAP_FILE = "detector_map.json"

# Load detector map from JSON
detector_map = read_json(DETECTOR_MAP_FILE)

# Flatten detector_map into group_to_detectors
group_to_detectors = {}
for category, groups in detector_map.items():
    for group_name, detectors in groups.items():
        group_to_detectors[group_name] = detectors

# Get detector info
detector_name_to_id_elements, max_elements = get_detector_info(SPECTROMETER_INFO_PATH)
detector_ids, element_ids = read_events(SPILL_PATH)
initial_event_number = find_first_non_empty(detector_ids)

# Generate initial heatmap
initial_heatmap = create_detector_heatmaps(
    detector_ids[initial_event_number],
    element_ids[initial_event_number],
    detector_name_to_id_elements,
    max_elements,
)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Navbar
def navbar(current_path):
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Nav(
                    [
                        dbc.NavLink("Main View", href="/main", active=(current_path == "/main" or current_path == "/")),
                        dbc.NavLink("Checkbox View", href="/checkbox", active=(current_path == "/checkbox")),
                    ],
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-4",
    )

# Main View layout
def main_view_layout(title, heatmap_fig, current_path):
    return html.Div([
        navbar(current_path),
        html.H1(title, className="text-center my-4"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Event Number:"),
                    dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=1, step=1),
                    dbc.Button("Update Plot", id="update-button", color="primary", n_clicks=0),
                ], width=12, className="text-center mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="heatmap-graph", figure=heatmap_fig),
                ]),
            ]),
        ]),
    ])

# Checkbox View layout
def checkbox_view_layout(title, heatmap_fig, current_path):
    return html.Div([
        navbar(current_path),
        html.H1(title, className="text-center my-4"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Event Number:"),
                    dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=1, step=1),
                    dbc.Button("Update Plot", id="update-button", color="primary", n_clicks=0),
                ], width=12, className="text-center mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="heatmap-graph", figure=heatmap_fig),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Detector Groups to Display:"),
                    dcc.Checklist(
                        id="grouped-detector-checklist",
                        options=[{"label": group, "value": group} for group in group_to_detectors],
                        value=list(group_to_detectors),  # All selected by default
                        inline=True,
                    ),
                ], width=12, className="mb-3"),
            ]),
        ]),
    ])

# App layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
])

# Callback to render the correct page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page(pathname):
    if pathname == "/checkbox":
        return checkbox_view_layout("Checkbox View", initial_heatmap, pathname)
    else:
        return main_view_layout("Main View", initial_heatmap, pathname)

# Callback to update the heatmap based on selected groups
@app.callback(
    Output("heatmap-graph", "figure"),
    [Input("update-button", "n_clicks"),
     Input("grouped-detector-checklist", "value")],
    State("event-number-input", "value"),
)
def update_heatmap(n_clicks, selected_groups, event_number):
    # Get detectors to display based on selected groups
    selected_detectors = [
        detector for group in selected_groups for detector in group_to_detectors[group]
    ]

    # Update detector visibility
    for detector in detector_name_to_id_elements:
        detector_name_to_id_elements[detector][-1] = detector in selected_detectors

    # Generate new heatmap
    return create_detector_heatmaps(
        detector_ids[event_number],
        element_ids[event_number],
        detector_name_to_id_elements,
        max_elements,
    )

if __name__ == "__main__":
    app.run_server(debug=False)
