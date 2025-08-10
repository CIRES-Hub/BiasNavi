import dash

from UI.app import app
from dash.dependencies import Input, Output, State
from UI.app_state import app_vars


@app.callback(
    Output("pipeline-alert", "is_open", allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 4},"style"),
    Output({'type': 'spinner-btn', 'index': 5},"style"),
    Output({'type': 'spinner-btn', 'index': 6},"style"),
    Output("right-arrow-icon-1","style"),
    Output("right-arrow-icon-2", "style"),
    Output("right-arrow-icon-3", "style"),
    Input("bias-stage-value", "data"),
    State({'type': 'spinner-btn', 'index': 4},"style"),
    State({'type': 'spinner-btn', 'index': 5},"style"),
    State({'type': 'spinner-btn', 'index': 6},"style"),
    State("right-arrow-icon-1","style"),
    State("right-arrow-icon-2", "style"),
    State("right-arrow-icon-3", "style"),
    prevent_initial_call=True
)
def change_pipeline_stage(val, m_style, s_style, a_style, ra1_style, ra2_style, ra3_style):
    stages = ["Identify","Measure","Surface","Adapt"]
    if app_vars.agent:
        if val>=(len(stages)):
            val = 3
        new_stage = stages[val]
        app_vars.agent.current_stage = new_stage
        app_vars.current_stage = new_stage
        app_vars.agent.add_user_action_to_history(f"I have modify the current stage of the bias management "
                                                     f"pipeline to {new_stage}. It's the time to go to this stage.")
        if val == 0:
            m_style["display"] = "none"
            s_style["display"] = "none"
            a_style["display"] = "none"
            ra1_style["display"] = "none"
            ra2_style["display"] = "none"
            ra3_style["display"] = "none"

        elif val == 1:
            m_style["display"] = "block"
            s_style["display"] = "none"
            a_style["display"] = "none"
            ra1_style["display"] = "block"
            ra2_style["display"] = "none"
            ra3_style["display"] = "none"

        elif val == 2:
            m_style["display"] = "block"
            s_style["display"] = "block"
            a_style["display"] = "none"
            ra1_style["display"] = "block"
            ra2_style["display"] = "block"
            ra3_style["display"] = "none"

        elif val == 3:
            m_style["display"] = "block"
            s_style["display"] = "block"
            a_style["display"] = "block"
            ra1_style["display"] = "block"
            ra2_style["display"] = "block"
            ra3_style["display"] = "block"

        return True, m_style, s_style, a_style, ra1_style, ra2_style, ra3_style
    else:
        return False, dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update



bias_management_questions = {
    "Identify": [
        "Is there any potential bias in my data?",
        "How do I know if my data has fairness issues?",
        "What steps can I take to check for bias?",
        "Are there any signals or patterns that indicate bias?",
        "Can you help me identify if bias exists?"
    ],
    "Measure": [
        "How do I measure bias once it’s identified?",
        "What metrics or tools can I use to quantify bias?",
        "Can you calculate the extent of the bias in this dataset?",
        "What does the bias measurement tell me?",
        "How can I understand the impact of bias based on metrics?"
    ],
    "Surface": [
        "How can I present the identified bias to others?",
        "What is the best way to summarize bias findings?",
        "Can you help me highlight the most important fairness issues?",
        "How should I explain these results to non-technical stakeholders?",
        "What tools or visuals can I use to report on bias?"
    ],
    "Adapt": [
        "How can I address the bias in my data or system?",
        "What are the options for mitigating bias?",
        "What changes should I make to reduce bias effectively?",
        "Can you suggest ways to improve fairness without affecting accuracy too much?",
        "How can I test if the bias mitigation strategies are working?"
    ]
}
@app.callback(
    Output("question-modal", "is_open"),
    Output("question-modal-list", "options"),
    [Input("common-question-btn", "n_clicks"),
     Input("question-modal-close-btn", "n_clicks")],
    [State("question-modal", "is_open")],
    prevent_initial_call=True,
)
def display_common_questions(open_clicks, close_clicks, is_open):
    questions = bias_management_questions.get(app_vars.current_stage, [])
    options = [{"label": question, "value": question} for question in questions]
    if open_clicks or close_clicks:
        return not is_open, options
    return is_open, options


@app.callback(
    Output("query-input", "value", allow_duplicate=True),
    Output("question-modal", "is_open", allow_duplicate=True),
    [Input("question-modal-choose-btn", "n_clicks"),
     State("question-modal-list", "value")],
    prevent_initial_call=True,
)
def choose_question(n_clicks, question):
    return question, False

@app.callback(
    Output("upload-modal", "is_open", allow_duplicate=True),
    Input("close-upload-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_upload_modal(n_clicks):
    return False
