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

dash.register_page(__name__, path='/settings/', path_template='/settings/<subsection>', title='Settings')

def layout(subsection=None):
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                            refresh=True, pathname="/login"),
        ])
        
    return html.Div([
        dbc.Container(fluid=True, children=[
            # =======================================================
            # banner and menu bar layout
            # dbc.Row(justify="center", align="center", className="banner-row settings-banner", children=[
            #     html.Div(children=[
            #         html.Img(src='../assets/logo.svg', className="logo"),
            #         html.P('BiasNavi', className="title"),
            #         dbc.Nav(
            #             className='navbar d-flex flex-wrap',
            #             children=[
            #                 dbc.DropdownMenu(
            #                     [dbc.DropdownMenuItem(
            #                         "Import Dataset", id="menu-import-data")],
            #                     label="Import",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 ),
            #                 dbc.DropdownMenu(
            #                     [dbc.DropdownMenuItem("Export Chat History"), dbc.DropdownMenuItem(
            #                         "Export Dataset Analysis Report")],
            #                     label="Export",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 ),
            #                 dbc.DropdownMenu(
            #                     [dbc.DropdownMenuItem("Predefined Prompt 1"),
            #                      dbc.DropdownMenuItem("Predefined Prompt 2"),
            #                      dbc.DropdownMenuItem("Custom Prompt")],
            #                     label="Prompts",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 ),
            #                 dbc.DropdownMenu(
            #                     [dbc.DropdownMenuItem("GPT-4o-mini  ✔", id="menu-model-gpt4omini"),
            #                      dbc.DropdownMenuItem("GPT-4", id="menu-model-gpt4"),
            #                      dbc.DropdownMenuItem("GPT-4o", id="menu-model-gpt4o")],
            #                     label="LLM Models",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 ),
            #                 dbc.DropdownMenu(
            #                     [dbc.DropdownMenuItem("Hide ChatBox", id="menu-hide-chatbox"),
            #                      dbc.DropdownMenuItem(
            #                          "Hide Data View", id="menu-hide-dataview"),
            #                      dbc.DropdownMenuItem("Hide Right View", id="menu-hide-chartview")],
            #                     label="View",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 ),
            #                 dbc.NavLink("Help", href="", className='nav-item'),
            #                 dbc.DropdownMenu(
            #                     [
            #                         dbc.DropdownMenuItem(
            #                             "About CIRES", href="https://cires.org.au/"),
            #                         dbc.DropdownMenuItem(
            #                             "Settings", id="setting-button", href="/settings/prompts", external_link=True),
            #                         dbc.DropdownMenuItem(
            #                             "Logout", id="logout-button", href="#")
            #                     ],
            #                     label="More",
            #                     nav=True,
            #                     toggleClassName="dropdown-toggle",
            #                     className='menu-item'
            #                 )
            #             ],
            #         ),
            #     ], className='banner'),
            # ]),

            # =======================================================
            # content layout
            dbc.Row([
                # dbc.Col(width=2, id="left-column", children=[dbc.Nav([
                #     dbc.NavLink([html.I(className="bi bi-house-door"), "Home"], href="/home", active="exact", className="settings-sidebar"),
                #     dbc.NavLink([html.I(className="bi bi-terminal"), "Prompts"], href="/settings/prompts", active="exact", class_name="settings-sidebar", external_link=True)
                # ], vertical=True, pills=True)]),

                # =======================================================
                # main content
                dbc.Col(width=10, id="middle-column", children=html.Div(id="main-content"))
            ], className="settings-content")
        ], className="body settings-body")
    ])
    
@callback(
    Output("main-content", "children"),
    [Input('url', 'pathname')],
)
def display_main_content(pathname):
    print(pathname)
    if (pathname == "/settings/prompts"):
        return [dbc.Card(children=[ html.H4("Prompt for Eliciting Model's ability"),
                                    dcc.Textarea(rows=7, id="system-prompt-input", className="mb-4 prompt-input p-2", value=current_user.system_prompt),
                                    html.H4("Prompt for Handling Dataset"),
                                    dcc.Textarea(rows=7, id="prefix-prompt-input", className="mb-4 prompt-input p-2", value=current_user.prefix_prompt),
                                    html.Div([html.H4("Prompt for Enhancing Personalization"), html.Span(
                                        html.I(className="fas fa-question-circle"),
                                        id="tooltip-snapshot",
                                        style={
                                            "fontSize": "20px",
                                            "color": "#aaa",
                                            "cursor": "pointer",
                                            "marginLeft": "5px",
                                            "alignSelf": "center"
                                        }
                                    )], style={"display": "flex", "justifyContent": "space-between"}),
                                    dcc.Textarea(rows=8, id="persona-prompt-input", className="mb-4 prompt-input p-2",
                                                 value=current_user.persona_prompt),
                                    html.H4("Prompt for Generating Follow-up Questions 1"),
                                    dcc.Textarea(rows=2, id="next-question-input-1", className="mb-4 prompt-input p-2",
                                                 value=current_user.follow_up_questions_prompt_1),
                                    html.H4("Prompt for Generating Follow-up Questions 2"),
                                    dcc.Textarea(rows=2, id="next-question-input-2", className="mb-4 prompt-input p-2",
                                                 value=current_user.follow_up_questions_prompt_2),
                                    dcc.Loading(id="update-prompt-loading", children=html.Div(children=[dbc.Button("Reset Default", id="reset-prompt-button", className="prompt-button", n_clicks=0),
                                                                                                        dbc.Button("Save", id="update-prompt-button", className="prompt-button", n_clicks=0),
                                                                                                        ], className="save-button")),
                                    dbc.Tooltip(
                                    "{{}} matches the field of the user information",
                                    target="tooltip-snapshot",
                                    )],
                                    className="prompt-card p-4")]
        
    if pathname == '/' or pathname == '/signup':
        if current_user.is_authenticated:
            return dcc.Location(pathname='/home', id='redirect-to-home', refresh=True)
        return dash.page_container
    
@callback(
    Output("update-prompt-button", "disabled"),
    Input("update-prompt-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_disable(n_clicks):
    return [True]



@callback(
    Output('next-question-input-1', "value"),
    Output('next-question-input-2', "value"),
    Output('system-prompt-input', "value"),
    Output('persona-prompt-input', "value"),
    Output('prefix-prompt-input', "value"),
    Input("reset-prompt-button", "n_clicks"),
    prevent_initial_call=True
)
def reset_default_prompts(n_clicks):
    return [
        "Generate the next question that the user might ask",
        "Generate the next question that the user might ask",
        ("You are an expert in dealing with bias in datasets for data science. \n"
                    "Your expertise includes identifying, measuring, and mitigating biases in tabular datasets.\n"
                    "You are well-versed in advanced statistical methods, machine learning techniques, and ethical considerations for fair AI.\n"
                    "You can provide detailed explanations of bias detection methods, offer actionable recommendations for bias mitigation, and guide users through complex scenarios with step-by-step instructions.\n" 
                    "Your goal is to ensure datasets are fair, transparent, and robust for accurate and equitable AI model/business development."),
        'My professional role is {{professional_role}}. I am working in {{industry_sector}} industry. My level of expertise in data analysis is {{expertise_level}}',
        ("You have already been provided with a dataframe df, all queries should be about that df.\n"
                "Do not create dataframe. Do not read dataframe from any other sources. Do not use pd.read_clipboard.\n"
                "If your response includes code, it will be executed, so you should define the code clearly.\n"
                "Code in response will be split by \\n so it should only include \\n at the end of each line.\n"
                "Do not execute code with 'functions', only use 'python_repl_ast'.")
    ]