import dash
from dash import html, Input, Output, State, MATCH, ALL, ctx
import dash_bootstrap_components as dbc
from UI.app import app
@app.callback(
    Output({"type": "collapse-card", "index": MATCH}, "is_open"),
    Output({"type": "toggle-icon", "index": MATCH}, "className"),
    Input({"type": "toggle-btn", "index": MATCH}, "n_clicks"),
    State({"type": "collapse-card", "index": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_card(n_clicks, is_open):
    return not is_open, "bi bi-chevron-down" if not is_open else "bi bi-chevron-right"

