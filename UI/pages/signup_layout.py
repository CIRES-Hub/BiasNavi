import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash.exceptions import PreventUpdate
from db_models.users import User
from db_models.databases import db
import docker
import os
import shutil
from constant_prompt import DEFAULT_NEXT_QUESTION_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_PREFIX_PROMPT, \
    DEFAULT_PERSONA_PROMPT

dash.register_page(__name__, path='/signup/', title='Signup')

custom_style = {
    "input-wrapper": {
        "width": "100%",
        "padding": "0 10px",
    },
    "input-field": {
        "width": "100%",
    }
}

layout = dbc.Container(fluid=True, children=[
    dbc.Row(
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Sign Up", className="card-title mb-4 text-center"),
                    dbc.Row([
                        dbc.Label("Email",
                                  className="font-weight-bold"),
                        html.Div(
                            dbc.Input(
                                id="email-input", placeholder="Enter your email",
                                style=custom_style["input-field"]), style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Label("Password",
                                  className="font-weight-bold"),
                        html.Div(
                            dbc.Input(
                                id="password-input", placeholder="Enter your password", type="password",
                                style=custom_style["input-field"]), style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Label("Confirm Password",
                                  className="font-weight-bold"),
                        html.Div(
                            dbc.Input(
                                id="confirm-password-input", placeholder="Enter your password", type="password",
                                style=custom_style["input-field"]), style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Label("Username",
                                  className="font-weight-bold"),
                        html.Div(
                            dbc.Input(
                                id="signup-username-input", placeholder="Enter your username",
                                style=custom_style["input-field"]), style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Professional Role",
                                  className="font-weight-bold"),
                        html.Div(
                            dcc.Dropdown(
                                id="professional-role-input",
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
                            ),
                            style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-3"),

                    dbc.Row([
                        html.Div([
                            dbc.Label(
                                "Level of Technical in Data Science and Machine Learning",
                                className="font-weight-bold"),
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
                            ),
                            style=custom_style["input-wrapper"]
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Button(
                                "Cancel", id="cancel-button", color="secondary", n_clicks=0, class_name="w-100"),
                            width=6, className="ms-auto"
                        ),
                        dbc.Col(
                            dbc.Button("Sign Up", id="submit-signup-button",
                                       color="primary", n_clicks=0, class_name="w-100"),
                            width=6
                        )
                    ], className="d-flex justify-content-between"),
                    html.Div(id="auth-signup-result", className="mt-3", style={'color': 'red'}),
                    dcc.Location(id='url', refresh=True)
                ]),
                style={"width": "400px"}
            )
        ], className="flex-center", style={"padding": "50px 0"})
        , style={'height': '100%', 'width': '100%'})
], className="body vh-100 d-flex align-items-center justify-content-center fade-in",
                       style={'overflowY': 'auto', "background": "linear-gradient(to right, #67b26f, #4ca2cd)"})


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("auth-signup-result", "children", allow_duplicate=True),
    Input("submit-signup-button", "n_clicks"),
    Input("cancel-button", "n_clicks"),
    State("email-input", "value"),
    State("password-input", "value"),
    State("confirm-password-input", "value"),
    State("signup-username-input", "value"),
    State("professional-role-input", "value"),
    State("industry-sector-dropdown", "value"),
    State("expertise-level-dropdown", "value"),
    State("technical-level-dropdown", "value"),
    State("bias-awareness-dropdown", "value"),
    State("areas-of-interest-checklist", "value"),
    prevent_initial_call=True
)
def handle_auth(signup_clicks, login_clicks, email, password, confirm_password, user_name, professional_role,
                industry_sector, expertise_level, technical_level, bias_awareness, areas_of_interest):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "submit-signup-button":
        if not all([email, password, user_name, professional_role, industry_sector, expertise_level, areas_of_interest,
                    technical_level, bias_awareness]):
            return dash.no_update, "Please fill in all fields."
        if password != confirm_password:
            return dash.no_update, "The password confirmation does not match."
        # Check if user already exists
        user = User.query.filter((User.email == email)).first()
        if user:
            return dash.no_update, "Email already exists. Please try a different email."

        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        new_user.signup()
        user_id = str(new_user.id)

        try:
            user = User.query.get(user_id)

            user.follow_up_questions_prompt_1 = DEFAULT_NEXT_QUESTION_PROMPT
            user.follow_up_questions_prompt_2 = DEFAULT_NEXT_QUESTION_PROMPT

            user.system_prompt = DEFAULT_SYSTEM_PROMPT

            user.prefix_prompt = DEFAULT_PREFIX_PROMPT

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
        except Exception as e:
            print("Create user failed: ", e)
            db.session.rollback()

        try:

            client = docker.from_env()
            current_path = os.path.dirname(os.path.realpath(__file__))
            user_data_dir = os.path.dirname(current_path) + '/../tmp/' + user_id
            os.makedirs(user_data_dir, exist_ok=True)
            shutil.copyfile(os.path.dirname(current_path) + '/assets/sandbox_main.py', user_data_dir + '/main.py')
            client.containers.run('daisyy512/hello-docker',
                                  name='biasnavi-' + user_id,
                                  volumes=[user_data_dir + ':/home/sandbox/' + user_id],
                                  detach=True,
                                  tty=True)
            print("Create container successfully")
        except Exception as e:
            print("Create container failed: ", e)
        return '/home', "Signup successful!"

    elif button_id == "cancel-button":
        return '/', ""

    raise PreventUpdate