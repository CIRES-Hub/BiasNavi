import dash_bootstrap_components as dbc
from dash import dcc, html

from flask_login import logout_user, current_user


def prompt_card():
    return dbc.Card(id="setting-container",
             children=[
                 html.H4("Prompt for Eliciting Model's ability"),
                 dcc.Textarea(rows=7, id="system-prompt-input", className="mb-4 prompt-input p-2",
                              value=current_user.system_prompt),
                 html.H4("Prompt for Handling Dataset"),
                 dcc.Textarea(rows=7, id="prefix-prompt-input", className="mb-4 prompt-input p-2",
                              value=current_user.prefix_prompt),
                 html.H4("Prompt for Enhancing Personalization"),
                 dcc.Textarea(rows=8, id="persona-prompt-input", className="mb-4 prompt-input p-2",
                              value=current_user.persona_prompt),
                 html.H4("Prompt for Generating Follow-up Questions"),
                 dcc.Textarea(rows=2, id="next-question-input-1", className="mb-4 prompt-input p-2",
                              value=current_user.follow_up_questions_prompt_1),
                 # html.H4("Prompt for Generating Follow-up Questions 2"),
                 # dcc.Textarea(rows=2, id="next-question-input-2", className="mb-4 prompt-input p-2",
                 #              value=current_user.follow_up_questions_prompt_2),
                 html.Div(children=[
                     dbc.Button("Reset Default", id="reset-prompt-button", className="prompt-button",
                                n_clicks=0),
                     dbc.Button("Save", id={'type': 'spinner-btn', 'index': 2}, className="prompt-button",
                                n_clicks=0),
                     dbc.Button("Home", id="return-home-button", className="prompt-button", n_clicks=0),
                 ], className="save-button"),
             ],
             className="prompt-card p-4", style={"display": "none"})