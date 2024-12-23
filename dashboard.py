import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ALL
from file_read import read_json, get_detector_info, find_first_non_empty, read_events, choose_root
from plot import create_detector_heatmaps, create_video

# CONSTANTS
SPECTROMETER_INFO_PATH = "spectrometer.csv"
DETECTOR_MAP_FILE = "detector_map.json"

# Load detector map from JSON
detector_map = read_json(DETECTOR_MAP_FILE)

# Flatten detector_map into group_to_detectors
group_to_detectors = {group_name: detectors for category, groups in detector_map.items() for group_name, detectors in groups.items()}

# Get detector info
detector_name_to_id_elements, max_elements = get_detector_info(SPECTROMETER_INFO_PATH)
detector_ids, element_ids = read_events(choose_root())
initial_event_number = find_first_non_empty(detector_ids)

# Define excluded detectors
excluded_detectors = ["D1V", "D1Vp", "D1X", "D1Xp", "D1U", "D1Up"]
excluded_detector_ids = [detector_name_to_id_elements[d][0] for d in excluded_detectors if d in detector_name_to_id_elements]

# Create video if user requests it 
video_response = input("Do you want to process the events in this root file into a video? (y/n): ")
if video_response.lower() == 'y':
    video_name = input("What name do you want the video to be? (NO FILE EXTENSION): ")
    create_video(detector_ids, element_ids, detector_name_to_id_elements, max_elements, initial_event_number, excluded_detector_ids, video_name + ".mp4")
    print("Done!")

# Filter initial event data
initial_detector_ids, initial_element_ids = detector_ids[initial_event_number], element_ids[initial_event_number]

# Generate initial heatmap
main_heatmap = create_detector_heatmaps(
    initial_detector_ids,
    initial_element_ids,
    detector_name_to_id_elements,
    max_elements,
    excluded_detector_ids
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
                    dcc.Input(id="event-number-input", type="number", value=initial_event_number, min=0, step=1),
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
    for detector in detector_name_to_id_elements:
        detector_name_to_id_elements[detector][-1] = detector in selected_detectors

    # Generate new heatmap
    return create_detector_heatmaps(
        detector_ids[event_number],
        element_ids[event_number],
        detector_name_to_id_elements,
        max_elements,
        excluded_detector_ids
    )

if __name__ == "__main__":
    app.run_server(debug=False)
