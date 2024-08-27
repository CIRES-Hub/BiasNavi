from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dash_editor_components.PythonEditor
import docker.errors
from db_models.conversation import Conversation
from db_models.users import User
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, ALL
import dash_daq as daq
import dash
from flask_login import logout_user, current_user
from dash.exceptions import PreventUpdate
import dash_editor_components
import time
import datetime

from agent import ConversationFormat

dash.register_page(__name__, path='/home/', title='Home')
import docker


def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=True, pathname="/login"),
        ])
    return html.Div([
        dbc.Container(fluid=True, children=[
            # =======================================================
            # banner and menu bar layout
            dbc.Row(justify="center", align="center", className="banner-row", children=[
                html.Div(children=[
                    html.Img(src='../assets/logo.svg', className="logo"),
                    html.P('BiasNavi', className="title"),
                    dbc.Nav(
                        className='navbar d-flex flex-wrap',
                        children=[
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem(
                                    "Import Dataset", id="menu-import-data")],
                                label="Import",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Export Chat History"), dbc.DropdownMenuItem(
                                    "Export Dataset Analysis Report")],
                                label="Export",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Predefined Prompt 1"),
                                 dbc.DropdownMenuItem("Predefined Prompt 2"),
                                 dbc.DropdownMenuItem("Custom Prompt")],
                                label="Prompts",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("GPT-4o-mini  ✔", id="menu-model-gpt4omini"),
                                 dbc.DropdownMenuItem("GPT-4", id="menu-model-gpt4"),
                                 dbc.DropdownMenuItem("GPT-4o", id="menu-model-gpt4o")],
                                label="LLM Models",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Hide ChatBox", id="menu-hide-chatbox"),
                                 dbc.DropdownMenuItem(
                                     "Hide Data View", id="menu-hide-dataview"),
                                 dbc.DropdownMenuItem("Hide Right View", id="menu-hide-chartview")],
                                label="View",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.NavLink("Help", href="", className='nav-item'),
                            dbc.DropdownMenu(
                                [
                                    dbc.DropdownMenuItem(
                                        "About CIRES", href="https://cires.org.au/"),
                                    dbc.DropdownMenuItem(
                                        "Logout", id="logout-button", href="#")
                                ],
                                label="More",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            )
                        ],
                    ),
                    dcc.Location(id='url', refresh=True)
                ], className='banner'),
            ]),

            # =======================================================
            # chatbox layout
            dbc.Row([
                dbc.Col(width=3, id="left-column", children=[
                    dbc.Card(children=[
                        html.Div(id="output-placeholder"),
                        dbc.Toast(
                            "Only the csv file is supported currently",
                            id="error-file-format",
                            header="Reminder",
                            is_open=False,
                            dismissable=True,
                            icon="danger",
                            duration=4000,
                        ),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and drop your data file here or ',
                                html.A(html.B('Browse files'))
                            ]),
                            style={"display": "none"},
                            className='upload',
                            multiple=True
                        )], className='card', style={"display": "none"}),
                    # User Profile Area
                    html.Div(id="user-profile-area", className="profile-area"),
                    dcc.Store(id="username-edit-success", data=False),
                    dbc.Card(children=[
                        html.Div([
                            # Chat display area
                            html.Div([
                                html.H4("Chat with BiasNavi",
                                        className="secondary-title")
                            ], className="query-header"),
                            html.Div([
                                dcc.Dropdown(id='export-format-dropdown', options=[
                                    v.value for v in ConversationFormat],
                                             value=ConversationFormat.SIMPLIFIED_JSON.value),
                                html.Button(
                                    "Export", id="download-button", className="download-button"),
                                dcc.Download(id="export")
                            ], className="query-header"),
                            dbc.Toast(
                                "Have you imported a dataset and entered a query?",
                                id="error-export",
                                header="Reminder",
                                is_open=False,
                                dismissable=True,
                                icon="danger",
                                duration=4000,
                            ),
                            dcc.Loading(
                                id="loading-1",
                                children=[
                                    html.Div(id='query-area', className='query-area')],
                                # dcc.Textarea(id='query-area', className='query-area', readOnly=True)],
                                type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                            ),
                            dbc.Toast(
                                "Have you imported a dataset and entered a query?",
                                id="error-query",
                                header="Reminder",
                                is_open=False,
                                dismissable=True,
                                icon="danger",
                                duration=4000,
                            ),
                            # generated follow-up questions
                            html.Div(id='next-suggested-questions'),

                            # Message input row
                            dcc.Input(id='query-input', type='text', className='query-input',
                                      placeholder='Type a query...'),

                            html.Div([

                                html.Button('Send', id='send-button',
                                            n_clicks=0, className='primary-button'),
                                dcc.Upload(id="upload-rag",
                                           children=html.Button(
                                               'RAG', id='RAG-button', n_clicks=0, className='secondary-button'),
                                           multiple=True), html.Div(id='rag-output'),
                                daq.ToggleSwitch(
                                    id='rag-switch',
                                    style={'marginLeft': '10px'},
                                    value=False,
                                ),
                                html.Div(id='rag-switch-output',
                                         style={'marginLeft': '10px'}),
                            ], className="center-align-div"),
                        ], className='query')
                    ], className='card'),

                    # RAG card
                    dbc.Card(id="rag-card", style={'display': 'block'}, children=[
                        html.Div([
                            # RAG display area
                            html.H4("RAG Documents", className="secondary-title"),
                            dcc.Loading(
                                id="loading-2",
                                children=[
                                    html.Div(id='RAG-area', className='RAG-area')],
                                type="dot",  # Choose from "graph", "cube", "circle", "dot", or "default"
                            ),
                            # Message input row

                        ], className='query'),
                    ], className='card'),
                    dbc.Card([
                        html.H4("Chat History",
                                className="secondary-title"),

                        dbc.CardBody([
                            html.Div(id="chat-history-content")
                        ])
                    ], className="mt-3"),
                    dcc.Store(id='chat-update-trigger', data=0)
                ]),

                # =======================================================
                # data views
                dbc.Col(width=6, id="middle-column", children=[
                    dbc.Card(body=True, className='card', children=[
                        dcc.Loading(id="table-loading", children=[html.Div([
                            html.H4(id="dataset-name"),
                            dcc.Input(id='input-start-row', type='number', placeholder='Start row',
                                      style={'margin': '10px', 'width': '10%'}),
                            dcc.Input(id='input-end-row', type='number', placeholder='End row',
                                      style={'margin': '10px', 'width': '10%'}),
                            html.Button('Show Rows', id='show-rows-button',
                                        className='load-button', style={'margin': '10px'}),
                            html.Button('Save Snapshot', id='open-modal-button',
                                        n_clicks=0, className='primary-button'),
                            html.Button('Download Data', id='download-data-button',
                                        n_clicks=0, className='secondary-button', style={'marginLeft': '10px'}),
                            dcc.Download(id='download-data-csv'),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader("Name This Dataset Snapshot"),
                                    dbc.ModalBody([
                                        dcc.Input(
                                            id="snapshot-name-input",
                                            type="text",
                                            placeholder="Enter a name",
                                            style={"width": "100%"}
                                        ),
                                    ]),
                                    dbc.ModalFooter([
                                        dbc.Button("Save", id="save-snapshot-button", className="ml-auto", n_clicks=0),
                                        dbc.Button("Close", id="close-snapshot-modal", className="ml-auto", n_clicks=0),
                                    ]),
                                ],
                                id="snapshot-modal",
                                is_open=False,
                            ),

                        ], ),
                            html.Div(children=[
                                dash_table.DataTable(id='table-overview', page_size=20, page_action='native',
                                                     editable=True, row_deletable=True, column_selectable='single',
                                                     style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                                     style_header={'backgroundColor': 'darkslateblue', 'color': 'white',
                                                                   'fontWeight': 'bold'
                                                                   },
                                                     style_table={'overflowX': 'auto'},
                                                     style_data_conditional=[
                                                         {
                                                             'if': {'row_index': 'odd'},
                                                             'backgroundColor': '#f2f2f2'
                                                         },
                                                         {
                                                             'if': {'row_index': 'even'},
                                                             'backgroundColor': 'white'
                                                         },
                                                     ]
                                                     )],
                                style={"margin": "15px", "marginLeft": "0px"}),
                        ],
                                    overlay_style={
                                        "visibility": "hidden", "opacity": .8, "backgroundColor": "white"},
                                    custom_spinner=html.H1(
                                        ["Loading data...", dbc.Spinner(color="primary")]),
                                    ),
                        html.Div(id='datatable-interactivity-container')
                    ]),

                    dbc.Card(body=True, className="card", children=[
                        dcc.Loading(id="report-loading", children=[
                            html.Div([
                                html.H2("Bias Report",
                                        style={'color': 'darkred', 'marginBottom': '20px', 'textAlign': 'center'}),
                                html.Div(children=[
                                    html.P(" Choose a column as the target attribute to generate bias report."),
                                    dcc.Dropdown(id='column-names-dropdown'),
                                    html.Div(id='plot-exception-msg'), ], style={'marginBottom': '20px'}),
                                html.Div(id="bias-report", className="bias-report-area", children=[]),
                                dcc.Tabs(id="report-tabs", value='tab-1', children=[
                                    dcc.Tab(label='Charts', children=[
                                        html.Div(id='graphs-container'),
                                    ]),
                                    dcc.Tab(label='Statistics', children=[
                                        html.Div(children=[
                                            html.Br(),
                                            html.H3("Statistics", style={'textAlign': 'center'}),
                                            dash_table.DataTable(id='bias-overview', page_size=25, page_action='native',
                                                                 sort_action='native',
                                                                 style_cell={'textAlign': 'center',
                                                                             'fontFamiliy': 'Arial'},
                                                                 style_header={'backgroundColor': 'darkslateblue',
                                                                               'color': 'white',
                                                                               'fontWeight': 'bold'
                                                                               }, style_table={'overflowX': 'auto'},
                                                                 style_data_conditional=[
                                                                     {
                                                                         'if': {'row_index': 'odd'},
                                                                         'backgroundColor': '#f2f2f2'
                                                                     },
                                                                     {
                                                                         'if': {'row_index': 'even'},
                                                                         'backgroundColor': 'white'
                                                                     },
                                                                 ]
                                                                 )
                                        ])
                                    ]),
                                ])

                            ])
                        ],
                                    overlay_style={
                                        "visibility": "hidden", "opacity": .8, "backgroundColor": "white"},
                                    custom_spinner=html.H2(
                                        ["Generating report...", dbc.Spinner(color="primary")]),
                                    ),
                    ]),
                    # dbc.Card(body=True, children=[
                    #     # dcc.Tabs(id='tabs-figures', value='single', children=[
                    #     #     dcc.Tab(label='Tab one', value='single'),
                    #     #     dcc.Tab(label='Tab two', value='pair'),
                    #     # ]),
                    #     # html.Div(id='tabs-output'),
                    #     "Select the attribute to visualize:\n",
                    #     dcc.Dropdown(id='column-names-dropdown'),
                    #     dcc.Graph(id='bar-chart'),
                    #     dcc.Graph(id='pie-chart')
                    # ], className='visualization')
                ]),

                dbc.Col(width=3, id="right-column", children=[

                    dbc.Card(children=[
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H4("Dataset Snapshots", style={'paddingLeft': 0}),
                                    html.Span(
                                        html.I(className="fas fa-question-circle"),
                                        id="tooltip-snapshot",
                                        style={
                                            "fontSize": "20px",
                                            "color": "#aaa",
                                            "cursor": "pointer",
                                            "margin-left": "5px",
                                            "alignSelf": "center"
                                        }
                                    )
                                ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                          "width": "100%"}),
                                dbc.Tooltip(
                                    "Click the Restore button to use the selected snapshot in the middle data view.",
                                    target="tooltip-snapshot",
                                ),
                            ]),

                            html.Div([
                                dash_table.DataTable(
                                    id="snapshot-table",
                                    row_selectable='single',
                                    columns=[
                                        {"name": "Version", "id": "ver"},
                                        {"name": "Description", "id": "desc"},
                                        {"name": "Timestamp", "id": "time"}
                                    ],
                                    style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                    style_header={'backgroundColor': 'darkslateblue', 'color': 'white',
                                                  'fontWeight': 'bold'
                                                  }, style_table={'overflowX': 'auto'},
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': '#f2f2f2'
                                        },
                                        {
                                            'if': {'row_index': 'even'},
                                            'backgroundColor': 'white'
                                        },
                                    ]
                                ),
                                html.Div([html.Button('Restore', id='restore-snapshot-button',
                                                      n_clicks=0, className='primary-button'),
                                          html.Button('Delete', id='delete-snapshot-button',
                                                      n_clicks=0, className='delete-button'),
                                          ], className='right-align-div'),
                            ], id='snapshot-area')
                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),

                    dbc.Card(children=[
                        html.Div([
                            html.Div([
                                html.H4("Dataset Evaluation", className="secondary-title")
                            ], className="query-header"),
                            html.Div([
                                html.Div([
                                    'Dataset Version:',
                                    dcc.Dropdown(
                                        id='dataset-selection',
                                        style={'width': '100%'},
                                    ),
                                    'Task:',
                                    dcc.Dropdown(
                                        ['Classification', 'Regression'],
                                        'Classification',
                                        style={'width': '100%'},
                                        id='task-selection'
                                    ), ], className='left-align-div'),
                                html.Div(html.Button('Run', id='eval-button',
                                                     n_clicks=0, className='primary-button'),
                                         className='right-align-div'),
                            ], id='evaluation-options')
                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),

                    dbc.Card(children=[
                        html.Div([
                            # Chat display area
                            html.Div([
                                html.H4("Charts", className="secondary-title")
                            ], className="query-header"),
                            html.Div([], id='llm-media-area')
                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),

                    dbc.Card(children=[
                        html.Div([
                            html.Div([
                                html.H4("Python Sandbox", style={'paddingLeft': 0}),
                                html.Span(
                                    html.I(className="fas fa-question-circle"),
                                    id="tooltip-code",
                                    style={
                                        "fontSize": "20px",
                                        "color": "#aaa",
                                        "cursor": "pointer",
                                        "margin-left": "5px",
                                        "alignSelf": "center"
                                    }
                                )
                            ], style={"display": "flex", "alignItems": "center","justifyContent": "space-between","width": "100%"}),
                            dbc.Tooltip(
                                "The variable df is a reference of the Pandas dataframe of the current dataset. "
                                "Any Modification on it will be reflected in the data view",
                                target="tooltip-code",
                            ),
                        ]),
                        html.Div([dash_editor_components.PythonEditor(id='commands-input',
                                                                      style={'height': '400px'}, value="")],
                                 className='commands_editor'),
                        html.Div([dbc.Button("Run", id="run-commands", n_clicks=0, className='primary-button')],
                                 className='right-align-div'),
                        dcc.Loading(
                            id="loading-1",
                            children=[html.P(id='console-area', className='query-area console-area')],
                            type="default",
                        ),
                    ], style={'padding': '15px'})
                ]),
            ])
        ], className="body")
    ])


@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('logout-button', 'n_clicks')],
    prevent_initial_call=True
)
def logout_and_redirect(n_clicks):
    if n_clicks:
        logout_user()
        return "/"
    raise PreventUpdate


# ================================================================
# =Chat history===================================================


def format_message(msg):
    role_class = "user-message" if msg['role'] == 'user' else "assistant-message"
    return html.Div([
        html.Div([
            html.Span(msg['role'].capitalize(), className="message-role"),
        ], className="message-header"),
        dcc.Markdown(msg['content'], className="message-content")
    ], className=f"chat-message {role_class}")


@callback(
    Output("chat-history-content", "children"),
    Input("url", "pathname"),
    Input("chat-update-trigger", "data")
)
def update_chat_history(pathname, trigger):
    user_id = str(current_user.id)
    conversations = Conversation.get_user_conversations(user_id)

    if not conversations:
        return [html.P("You don't have any chat history yet.")]

    history_blocks = []
    for idx, conv in enumerate(conversations):
        card_content = [
            dbc.CardHeader([
                html.H5(f"Dataset: {conv.dataset}", className="mb-0"),
                html.Small(f"Model: {conv.model}", className="text-muted"),
                html.Small(f"Last updated: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                           className="text-muted d-block")
            ]),
            dbc.CardBody([
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                [format_message(msg) for msg in conv.messages],
                                style={
                                    'maxHeight': '400px',  # Adjust this value as needed
                                    'overflowY': 'auto',
                                },
                                className="scrollable-conversation-body"
                            )
                        )
                    ),
                    id={"type": "collapse", "index": idx},
                    is_open=False,
                ),
                dbc.Button(
                    ["Show Messages ", html.I(
                        className="fas fa-chevron-down")],
                    id={"type": "collapse-button", "index": idx},
                    className="mt-3",
                    color="primary",
                    n_clicks=0,
                ),
            ])
        ]

        history_blocks.append(
                                dbc.Card(card_content, className="mb-3 chat-history-card")
                            )

    return history_blocks


@callback(
    Output({"type": "collapse", "index": MATCH}, "is_open"),
    Output({"type": "collapse-button", "index": MATCH}, "children"),
    Input({"type": "collapse-button", "index": MATCH}, "n_clicks"),
    State({"type": "collapse", "index": MATCH}, "is_open"),
)
def toggle_collapse(n_clicks, is_open):
    text = "Show Messages"
    if n_clicks:
        new_state = not is_open
        button_text = "Hide" if new_state else "Show"
        icon_class = "fas fa-chevron-up" if new_state else "fas fa-chevron-down"
        return new_state, [button_text, html.I(className=icon_class)]
    return is_open, ["Show", html.I(className="fas fa-chevron-down")]


# ================================================================
# =Chat history===================================================

@callback(
    Output("user-profile-area", "children"),
    Input("user-profile-area", "id"),
    Input("username-edit-success", "data")
)
def update_user_profile(trigger, edit_success):
    user = User.query.get(current_user.id)
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # dbc.Col([
                #     html.Img(src='/assets/default-avatar.png',
                #              className='profile-avatar mx-auto d-block',),
                # ], width=12, className='mb-3'),
                dbc.Col([
                    html.Div([
                        html.H5(user.username or user.email, id="username-display",
                                className='profile-name d-inline-block mb-0 me-2'),
                        html.I(className="fas fa-edit edit-icon",
                               id="edit-username-icon", )
                    ], className="d-flex align-items-center justify-content-center mb-1"),

                    dbc.Modal([
                        dbc.ModalHeader("Edit Username"),
                        dbc.ModalBody([
                            dbc.Input(
                                id="new-username-input", placeholder="Enter new username", type="text"),
                        ]),
                        dbc.ModalFooter([
                            dbc.Button("Save", id="save-username-button",
                                       className="ms-auto", n_clicks=0),
                            dbc.Button(
                                "Cancel", id="cancel-username-edit", className="ms-2", n_clicks=0),
                        ]),
                    ], id="edit-username-modal", is_open=False),
                    html.P(user.professional_role or "Role not specified",
                           className='profile-title text-center mb-3'),
                ], width=12),
                dbc.Button(
                    ["More Info ", html.I(
                        className="fas fa-chevron-down", id="more-info-icon")],
                    id="profile-more-info-button",
                    size="sm",
                    className="profile-more-info-button"
                ),
            ], className='align-items-center'),
            dbc.Collapse(
                dbc.CardBody([
                    html.Ul([
                        html.Li([
                            html.B("Industry: "),
                            html.Span(
                                user.industry_sector or 'Not provided')
                        ], className="mb-2"),
                        html.Li([
                            html.B("Expertise: "),
                            html.Span(
                                user.expertise_level or 'Not provided')
                        ], className="mb-2"),
                        html.Li([
                            html.B("Interests: "),
                            html.Span(', '.join(user.areas_of_interest)
                                      if user.areas_of_interest else 'None provided')
                        ]),
                    ], className="px-0", style={"margin-bottom": "0"})
                ], style={"padding-bottom": "0", }),
                id="profile-collapse",
                is_open=False,
            ),
        ])
    ], className="profile-area shadow-sm")


@callback(
    Output("more-info-icon", "className"),
    Output("profile-collapse", "is_open"),
    Input("profile-more-info-button", "n_clicks"),
    State("profile-collapse", "is_open"),
)
def toggle_collapse(n, is_open):
    if n:
        return ("fas fa-chevron-up" if not is_open else "fas fa-chevron-down"), not is_open
    return "fas fa-chevron-down", is_open


@callback(
    Output("commands-input", "disabled"),
    Output("run-commands", "disabled"),
    Input("run-commands", "n_clicks"),
    prevent_initial_call=True
)
def toggle_disable(n_clicks):
    return True, True
