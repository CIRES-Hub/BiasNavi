import dash
from UI.app import app
from db_models.users import User
from db_models.databases import db
from dash.dependencies import Input, Output, State
from flask_login import current_user


# Update Username
@app.callback(
    Output("edit-username-modal", "is_open"),
    Output("new-username-input", "value"),
    Input("edit-username-icon", "n_clicks"),
    Input("cancel-username-edit", "n_clicks"),
    Input("save-username-button", "n_clicks"),
    State("edit-username-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_username_modal(edit_clicks, cancel_clicks, save_clicks, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "edit-username-icon":
            return True, current_user.username or ""
        elif button_id in ["cancel-username-edit", "save-username-button"]:
            return False, ""
    return is_open, ""


@app.callback(
    Output("username-edit-success", "data"),
    Input("save-username-button", "n_clicks"),
    State("new-username-input", "value"),
    prevent_initial_call=True
)
def save_new_username(n_clicks, new_username):
    if n_clicks > 0 and new_username:
        user = User.query.get(current_user.id)
        user.username = new_username
        db.session.commit()
        return True
    return False
