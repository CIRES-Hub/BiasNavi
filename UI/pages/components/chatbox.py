import dash_bootstrap_components as dbc
from dash import dcc, html


def chatbox():
    return dbc.Card(id="chat-box", children=[
        dbc.CardHeader(
            html.Div([

                html.Div([html.H4([html.I(className="bi bi-robot",style={"marginRight": "10pt"}), "Chat with BiasNavi"], style={"margin": "0","marginLeft":"0.8em"}, className="secondary-title"),
                          html.Div([html.P("Suggestion:", id="recommended-op", className="op-highlight"),
                          html.Span(
                            html.I(className="fas fa-question-circle"),
                            id="tooltip-op",
                            style={
                                "fontSize": "20px",
                                "color": "#aaa",
                                "cursor": "pointer",
                                "marginLeft": "5px",
                                "alignSelf": "center"
                            }
                          )], id="to-do-div",style={"display": "block"}),
                         ],style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                "width": "100%", "padding": "0pt 10pt 0pt 0pt"}),

                dbc.Tooltip(
                    "",
                    target="tooltip-op",
                    id="tooltip-expl",
                )
            ],
                id={"type": "toggle-btn", "index": 3},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.CardBody(
            [
                html.Div([


                html.Div(id='query-area', className='query-area'),

                dbc.Alert(
                    "Forget to import a dataset or enter a query?",
                    id="error-alert",
                    is_open=False,
                    dismissable=True,
                    color="danger",
                    duration=5000,
                ),
                dbc.Alert(
                    "",
                    id="report-alert",
                    is_open=False,
                    dismissable=True,
                    color="warning",
                    duration=5000
                ),
                html.Div([
                    dcc.Loading(
                        id="loading-1",
                        children=[
                            html.Div(id='next-suggested-questions', style={"marginBottom":"20px"}),
                            html.Div([
                                html.Button(id="common-question-btn", children="Common Questions",
                                            style={"backgroundColor": "white", "color": "grey", "border": "none","marginBottom":"5pt"}, )
                            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                      "width": "100%"}),
                            html.Div(
                                style={'position': 'relative', 'width': '100%'},
                                children=[
                                    html.Div(
                                        style={
                                            'position': 'relative',
                                            'width': '100%',
                                            'height': '120px',
                                            'borderRadius': '20px',
                                            'backgroundColor': '#f5f5f5',
                                            'padding': '10px 15px 40px 15px',
                                            'boxSizing': 'border-box',
                                            'overflow': 'hidden'
                                        },
                                        children=[
                                            dcc.Textarea(
                                                id='query-input',
                                                placeholder='Type your message here',
                                                className='query-input',
                                                style={
                                                    'width': '100%',
                                                    'height': '100%',
                                                    'resize': 'none',
                                                    'border': 'none',
                                                    'background': 'transparent',
                                                    'fontSize': '16px',
                                                    'overflowY': 'auto',
                                                    'outline': 'none',
                                                    'paddingRight': '5px'
                                                }
                                            ),
                                            html.Div(
                                                style={
                                                    'position': 'absolute',
                                                    'bottom': '5px',
                                                    'left': '15px',
                                                    'display': 'flex',
                                                    'gap': '8px',
                                                },
                                                children=[
                                                    html.Button(
                                                        children=[html.Span(className="fas fa-paper-plane"), "Send"],
                                                        id='send-button',
                                                        title="Send your message.",
                                                        n_clicks=0,
                                                        className='send-button'
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-rag",
                                                        children=html.Button(
                                                            "Doc",
                                                            id='RAG-button',
                                                            title="Upload a txt/pdf document as the description of the dataset.",
                                                            n_clicks=0,
                                                            className='send-button'
                                                        ),
                                                        multiple=False
                                                    ),
                                                    html.Button(
                                                        "RAG",
                                                        id='rag-switch',
                                                        title="Toggle RAG mode.",
                                                        n_clicks=0,
                                                        className='send-button'
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    dcc.Store(id="rag-state", data=False)
                                ]
                            )

                        ],
                        type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                    ),
                    html.Div([
                        dcc.Store(id="bias-stage-value", data=1),
                        dcc.Store(id="toggle-msg-value", data=1),
                        html.Button('Identify Bias',
                                    id={'type': 'spinner-btn', 'index': 3},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px'},
                                    title="Detect potential bias or fairness issues."),

                        html.I(
                            className="bi bi-arrow-right fade-in-arrow",
                            id="right-arrow-icon-1",
                            style={
                                "fontSize": "1.5rem",
                                "display": "none"
                            }
                        ),
                        html.Button('Measure Bias',
                                    id={'type': 'spinner-btn', 'index': 4},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Quantify the magnitude of detected biases."),
                        html.I(
                            className="bi bi-arrow-right fade-in-arrow",
                            id="right-arrow-icon-2",
                            style={
                                "fontSize": "1.5rem",
                                "display": "none"
                            }
                        ),
                        html.Button('Surface Bias',
                                    id={'type': 'spinner-btn', 'index': 5},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Present the identified biases clearly."),
                        html.I(
                            className="bi bi-arrow-right fade-in-arrow",
                            id="right-arrow-icon-3",
                            style={
                                "fontSize": "1.5rem",
                                "display": "none"
                            }
                        ),
                        html.Button('Adapt Bias',
                                    id={'type': 'spinner-btn', 'index': 6},
                                    n_clicks=0, className='primary-button',
                                    style={'margin': '10px', "display": "none"},
                                    title="Provide tools for mitigating biases."),

                        dcc.Store(id='sensitive-attr-store', data={})

                    ], id="bias-management-buttons", className="bias-buttons"),
                    # for experiment use only
                    html.Div([
                        html.Button('Adapt Bias',
                                id="baseline-mode-adapt-btn",
                                n_clicks=0, className='primary-button',
                                style={'margin': '10px', "display": "none"},
                                title="Provide tools for mitigating biases."),],
                        className="bias-buttons")

                ], style={"marginTop":"20px", "marginBottom":"10px"}),
            ], className='query')]
        ),



    ], className='card')
