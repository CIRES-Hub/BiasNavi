import dash_bootstrap_components as dbc
from dash import dcc, html


def chatbox():
    return dbc.Card(id="chat-box", children=[
                html.Div([

                    html.Div([
                        html.H4("Chat with BiasNavi", className="secondary-title"),
                        html.Button(id="common-question-btn", children="Common Questions",
                                    style={"backgroundColor": "white", "color": "grey", "border": "none"}, )
                    ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                              "width": "100%"}),
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
                ], className='query')
            ], className='card')