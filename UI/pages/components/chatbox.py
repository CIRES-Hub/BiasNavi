import dash_bootstrap_components as dbc
from dash import dcc, html


def chatbox():
    return dbc.Card(id="chat-box", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 3},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Chat with BiasNavi", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 3},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
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
                                                                        title="Upload your document for RAG.",
                                                                        n_clicks=0,
                                                                        className='send-button'),
                                                   multiple=True),
                                    ])
                            ],
                            type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                        ),

                    ], style={"marginTop":"20px", "marginBottom":"10px"}),
                ], className='query')]
            ),
            id={"type": "collapse-card", "index": 3},
            is_open=True
        )


    ], className='card')
