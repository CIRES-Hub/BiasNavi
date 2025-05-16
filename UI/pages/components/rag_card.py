import dash_bootstrap_components as dbc
from click import style
from dash import dcc, html
import dash_daq as daq

def rag():
    return dbc.Card(id="rag-card", style={'display': 'none'}, children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-right", id={"type": "toggle-icon", "index": 5},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("RAG View", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 5},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [
                    html.Div([
                        # RAG display area
                        html.Div([
                            html.Div(
                                [
                                    daq.ToggleSwitch(
                                        id='rag-toggle',
                                        value=False,
                                        color="#67b26f",  # Green gradient for ON (matches your theme)
                                        size=48,  # Bigger for clarity (default is 36)
                                    ),
                                    html.Div(id='rag-switch-status', children="RAG is OFF.")
                                ],
                                style={"display": "flex", "alignItems": "center", "gap": "12px"}
                            )

                        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                  "width": "100%"}),
                        dcc.Loading(
                            id="loading-2",
                            children=[
                                html.Div(id='RAG-area', className='RAG-area')],
                            type="dot",  # Choose from "graph", "cube", "circle", "dot", or "default"
                        ),
                        # Message input row

                    ], className='query'),
                ]),
            id={"type": "collapse-card", "index": 5},
            is_open=False
        )
    ], className='card')