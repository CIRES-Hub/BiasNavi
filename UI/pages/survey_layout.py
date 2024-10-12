from db_models.users import User, db
from flask_login import current_user
from dash import callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash.exceptions import PreventUpdate
from werkzeug.security import generate_password_hash
from db_models.users import User
from db_models.databases import db
from flask_login import current_user
from utils.constant import DEFAULT_PERSONA_PROMPT

dash.register_page(__name__, path='/survey/', title='Survey')

custom_style = {
    "input-wrapper": {
        "width": "100%",
        "padding": "0 10px",
    },
    "input-field": {
        "width": "100%",
    }
}

def layout():
    user = User.query.get(current_user.id)
    return dbc.Container(
    fluid=True,
    className="body vh-100 d-flex align-items-center justify-content-center bg-light",
    style={"background": "linear-gradient(to right, #67b26f, #4ca2cd)"},
    children=[
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H3("Background Survey",
                                className="card-title text-center mb-4"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Username",
                                          className="font-weight-bold"),
                                html.Div(
                                    dbc.Input(
                                        id="username-input", placeholder="Enter your username", 
                                        style=custom_style["input-field"], value=user.username), style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Label("Professional Role",
                                          className="font-weight-bold"),
                                html.Div(
                                    dcc.Dropdown(
                                        id="professional-role-input",
                                        value=user.professional_role,
                                        options=[
                                            {"label": sector, "value": sector} for sector in
                                            ["Data Scientist", "Researcher", "Other"]
                                        ],
                                        placeholder="Select your professional role",
                                        style=custom_style["input-field"],
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Label("Industry Sector",
                                          className="font-weight-bold"),
                                html.Div(
                                    dcc.Dropdown(
                                        id="industry-sector-dropdown",
                                        options=[
                                            {"label": sector, "value": sector} for sector in
                                            ["Technology", "Healthcare", "Finance",
                                                "Education", "Media", "Other"]
                                        ],
                                        placeholder="Select your industry sector",
                                        style=custom_style["input-field"],
                                        value=user.industry_sector,
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Label(
                                    "Level of Expertise in Data Analysis", className="font-weight-bold"),
                                html.Div(
                                    dcc.Dropdown(
                                        id="expertise-level-dropdown",
                                        options=[
                                            {"label": level, "value": level} for level in
                                            ["Beginner", "Intermediate",
                                                "Advanced", "Expert"]
                                        ],
                                        placeholder="Select your expertise level",
                                        style=custom_style["input-field"],
                                        value=user.expertise_level,
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),
                            
                            dbc.Row([
                                html.Div([
                                    dbc.Label(
                                        "Level of Technical in Data Science and Machine Learning", className="font-weight-bold"),
                                    html.Span(
                                        html.I(className="fas fa-question-circle"),
                                        id="technical-tooltip-snapshot",
                                        style={
                                            "fontSize": "20px",
                                            "color": "#aaa",
                                            "cursor": "pointer",
                                            "marginLeft": "5px",
                                            "alignSelf": "center"
                                        }
                                    )], className="survey-tooltip"),
                                    dbc.Tooltip(
                                    "How would you rate your expertise in data science and machine learning?",
                                    target="technical-tooltip-snapshot",
                                    placement="right"
                                ),
                                html.Div(
                                    dcc.Dropdown(
                                        id="technical-level-dropdown",
                                        options=[
                                            {"label": level, "value": level} for level in
                                            ["Novice", "Beginner",
                                                "Intermediate", "Advanced", "Expert"]
                                        ],
                                        placeholder="Select your expertise level",
                                        style=custom_style["input-field"],
                                        value=user.technical_level,
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),
                            
                            dbc.Row([
                                html.Div([
                                    dbc.Label(
                                        "Level of Awareness of Biases in Datasets and AI Models", className="font-weight-bold"),
                                    html.Span(
                                        html.I(className="fas fa-question-circle"),
                                        id="bias-tooltip-snapshot",
                                        style={
                                            "fontSize": "20px",
                                            "color": "#aaa",
                                            "cursor": "pointer",
                                            "marginLeft": "5px",
                                            "alignSelf": "center"
                                        }
                                    )], className="survey-tooltip"),
                                    dbc.Tooltip(
                                    "How would you rate your awareness of biases in datasets and AI models?",
                                    target="bias-tooltip-snapshot",
                                    placement="right"
                                ),
                                html.Div(
                                    dcc.Dropdown(
                                        id="bias-awareness-dropdown",
                                        options=[
                                            {"label": level, "value": level} for level in
                                            ["Very Low", "Low",
                                                "Moderate", "High", "Very High"]
                                        ],
                                        placeholder="Select your awareness level",
                                        style=custom_style["input-field"],
                                        value=user.bias_awareness,
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Label("Primary Areas of Interest",
                                          className="font-weight-bold"),
                                html.Div(
                                    dbc.Checklist(
                                        id="areas-of-interest-checklist",
                                        options=[
                                            {"label": area, "value": area} for area in
                                            ["Bias Detection", "Data Visualization",
                                                "Statistical Analysis", "Machine Learning", "Other"]
                                        ],
                                        inline=True,
                                        style=custom_style["input-field"],
                                        value=user.areas_of_interest or [],
                                    ),
                                    style=custom_style["input-wrapper"]
                                ),
                            ], className="mb-4"),

                            dbc.Row([
                                dbc.Col(
                                    dbc.Button(
                                        "Submit", id="submit-button", color="primary", className="w-100"),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Skip", id="skip-button", color="secondary", className="w-100"),
                                    width=6,
                                ),
                            ], className="mt-3"),
                        ]),

                        html.Div(id="survey-result",
                                 className="mt-3 text-center"),
                        dcc.Location(id='url', refresh=True)
                    ]),
                    className="shadow",
                    style={"maxWidth": "500px", "width": "100%"}
                )
            )
        )
    ]
)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("survey-result", "children"),
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

    if button_id == "submit-button":
        if not all([professional_role, industry_sector, expertise_level, areas_of_interest, technical_level, bias_awareness]):
            return dash.no_update, "Please fill in all."

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
            return '/home', 'Survey information updated!'
        except Exception as e:
            db.session.rollback()
            return dash.no_update, f"An error occurred: {str(e)}"

    elif button_id == "skip-button":
        return '/home', 'Survey skipped.'

    raise PreventUpdate
