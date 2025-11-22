import dash
from UI.app import app
from dash.dependencies import Input, Output, State
from UI.functions import *
from dash.exceptions import PreventUpdate
from dash import callback_context
from UI.pages.components.survey_modal import survey_modal
from flask_login import logout_user, current_user
from agent.baseline_agent import BaselineAgent
from agent import DatasetAgent
@app.callback(
     Output('right-column', 'style', allow_duplicate=True),
     Output('menu-nex-view', 'children', allow_duplicate=True),
     Output('menu-ex-view', 'children', allow_duplicate=True),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     Output('data-view-buttons', 'style', allow_duplicate=True),
     Output("chat_history", 'style', allow_duplicate=True),
     Input('menu-nex-view', 'n_clicks'),
     State('menu-nex-view', 'children'),
     State('right-column', 'style'),
    prevent_initial_call=True
)
def display_non_expert_view(n_clicks, label, style):
    if label == 'Non-Expert Mode':
        style['display'] = 'none'
        return style, "Non-Expert Mode ✔", "Expert Mode", 5, 7, 0, {'display': 'none'}, {'display': 'none'}
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
     Output('right-column', 'style', allow_duplicate=True),
     Output('menu-nex-view', 'disabled', allow_duplicate=True),
     Output('menu-ex-view', 'disabled', allow_duplicate=True),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     Output('data-view-buttons', 'style', allow_duplicate=True),
     Output("chat_history", 'style', allow_duplicate=True),
     Output("next-suggested-questions", 'style', allow_duplicate=True),
     Output('menu-baseline-view', 'children', allow_duplicate=True),
     Output("baseline-mode-adapt-btn","style", allow_duplicate=True),
     Output("bias-management-buttons", "style", allow_duplicate=True),
     Output("to-do-div", "style", allow_duplicate=True),
     Output("menu-prompt", "style", allow_duplicate=True),
     Output("menu-profile", "style", allow_duplicate=True),
     Input('menu-baseline-view', 'n_clicks'),
     State('menu-baseline-view', 'children'),
     State('right-column', 'style'),
    prevent_initial_call=True
)
def baseline_mode(n_clicks, label, right_column_style):
    if label == 'Baseline Mode':
        right_column_style['display'] = 'none'
        app_vars.baseline_mode = True
        app_vars.agent = BaselineAgent(app_vars.df)
        return right_column_style, True, True, 5, 7, 0, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, "Exit Baseline Mode", {'display': 'block'},{'display': 'none'}, {'display': 'none'},{'display': 'none'}, {'display': 'none'}
    else:
        app_vars.agent = DatasetAgent(app_vars.df)
        app_vars.baseline_mode = False
        return (dash.no_update, False, False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, {'display': 'block'},
                "Baseline Mode", {'display': 'none'}, {'display': 'block'}, {'display': 'block'},{'display': 'block'}, {'display': 'block'})


@app.callback(
     Output('right-column', 'style', allow_duplicate=True),
     Output('menu-ex-view', 'children', allow_duplicate=True),
     Output('menu-nex-view', 'children', allow_duplicate=True),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     Output('data-view-buttons', 'style', allow_duplicate=True),
     Output("chat_history", 'style', allow_duplicate=True),
     Input('menu-ex-view', 'n_clicks'),
     State('menu-ex-view', 'children'),
     State('right-column', 'style'),
    prevent_initial_call=True
)
def display_expert_view(n_clicks, label, style):
    if label == 'Expert Mode':
        style['display'] = 'block'
        return style, "Expert Mode ✔", "Non-Expert Mode", 4, 5, 3, {'display': 'block'},  {'display': 'block'}
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,  dash.no_update, dash.no_update


# @app.callback(
#     [Output('right-column', 'style'),
#      Output('menu-hide-chartview', 'children'),
#      Output('left-column', 'width', allow_duplicate=True),
#      Output('middle-column', 'width', allow_duplicate=True),
#      Output('right-column', 'width', allow_duplicate=True),
#      ],
#     [Input('menu-hide-chartview', 'n_clicks')],
#     [State('menu-hide-chartview', 'children')],
#     prevent_initial_call=True
# )
# def hide_chartview(n_clicks, label):
#     if label == 'Show Right View':
#         return {'display': 'block'}, "Hide Right View", 3, 6, 3
#     else:
#         return {'display': 'none'}, "Show Right View", 3, 9, 0


@app.callback(
    [Output('menu-model-gpt4omini', 'children', allow_duplicate=True),
     Output('menu-model-gpt4o', 'children', allow_duplicate=True)],
    [Input('menu-model-gpt4omini', 'n_clicks'),
     Input('menu-model-gpt4o', 'n_clicks')],
    prevent_initial_call=True
)
def change_llm_model(n_clicks_gpt3dot5, n_clicks_gpt4o):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if clicked_id == 'menu-model-gpt4omini':
        app_vars.agent.set_llm_model('GPT-4o-mini')
        return "GPT-4o-mini ✔", "GPT-4o"
    elif clicked_id == 'menu-model-gpt4':
        app_vars.agent.set_llm_model('gpt-4-turbo')
        return "GPT-4o-mini", "GPT-4o"
    raise dash.exceptions.PreventUpdate

# @app.callback(
#     Output("export-history-modal", "is_open"),
#     [Input("menu-export-chat", "n_clicks"), Input("close", "n_clicks")],
#     [State("export-history-modal", "is_open")],
# )
# def toggle_modal(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open

@app.callback(
    Output("hero-dismissed", "data"),
    Input("hero-close", "n_clicks"),
    Input("hero-auto-dismiss", "n_intervals"),
    State("hero-dismissed", "data"),
    prevent_initial_call=True
)
def dismiss_hero_section(close_clicks, auto_dismiss, dismissed):
    ctx = callback_context
    if dismissed:
        raise PreventUpdate
    if ctx.triggered:
        return True
    raise PreventUpdate

# Callback to toggle hero-section display
@app.callback(
    Output("hero-section", "style"),
    Input("hero-dismissed", "data"),
)
def toggle_hero_section_style(dismissed):
    if dismissed:
        return {"display": "none"}
    return {"position": "relative"}



@app.callback(
    Output("survey-modal", "is_open"),
    Input("menu-profile", "n_clicks"),
    prevent_initial_call=True
)
def open_survey_modal(n_clicks):
    if n_clicks:
        return True

@app.callback(
    Output("survey-modal-body", "children"),
    Input("survey-edit-success", "data"),
    Input("username-edit-success", "data")
)
def update_survey_content(survey_update, username_update):
    return survey_modal()

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    #Input('menu-help', 'n_clicks'),
    Input('menu-prompt', 'n_clicks'),
    prevent_initial_call=True
)
def logout_and_redirect(logout_clicks, setting_clicks):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (logout_clicks is not None and logout_clicks > 0) or (
            setting_clicks is not None and setting_clicks > 0):
        if button_id == "logout-button":
            logout_user()
            return "/"
        # if button_id == "menu-help":
        #     return "/helps/"
        elif button_id == "menu-prompt":
            return "/settings/prompts"
        return dash.no_update
    return dash.no_update