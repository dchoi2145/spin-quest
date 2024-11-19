import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from open_root_file import find_first_event_with_data
from plot import generate_combined_heatmap_figure

# CONSTANTS
SPILL_PATH = "run_005591_spill_001903474_sraw.root"

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

# Set initial event number
initial_event_number = find_first_event_with_data(SPILL_PATH)

# Generate figure for the initial event
initial_heatmap = generate_combined_heatmap_figure(SPILL_PATH, initial_event_number)

# Layout for each page
def create_page_layout(title, heatmap_fig):
    return html.Div([
        html.H1(title, className="text-center my-4"),
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
        dcc.Graph(
            figure=heatmap_fig,
            id="heatmap-graph",
            style={"width": "100%"},
            config={"displayModeBar": True, "displaylogo": False}
        ),
        #dcc.Interval(
        #    id="interval-component",
        #    interval=5000,  # Update every 5 seconds
        #    n_intervals=0
        #)
    ])

# App layout with default content to prevent errors
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    html.Div(id="page-content", children=create_page_layout("All Stations", initial_heatmap))
])

# Callback to update the content based on the URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/stations":
        return create_page_layout("All Stations", initial_heatmap)
    elif pathname == "/hodoscopes":
        return create_page_layout("Hodoscopes", initial_heatmap)
    elif pathname == "/prop-detectors":
        return create_page_layout("Prop Detectors", initial_heatmap)
    elif pathname == "/dp-detectors":
        return create_page_layout("DP Detectors", initial_heatmap)
    else:
        return create_page_layout("All Stations", initial_heatmap)  # Default page

# Callback to update the heatmap based on button click 
@app.callback(
    Output('heatmap-graph', 'figure'),
    Input('update-button', 'n_clicks'),
    State('event-number-input', 'value'),
    prevent_initial_call=True 
)
def update_heatmap(n_clicks, event_number):
    if n_clicks is None:  # Don't update on initial load
        raise dash.no_update
        
    # Generate new heatmap figure
    return generate_combined_heatmap_figure(SPILL_PATH, event_number)

# callback for interval
#@app.callback(
#    Output('heatmap-graph', 'figure'),
#    Input('interval-component', 'n_intervals'),
#    State('event-number-input', 'value'),
#    prevent_initial_call=True
#)
#def update_heatmap_interval(n_intervals, event_number):
#    return generate_combined_heatmap_figure(SPILL_PATH, event_number)

if __name__ == "__main__":
    app.run_server(debug=False)
    
