import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_daq as daq

def rag():
    return dbc.Card(id="rag-card", style={'display': 'block'}, children=[
            html.Div([
                # RAG display area
                html.Div([
                    html.H4("RAG View", style={'paddingLeft': 0}, className="secondary-title"),
                    html.Div(
                        [
                            daq.ToggleSwitch(
                                id='rag-switch',
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
        ], className='card')