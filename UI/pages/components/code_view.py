import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_editor_components
def code_view():
    return dbc.Card(id="code-view", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 7},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Chart & Code", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 7},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [
                    dbc.Tabs([
                        dbc.Tab([
                            html.Div([
                                # Chat display area
                                # html.Div([
                                #     html.H4("Charts", className="secondary-title")
                                # ], className="query-header"),
                                html.Div([], id='llm-media-area')
                            ], className='llm-chart', style={'overflowX': 'auto'})
                        ], label="Chart"),

                        dbc.Tab([
                            html.Div([
                                html.Div([
                                    html.Div([dash_editor_components.PythonEditor(id='commands-input', style={'overflow': "auto"}, value="")],
                                             className='commands_editor'),
                                ], id="python-code-editor", style={"marginTop":"20pt"}),
                                # html.Div([
                                #     # html.H4("Python Sandbox", style={'paddingLeft': 0}, className="secondary-title"),
                                #
                                # ], style={"display": "flex", "alignItems": "center",
                                #           "justifyContent": "space-between",
                                #           "width": "100%"}),

                            ]),
                            html.Div([
                                html.Span(
                                    html.I(className="fas fa-question-circle"),
                                    id="tooltip-code",
                                    style={
                                        "fontSize": "20px",
                                        "color": "#aaa",
                                        "cursor": "pointer",
                                        "marginLeft": "5px",
                                        "alignSelf": "center"
                                    }
                                ),
                                dbc.Button("Run", id={'type': 'spinner-btn', 'index': 9}, n_clicks=0,
                                           className='primary-button'),
                            ], className='right-align-div'),
                            dbc.Tooltip(
                                "The variable df is a reference of the Pandas dataframe of the current dataset. "
                                "Any Modification on it will be reflected in the data view",
                                target="tooltip-code",
                            ),
                            html.Div([
                                html.Div([
                                    html.H4("Console", className="secondary-title")
                                ], className="query-header"),
                                dcc.Loading(
                                    id="loading-1",
                                    children=[html.P(id='console-area', className='commands_result')],
                                    type="default",
                                ),
                            ], id="python-code-console", style={"display": "none"})
                        ],label="Python Sandbox"),
                    ]
                    )
                    ,]
            ),
            id={"type": "collapse-card", "index": 7},
            is_open=True
        )
    ], className="card")
