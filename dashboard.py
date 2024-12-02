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

# Define excluded detectors
excluded_detectors = ["D1V", "D1Vp", "D1X", "D1Xp", "D1U", "D1Up"]
excluded_detector_ids = [detector_name_to_id_elements[d][0] for d in excluded_detectors if d in detector_name_to_id_elements]

# Remove excluded detectors from detector_name_to_id_elements
filtered_detector_name_to_id_elements = {
    key: value
    for key, value in detector_name_to_id_elements.items()
    if key not in excluded_detectors
}

# Filter out excluded detectors from the event data
def filter_excluded(detector_ids, element_ids, excluded_ids):
    filtered_detector_ids = []
    filtered_element_ids = []

    for det_id, elem_id in zip(detector_ids, element_ids):
        if det_id not in excluded_ids:
            filtered_detector_ids.append(det_id)
            filtered_element_ids.append(elem_id)

    return filtered_detector_ids, filtered_element_ids

# Filter initial event data
filtered_detector_ids, filtered_element_ids = filter_excluded(
    detector_ids[initial_event_number], element_ids[initial_event_number], excluded_detector_ids
)

# Generate initial heatmap
main_heatmap = create_detector_heatmaps(
    filtered_detector_ids,
    filtered_element_ids,
    filtered_detector_name_to_id_elements,
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
def main_view_layout(title, current_path):
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
                    dcc.Graph(id="heatmap-graph", figure=main_heatmap),
                ]),
            ]),
        ]),
    ])

# Checkbox View layout
def checkbox_view_layout(title, current_path):
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
                    dcc.Graph(id="heatmap-graph", figure=main_heatmap),
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
        return checkbox_view_layout("Checkbox View", pathname)
    else:
        return main_view_layout("Main View", pathname)

# Callback to update the heatmap dynamically
@app.callback(
    Output("heatmap-graph", "figure"),
    [Input("update-button", "n_clicks"),
     Input("grouped-detector-checklist", "value"),
     State("event-number-input", "value")],
)
def update_heatmap(n_clicks, selected_groups, event_number):
    # Get detectors to display based on selected groups
    if selected_groups:
        selected_detectors = [
            detector for group in selected_groups for detector in group_to_detectors[group]
        ]
    else:
        selected_detectors = []

    # Update detector visibility
    for detector in filtered_detector_name_to_id_elements:
        filtered_detector_name_to_id_elements[detector][-1] = detector in selected_detectors

    # Filter data for the updated event number
    filtered_ids, filtered_elements = filter_excluded(
        detector_ids[event_number], element_ids[event_number], excluded_detector_ids
    )

    # Generate new heatmap
    return create_detector_heatmaps(
        filtered_ids,
        filtered_elements,
        filtered_detector_name_to_id_elements,
        max_elements,
    )

if __name__ == "__main__":
    app.run_server(debug=False)
