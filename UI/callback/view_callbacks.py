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

@app.callback(
    Output({"type": "collapse-msg", "index": MATCH}, "is_open"),
    Output({"type": "toggle-msg-icon", "index": MATCH}, "className"),
    Input({"type": "toggle-msg-btn", "index": MATCH}, "n_clicks"),
    State({"type": "collapse-msg", "index": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_card(n_clicks, is_open):
    return not is_open, "bi bi-chevron-down" if not is_open else "bi bi-chevron-right"

@app.callback(
    Output("more-info-icon", "className"),
    Output("profile-collapse", "is_open"),
    Input("profile-more-info-button", "n_clicks"),
    State("profile-collapse", "is_open"),
)
def toggle_history(n, is_open):
    if n:
        return ("fas fa-chevron-up" if not is_open else "fas fa-chevron-down"), not is_open
    return "fas fa-chevron-down", is_open

@app.callback(
    Output({"type": "collapse", "index": MATCH}, "is_open"),
    Output({"type": "collapse-button", "index": MATCH}, "children"),
    Input({"type": "collapse-button", "index": MATCH}, "n_clicks"),
    State({"type": "collapse", "index": MATCH}, "is_open"),
)
def toggle_collapse(n_clicks, is_open):
    text = "Show Messages"
    if n_clicks:
        new_state = not is_open
        button_text = "Hide" if new_state else "Show"
        icon_class = "fas fa-chevron-up" if new_state else "fas fa-chevron-down"
        return new_state, [button_text, html.I(className=icon_class)]
    return is_open, ["Show", html.I(className="fas fa-chevron-down")]

