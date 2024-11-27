import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from file_read import read_json, get_detector_info, find_first_non_empty, read_events
from plot import generate_combined_heatmap_figure

# CONSTANTS
SPILL_PATH = "run_005591_spill_001903474_sraw.root"
SPECTROMETER_INFO_PATH = "spectrometer.csv"
DETECTOR_MAP = "detector_map.json"

# Initialize the Dash app with Bootstrap theme and suppress callback exceptions
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Navbar with "Menu" dropdown
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Nav(
                [
                    dbc.DropdownMenu(
                        label="Menu",
                        children=[
                            dbc.DropdownMenuItem("All Stations", href="/stations"),
                            dbc.DropdownMenuItem("Hodoscopes", href="/hodoscopes"),
                            dbc.DropdownMenuItem("Prop Detectors", href="/prop-detectors"),
                            dbc.DropdownMenuItem("DP Detectors", href="/dp-detectors"),
                        ],
                        nav=True,
                        in_navbar=True,
                        toggle_style={"cursor": "pointer"},
                        direction="down"
                    )
                ],
                navbar=True,
                className="ms-3"
            ),
        ],
        fluid=True
    ),
    color="dark",
    dark=True,
    className="mb-4"
)

# Get detector names
detector_name_to_id_elements = get_detector_info(SPECTROMETER_INFO_PATH)
initial_detector_names = [key for key in detector_name_to_id_elements]

# Debugging: Print all detector names and their configurations
print("Detector Configurations:")
for detector, details in detector_name_to_id_elements.items():
    print(f"{detector}: {details}")

# Get events from spill file
detector_ids, element_ids = read_events(SPILL_PATH)

# Generate figure for the initial event
initial_heatmap = generate_combined_heatmap_figure(SPILL_PATH, initial_event_number, detector_name_to_id_elements)

# Layout for each page
def create_page_layout(title, heatmap_fig, include_checkboxes=False, specific_checkboxes=None):
    layout = html.Div([
        html.H1(title, className="text-center my-4"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Event Number:", className="me-2"),
                    dcc.Input(
                        id="event-number-input",
                        type="number",
                        value=initial_event_number,
                        min=1,
                        step=1,
                        className="me-2"
                    ),
                    dbc.Button(
                        "Update Plot",
                        id="update-button",
                        color="primary",
                        n_clicks=0
                    ),
                ], width=12, className="text-center mb-3")
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=heatmap_fig,
                        id="heatmap-graph",
                        style={"width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False}
                    )
                ])
            ]),
        ]),
    ])

    if include_checkboxes and specific_checkboxes:
        # Add the checkbox section with specific options
        layout.children.append(
            dbc.Row([
                dbc.Col([
                    html.Label("Select Detectors to Display:", className="mb-2"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Checklist(
                                id="detector-checklist",
                                options=[{'label': name, 'value': name} for name in specific_checkboxes],
                                value=specific_checkboxes,
                                inline=True,
                                className="detector-checklist"
                            )
                        ])
                    ])
                ], width=12, className="mb-3")
            ])
        )

    return layout

# App layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    html.Div(id="page-content", children=create_page_layout("All Stations", initial_heatmap, include_checkboxes=False))
])

# Callback to update the content based on the URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/stations":
        return create_page_layout("All Stations", initial_heatmap, include_checkboxes=False)
    elif pathname == "/hodoscopes":
        # Adjust keys based on debug output
        detector_keys = ["D0V", "D0Vp", "D0Xp"]  # Match exact names
        valid_detectors = {key: detector_name_to_id_elements[key] for key in detector_keys if key in detector_name_to_id_elements}
        print("Valid Detectors for Hodoscopes:", valid_detectors.keys())  # Debugging output

        if valid_detectors:
            hodoscope_heatmap = generate_combined_heatmap_figure(SPILL_PATH, initial_event_number, valid_detectors)
            return create_page_layout("Hodoscopes", hodoscope_heatmap, include_checkboxes=True, specific_checkboxes=list(valid_detectors.keys()))
        else:
            return html.Div([
                html.H1("Error: No valid detectors found", className="text-center my-4"),
                html.P("The requested detectors (D0V, D0Vp, D0Xp) are not available. Please check the detector configuration."),
            ])
    elif pathname == "/prop-detectors":
        return create_page_layout("Prop Detectors", initial_heatmap, include_checkboxes=True, specific_checkboxes=initial_detector_names)
    elif pathname == "/dp-detectors":
        return create_page_layout("DP Detectors", initial_heatmap, include_checkboxes=True, specific_checkboxes=initial_detector_names)
    else:
        return create_page_layout("All Stations", initial_heatmap, include_checkboxes=False)  # Default page

# Callback to update the heatmap based on button click for the hodoscope page
@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('update-button', 'n_clicks'),
     Input('detector-checklist', 'value')],
    [State('event-number-input', 'value')],
    prevent_initial_call=True
)
def update_heatmap(n_clicks, selected_detectors, event_number):
    # Only allow updates for the detectors on the Hodoscope page
    detector_keys = ["D0V", "D0Vp", "D0Xp"]  # Match exact names
    valid_detectors = {key: detector_name_to_id_elements[key] for key in detector_keys if key in detector_name_to_id_elements}

    # Update only the selected detectors
    for key in valid_detectors.keys():
        if key in selected_detectors:
            valid_detectors[key][2] = True  # Enable detector
        else:
            valid_detectors[key][2] = False  # Disable detector

    # Generate the updated heatmap
    return generate_combined_heatmap_figure(SPILL_PATH, event_number, valid_detectors)

if __name__ == "__main__":
    app.run_server(debug=False)
