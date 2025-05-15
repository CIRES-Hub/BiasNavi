import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_editor_components
def code_view():
    return dbc.Card(id="code-view", children=[
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
            ],label="Python Sandbox"),
        ]
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
        ], id="python-code-console",style={"display":"none"}),
    ], style={'padding': '15px'})
