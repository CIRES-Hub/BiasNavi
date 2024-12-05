from UI.app import app
from db_models.users import User
from db_models.databases import db
from dash.dependencies import Input, Output, State
from flask_login import current_user
from utils.constant import DEFAULT_NEXT_QUESTION_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_PREFIX_PROMPT, \
    DEFAULT_PERSONA_PROMPT
from core.variable import global_vars

@app.callback(
    Output({'type': 'spinner-btn', 'index': 2}, 'children', allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 2}, 'children'),
    [State('next-question-input-1', "value"),
     # State('next-question-input-2', "value"),
     State('system-prompt-input', "value"),
     State('persona-prompt-input', "value"),
     State('prefix-prompt-input', "value")],
    prevent_initial_call=True,
)
def update_prompt(update_prompt_click, new_next_question_1, new_system_prompt, new_persona_prompt,
                  new_prefix_prompt):
    try:
        # Fetch
        user = User.query.get(current_user.id)

        # Update and commit
        user.follow_up_questions_prompt_1 = new_next_question_1
        user.prefix_prompt = new_prefix_prompt
        user.persona_prompt = new_persona_prompt
        user.system_prompt = new_system_prompt
        db.session.commit()
        global_vars.agent.update_agent_prompt()
    except Exception as e:
        db.session.rollback()
        print("Error when update prompt", e)
    return "Save"


# @app.callback(
#     Output('update-prompt-button', 'disabled', allow_duplicate=True),
#     Input('reset-prompt-button', 'n_clicks'),
#     [State('next-question-input-1', "value"),
#      State('system-prompt-input', "value"),
#      State('persona-prompt-input', "value"),
#      State('prefix-prompt-input', "value")],
#     prevent_initial_call=True,
# )
# def reset_prompt(reset_prompt_click, new_next_question_1, new_system_prompt, new_persona_prompt,
#                  new_prefix_prompt):
#     try:
#         # Fetch
#         user = User.query.get(current_user.id)
#
#         # Update and commit
#         user.follow_up_questions_prompt_1 = DEFAULT_NEXT_QUESTION_PROMPT
#         user.prefix_prompt = DEFAULT_PREFIX_PROMPT
#         user.persona_prompt = DEFAULT_PERSONA_PROMPT
#         user.system_prompt = DEFAULT_SYSTEM_PROMPT
#         db.session.commit()
#         global_vars.agent.update_agent_prompt()
#     except Exception as e:
#         db.session.rollback()
#         print("Error when update prompt", e)
#     return False
# @app.callback(
#     Output('next-question-input-1', "value"),
#     Output('system-prompt-input', "value"),
#     Output('persona-prompt-input', "value"),
#     Output('prefix-prompt-input', "value"),
#     Input("reset-prompt-button", "n_clicks"),
#     prevent_initial_call=True
# )
# def reset_default_prompts(n_clicks):
#     return [
#         DEFAULT_NEXT_QUESTION_PROMPT,
#         DEFAULT_SYSTEM_PROMPT,
#         DEFAULT_PERSONA_PROMPT,
#         DEFAULT_PREFIX_PROMPT
#     ]

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('return-home-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout_and_redirect(n_clicks):
    if n_clicks > 0:
        return "/home"
