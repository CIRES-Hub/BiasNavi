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
                          )], id="to-do-div",style={"display": "none"}),
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
                                style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', "gap":"10px"},
                                children=[
                                    dcc.Input(id='query-input', type='text', className='query-input',
                                              placeholder='Type your message here'),
                                    html.Button(html.Span(className="fas fa-paper-plane"), id='send-button',
                                                title="Send your message.", n_clicks=0,
                                                className='send-button'),

                                    dcc.Upload(id="upload-rag",
                                               children=html.Button(html.Span(className="fas fa-file"),
                                                                    id='RAG-button',
                                                                    title="Upload supplementary document to enhance bias management.",
                                                                    n_clicks=0,
                                                                    className='send-button'),
                                               multiple=True),
                                    html.Button("RAG", id='rag-switch',
                                                title="Enable/Disable information retrieval in the supplementary document.", n_clicks=0,
                                                className='send-button'),
                                    dcc.Store(id="rag-state", data=False)
                                ]),

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

                ], style={"marginTop":"20px", "marginBottom":"10px"}),
            ], className='query')]
        ),



    ], className='card')
