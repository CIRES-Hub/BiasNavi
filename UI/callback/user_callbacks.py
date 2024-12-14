import dash
from UI.app import app
from db_models.users import User
from db_models.databases import db
from flask_login import current_user
from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from utils.constant import DEFAULT_PERSONA_PROMPT
from UI.variable import global_vars

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


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("survey-result", "children"),
    Output("survey-modal", "is_open", allow_duplicate=True),
    Output("survey-edit-success", "data"),
    Input("submit-button", "n_clicks"),
    Input("skip-button", "n_clicks"),
    State("username-input", "value"),
    State("professional-role-input", "value"),
    State("industry-sector-dropdown", "value"),
    State("expertise-level-dropdown", "value"),
    State("technical-level-dropdown", "value"),
    State("bias-awareness-dropdown", "value"),
    State("areas-of-interest-checklist", "value"),
    prevent_initial_call=True
)
def update_survey_info(submit_clicks, skip_clicks, user_name, professional_role, industry_sector, expertise_level, technical_level, bias_awareness, areas_of_interest):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if submit_clicks is not None and button_id == "submit-button":
        if not all([professional_role, industry_sector, expertise_level, areas_of_interest, technical_level, bias_awareness]):
            return dash.no_update, "Please fill in all.", dash.no_update, False

        try:
            # Fetch
            user = User.query.get(current_user.id)

            # Update and commit
            user.username = user_name
            user.professional_role = professional_role
            user.industry_sector = industry_sector
            user.expertise_level = expertise_level
            user.technical_level = technical_level
            user.bias_awareness = bias_awareness
            user.areas_of_interest = areas_of_interest
            user.persona_prompt = DEFAULT_PERSONA_PROMPT.format(professional_role=user.professional_role,
                                                                industry_sector=user.industry_sector,
                                                                expertise_level=user.expertise_level,
                                                                technical_level=user.technical_level,
                                                                bias_level=user.bias_awareness
                                                                ),

            db.session.commit()
            global_vars.agent.update_agent_prompt()
            return '/home', 'Survey information updated!', False, True
        except Exception as e:
            db.session.rollback()
            return dash.no_update, f"An error occurred: {str(e)}", dash.no_update, dash.no_update

    elif button_id == "skip-button":
        return '/home', 'Survey skipped.', False, False

    raise PreventUpdate
