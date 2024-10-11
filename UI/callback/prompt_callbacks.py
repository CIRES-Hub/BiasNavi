from UI.app import app
from db_models.users import User
from db_models.databases import db
from dash.dependencies import Input, Output, State
from agent import DatasetAgent
from UI.functions import *
from flask_login import current_user
from UI.functions import query_llm
from utils.constant import DEFAULT_NEXT_QUESTION_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_PREFIX_PROMPT, DEFAULT_PERSONA_PROMPT

@app.callback(
    Output('update-prompt-button', 'disabled', allow_duplicate=True),
    Input('update-prompt-button', 'n_clicks'),
    [State('next-question-input-1', "value"),
     State('next-question-input-2', "value"),
     State('system-prompt-input', "value"),
     State('persona-prompt-input', "value"),
     State('prefix-prompt-input', "value")],
    prevent_initial_call=True,
)
def update_prompt(update_prompt_click, new_next_question_1, new_next_question_2, new_system_prompt, new_persona_prompt,
                  new_prefix_prompt):
    try:
        # Fetch
        user = User.query.get(current_user.id)

        # Update and commit
        user.follow_up_questions_prompt_1 = new_next_question_1
        user.follow_up_questions_prompt_2 = new_next_question_2
        user.prefix_prompt = new_prefix_prompt
        user.persona_prompt = new_persona_prompt
        user.system_prompt = new_system_prompt
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Error when update prompt", e)

    if global_vars.df is not None and global_vars.file_name is not None:
        global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name, conversation_session=global_vars.conversation_session)
        if all([current_user.professional_role, current_user.industry_sector, current_user.expertise_level]):
            persona_query = current_user.persona_prompt.replace("{{professional_role}}", current_user.professional_role)
            persona_query = persona_query.replace("{{industry_sector}}", current_user.industry_sector)
            persona_query = persona_query.replace("{{expertise_level}}", current_user.expertise_level)
            persona_query = persona_query.replace("{{technical_level}}", current_user.technical_level)
            persona_query = persona_query.replace("{{bias_awareness}}", current_user.bias_awareness)
            query_llm(persona_query, current_user.id)
    return False


@app.callback(
    Output('update-prompt-button', 'disabled', allow_duplicate=True),
    Input('reset-prompt-button', 'n_clicks'),
    [State('next-question-input-1', "value"),
     State('next-question-input-2', "value"),
     State('system-prompt-input', "value"),
     State('persona-prompt-input', "value"),
     State('prefix-prompt-input', "value")],
    prevent_initial_call=True,
)
def reset_prompt(reset_prompt_click, new_next_question_1, new_next_question_2, new_system_prompt, new_persona_prompt,
                  new_prefix_prompt):
    try:
        # Fetch
        user = User.query.get(current_user.id)

        # Update and commit
        user.follow_up_questions_prompt_1 = DEFAULT_NEXT_QUESTION_PROMPT
        user.follow_up_questions_prompt_2 = DEFAULT_NEXT_QUESTION_PROMPT
        user.prefix_prompt = DEFAULT_PREFIX_PROMPT
        user.persona_prompt = DEFAULT_PERSONA_PROMPT
        user.system_prompt = DEFAULT_SYSTEM_PROMPT
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Error when update prompt", e)

    if global_vars.df is not None and global_vars.file_name is not None:
        global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name, conversation_session=global_vars.conversation_session)
        if all([current_user.professional_role, current_user.industry_sector, current_user.expertise_level]):
            persona_query = current_user.persona_prompt.replace("{{professional_role}}", current_user.professional_role)
            persona_query = persona_query.replace("{{industry_sector}}", current_user.industry_sector)
            persona_query = persona_query.replace("{{expertise_level}}", current_user.expertise_level)
            persona_query = persona_query.replace("{{technical_level}}", current_user.technical_level)
            persona_query = persona_query.replace("{{bias_awareness}}", current_user.bias_awareness)
            query_llm(persona_query, current_user.id)
    return False
