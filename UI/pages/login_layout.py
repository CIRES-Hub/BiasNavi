from flask_login import login_user
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash.exceptions import PreventUpdate
from db_models.users import User
from db_models.databases import db
from UI.app import server
import time

dash.register_page(__name__, path='/', title='Login')

layout = dbc.Container(fluid=True, children=[
    dbc.Row(
        dbc.Col([
            html.H1("BiasNavi", id="fade-div", className='fade-in', style={'display': 'block',
                    'color': 'white', "fontSize": "3vw", "marginBottom": "-5px",}),
            html.H5("Navigate you through bias in your data with AI", id="fade-div", className='fade-in',
                    style={'display': 'block', 'color': 'coral', "fontSize": "0.85vw", "marginBottom": "30px",}),
            dbc.Card(
                [

                    dbc.CardBody([
                        html.H4([
                            html.I(className="bi bi-person-circle", style={"marginRight": "10px", "color": "#614385", "fontSize": "1.8rem"}),
                            "Login"
                        ], className="card-title mb-4 text-center", style={"fontWeight": "bold", "letterSpacing": "1px", "color": "#232946"}),
                        dbc.Input(id="email-input", placeholder="Email", type="text", className="mb-3 rounded-pill px-3", style={
                            "backgroundColor": "rgb(255,255,255)",
                            "border": "1.5px solid #cfd8dc",
                            "fontSize": "1.07rem",
                            "boxShadow": "none"
                        }),
                        dbc.Input(id="password-input", placeholder="Password", type="password", className="mb-4 rounded-pill px-3", style={
                            "backgroundColor": "rgb(255,255,255)",
                            "border": "1.5px solid #cfd8dc",
                            "fontSize": "1.07rem",
                            "boxShadow": "none"
                        }),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "Log in",
                                        id="login-button",
                                        color="primary",
                                        n_clicks=0,
                                        class_name="primary-button w-100"
                                    ),
                                    width=6
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Sign up",
                                        id="signup-button",
                                        color="secondary",
                                        n_clicks=0,
                                        class_name="primary-button w-100"
                                    ),
                                    width=6
                                )
                            ],
                            className="justify-content-center"
                        ),
                        html.Div(id="auth-result", className="mt-3", style={'color': 'red'}),
                        dcc.Location(id='url', refresh=True)
                    ])
                ],
                style={
                    "width": "430px",
                    "boxShadow": "0 8px 32px 0 rgba(31,38,135,0.18)",
                    "background": "rgb(255,255,255)",
                    "border": "1.5px solid rgb(255,255,255)",
                    "backdropFilter": "blur(16px)",
                    "WebkitBackdropFilter": "blur(16px)",
                    "marginTop": "18px",
                    "overflow": "hidden",
                    "position": "relative"
                },
                className="fade-in"
            )
        ])
    )
], className="body vh-100 d-flex align-items-center justify-content-center fade-in login-bg", style={"overflowY": "auto"})

# Add the login background div at the top level


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("auth-result", "children", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    Input("signup-button", "n_clicks"),
    State("email-input", "value"),
    State("password-input", "value"),
    # Input('user-mode', 'value'),
    prevent_initial_call=True
)
def handle_auth(login_clicks, signup_clicks, email, password):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "login-button":
        if not email or not password:
            return dash.no_update, "Please fill in all fields."

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return '/home', "Login successful!"
        else:
            return dash.no_update, "Invalid username or password."
    elif button_id == "signup-button":
        return '/signup', ""

    raise PreventUpdate
