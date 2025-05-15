import dash_bootstrap_components as dbc
from dash import dcc, html,dash_table

def report_view():
    return dbc.Card(body=True, id="report-view", className="card", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 2},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Bias Management", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 2},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem","borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody([
                html.Div([
                    # Button row
                    html.Div([
                        html.Button('Identify Bias',
                                    id={'type': 'spinner-btn', 'index': 3},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px'},
                                    title="Detect potential bias or fairness issues."),
                        html.Button('Measure Bias',
                                    id={'type': 'spinner-btn', 'index': 4},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Quantify the magnitude of detected biases."),
                        html.Button('Surface Bias',
                                    id={'type': 'spinner-btn', 'index': 5},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Present the identified biases clearly."),
                        html.Button('Adapt Bias',
                                    id={'type': 'spinner-btn', 'index': 6},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Provide tools for mitigating biases.")
                    ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'}),

                    # Hidden store
                    dcc.Store(id='sensitive-attr-store', data={}),

                    # Dropdown for target attribute
                    html.Div([
                        html.Label("Target Attribute:",
                                   style={"marginRight": "10px", "whiteSpace": "nowrap"}),
                        dcc.Dropdown(
                            id='column-names-dropdown',
                            placeholder="Choose a column as the target attribute",
                            style={"flex": "1"}
                        )
                    ], style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginTop": "20px",
                        "marginBottom": "20px"
                    }),

                    # Alert for bias report
                    dbc.Alert(
                        "",
                        id="report-alert",
                        is_open=False,
                        dismissable=True,
                        color="warning",
                        duration=5000
                    ),

                    # Output areas
                    html.Div(id="bias-identifying-area", className="section"),
                    html.Div(id='bias-measuring-area', className="table-container section"),
                    html.Div(id='bias-surfacing-area', className="section"),
                    html.Div(id='bias-adapting-area', className="section"),
                ])
            ]),
            id={"type": "collapse-card", "index": 2},
            is_open=True
        ),
    ])