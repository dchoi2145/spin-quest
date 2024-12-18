import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ALL
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

# Layout
def layout():
    # Create individual checkbox elements
    checkbox_elements = [
        html.Div(
            [
                dcc.Checklist(
                    options=[{"label": group, "value": group}],
                    value=[group],  # Preselect the checkbox
                    id={"type": "group-checklist", "index": group},
                    inline=True,
                )
            ],
            style={"display": "inline-block", "margin-right": "10px"}
        )
        for group in group_to_detectors
    ]

    return html.Div([
        html.H1(
            "Detector Heatmap", 
            className="text-center", 
            style={"margin-bottom": "10px", "margin-top": "20px"}
        ),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Event Number:", className="me-2"),
                    dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=1, step=1),
                    dbc.Button("Update Plot", id="update-button", color="primary", className="ms-2"),
                ], width=12, className="text-center mb-2"),
            ]),
            dcc.Graph(id="heatmap-graph", figure=main_heatmap, style={"margin-bottom": "5px"}),  # Further reduced margin-bottom
            dbc.Card(
                [
                    dbc.CardHeader(
                        "Select Detector Groups to Display:", 
                        style={"font-weight": "bold", "font-size": "1.2rem", "background-color": "#f8f9fa"}
                    ),
                    dbc.CardBody(
                        html.Div(checkbox_elements, style={"white-space": "nowrap", "overflow-x": "auto"})
                    ),
                ],
                style={"margin-top": "2px", "border": "1px solid #ddd", "border-radius": "5px"}  # Minimal margin-top
            ),
        ], style={"padding": "10px"}),
    ])


app.layout = layout()

# Callback to update the heatmap dynamically
@app.callback(
    Output("heatmap-graph", "figure"),
    [Input("update-button", "n_clicks"),
     Input({"type": "group-checklist", "index": ALL}, "value")],
    State("event-number-input", "value"),
)
def update_heatmap(n_clicks, selected_groups, event_number):
    # Flatten selected groups from nested lists
    selected_groups = [item for sublist in selected_groups for item in sublist if item]

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
