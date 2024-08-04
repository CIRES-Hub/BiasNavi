import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash.exceptions import PreventUpdate
from werkzeug.security import generate_password_hash
from db_models.users import User
from db_models.databases import db
from flask_login import login_user

dash.register_page(__name__, path='/signup/', title='Signup')

layout = dbc.Container(fluid=True, children=[
    dbc.Row(
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Sign Up", className="card-title mb-4 text-center"),
                    dbc.Input(id="email-input", placeholder="Email Address",
                              type="email", className="mb-2"),
                    dbc.Input(id="password-input", placeholder="Password",
                              type="password", className="mb-3"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Button("Sign Up", id="signup-button",
                                       color="primary", n_clicks=0, class_name="w-100"),
                            width=6
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Log in", id="login-button", color="secondary", n_clicks=0, class_name="w-100"),
                            width=6, className="ms-auto"
                        )
                    ], className="d-flex justify-content-between"),
                    html.Div(id="auth-result", className="mt-3"),
                    dcc.Location(id='url', refresh=True)
                ]),
                style={"width": "400px"}
            )
        ])
    )
], className="body vh-100 d-flex align-items-center justify-content-center")


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("auth-result", "children", allow_duplicate=True),
    Input("signup-button", "n_clicks"),
    Input("login-button", "n_clicks"),
    State("email-input", "value"),
    State("password-input", "value"),
    prevent_initial_call=True
)
def handle_auth(signup_clicks, login_clicks, email, password):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "signup-button":
        if not email or not password:
            return dash.no_update, "Please fill in all fields."

        # Check if user already exists
        user = User.query.filter((User.email == email)).first()
        if user:
            return dash.no_update, "Email already exists. Please try a different email."

        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        new_user.signup()
        return '/survey', "Signup successful!"

    elif button_id == "login-button":
        return '/', ""

    raise PreventUpdate
