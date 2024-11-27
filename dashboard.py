import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from file_read import read_json, get_detector_info, find_first_non_empty, read_events
from plot import generate_combined_heatmap_figure

# CONSTANTS
SPILL_PATH = "run_005591_spill_001903474_sraw.root"
SPECTROMETER_INFO_PATH = "spectrometer.csv"
DETECTOR_MAP = "detector_map.json"

# Get detector map info
detector_info = read_json(DETECTOR_MAP)

# Get spectrometer info
detector_name_to_id_elements = get_detector_info(SPECTROMETER_INFO_PATH)
initial_detector_names = [key for key in detector_name_to_id_elements]

# Debugging: Print all detector names and their configurations
print("Detector Configurations:")
for detector, details in detector_name_to_id_elements.items():
    print(f"{detector}: {details}")

# Get events from spill file
detector_ids, element_ids = read_events(SPILL_PATH)
initial_event_number = find_first_non_empty(detector_ids)

# Generate figure for the initial event
initial_heatmap = generate_combined_heatmap_figure(SPILL_PATH, detector_ids[initial_event_number], element_ids[initial_event_number], detector_name_to_id_elements)

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
                            dbc.DropdownMenuItem("All Stations", href="/all-stations")
                        ] + [dbc.DropdownMenuItem(detector_type, href="/" + detector_type) for detector_type in detector_info],
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

# Layout for each page
def create_page_layout(title, heatmap_fig, checkboxes=None):
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

    if checkboxes:
        # Add the checkbox section with specific options
        layout.children.append(
            dbc.Row([
                dbc.Col([
                    html.Label("Select Detectors to Display:", className="mb-2"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Checklist(
                                id="detector-checklist",
                                options=[{'label': name, 'value': name} for name in checkboxes],
                                value=checkboxes,
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
    html.Div(id="page-content", children=create_page_layout("All Stations", initial_heatmap, checkboxes=False))
])

# Callback to update the content based on the URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/all-stations":
        return create_page_layout("All Stations", initial_heatmap, checkboxes=False)
    else:
        pathname = pathname[1:]
        detector_keys = [name for detector in detector_info[pathname] for name in detector_info[pathname][detector]]
        valid_detectors = {key: detector_name_to_id_elements[key] for key in detector_keys if key in detector_name_to_id_elements}
        print("Valid Detectors for {}:".format(pathname), valid_detectors.keys())  # Debugging output

        if valid_detectors:
            heatmap = generate_combined_heatmap_figure(SPILL_PATH, detector_ids[initial_event_number], element_ids[initial_event_number], detector_name_to_id_elements)
            return create_page_layout(pathname, heatmap, checkboxes=list(valid_detectors.keys()))
        else:
            return html.Div([
                html.H1("Error: No valid detectors found", className="text-center my-4"),
                html.P("The requested detectors {} are not available. Please check the detector configuration.".format(detector_keys)),
            ])
        
# Callback to update the heatmap based on button click for the hodoscope page
@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('update-button', 'n_clicks'),
     Input('detector-checklist', 'value')],
    [State('event-number-input', 'value')],
    prevent_initial_call=True
)
def update_heatmap(n_clicks, selected_detectors, event_number):
    for key in detector_name_to_id_elements:
        if key in selected_detectors:
            detector_name_to_id_elements[key][2] = True  # Enable detector
        else:
            detector_name_to_id_elements[key][2] = False  # Disable detector

    # Generate the updated heatmap
    return generate_combined_heatmap_figure(SPILL_PATH, event_number, detector_name_to_id_elements)

if __name__ == "__main__":
    app.run_server(debug=False)
