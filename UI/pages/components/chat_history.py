import dash_bootstrap_components as dbc
from dash import dcc, html

def chat_history():
    return  dbc.Card(id = "chat_history", children = [
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-right", id={"type": "toggle-icon", "index": 6},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Chat History", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 6},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
        dbc.CardBody([
            html.Div(id="chat-history-content")
        ]),
        id={"type": "collapse-card", "index": 6},
        is_open = False
        )

    ], className="card", style={"display": "none"})