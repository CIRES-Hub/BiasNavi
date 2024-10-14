import dash_bootstrap_components as dbc
import dash_editor_components.PythonEditor
from db_models.conversation import Conversation
from db_models.users import User
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, ALL, callback_context
import dash_daq as daq
import dash
from flask_login import logout_user, current_user
from dash.exceptions import PreventUpdate
import dash_editor_components
from agent import ConversationFormat
from utils.constant import DEFAULT_NEXT_QUESTION_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_PREFIX_PROMPT, DEFAULT_PERSONA_PROMPT


dash.register_page(__name__, path='/home/', title='Home')


def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=False, pathname="/"),
        ])
    return html.Div([
        # Home Layout
        dbc.Container(fluid=True, children=[
            # For user wizard
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="wizard-title")),
                    dbc.ModalBody(id="wizard-body",style={"fontSize": "0.7vw"}),
                    dbc.ModalFooter(
                        dbc.Button("Next", id="next-step", className="ms-auto", n_clicks=0)
                    ),
                ],
                id="wizard-modal",
                is_open=False,
                backdrop=False,  # Allow interaction with the underlying page
                style={"position": "absolute", "z-index": "1050", "color": "#614385"},  # Float above other elements
            ),
            dcc.Store(id="base-styles", data={}),
            html.Div(id="overlay",
                     style={"position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                            "backgroundColor": "rgba(0, 0, 0, 0.7)", "z-index": "100", "display": "none"}),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Upload a CSV Dataset",style={"color" : "#614385"})),
                    dbc.ModalBody(
                        dcc.Loading(
                            html.Div(
                                dcc.Upload(
                                    id='upload-data-modal',
                                    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                                    style={
                                        'width': '100%',
                                        'height': '120px',  # Adjusted height
                                        'lineHeight': '120px',  # Aligns the text vertically in the center
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px',
                                        'backgroundColor': '#f5f5f5',  # Set background color
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'alignItems': 'center',
                                    },
                                    multiple=True
                                ),
                                style={
                                    'display': 'flex',
                                    'justifyContent': 'center',
                                    'alignItems': 'center'
                                }
                            )
                        ),
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-modal", className="ml-auto")
                    ),
                ],
                id="upload-modal",
                is_open=True,
                centered=True,  # This ensures the modal is centered
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);"
                }
            ),
            # =======================================================
            # banner and menu bar layout
            dbc.Row(justify="center", align="center", children=[
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
                                className='menu-item',
                                id="menu-dataset",

                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Export Chat History"), dbc.DropdownMenuItem(
                                    "Export Dataset Analysis Report")],
                                label="Export",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            # dbc.DropdownMenu(
                            #     [dbc.DropdownMenuItem("Predefined Prompt 1"),
                            #      dbc.DropdownMenuItem("Predefined Prompt 2"),
                            #      dbc.DropdownMenuItem("Custom Prompt")],
                            #     label="Prompts",
                            #     nav=True,
                            #     toggleClassName="dropdown-toggle",
                            #     className='menu-item'
                            # ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("GPT-4o-mini  ✔", id="menu-model-gpt4omini"),
                                 dbc.DropdownMenuItem("GPT-4", id="menu-model-gpt4"),
                                 dbc.DropdownMenuItem("GPT-4o  ✔", id="menu-model-gpt4o")],
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
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Wizard", id="menu-help-wizard"),
                                 dbc.DropdownMenuItem("Tutorial", id="menu-help-tutorial"),],
                                label="Help",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item',
                                id="help-button"
                            ),
                            dbc.NavLink("Prompts", id="menu-prompt", className='nav-item'),

                            dbc.DropdownMenu(
                                [
                                    dbc.DropdownMenuItem(
                                        "About CIRES", href="https://cires.org.au/"),
                                    dbc.DropdownMenuItem(
                                        "Logout", id="logout-button", href="/")
                                ],
                                label="More",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            )
                        ],
                    ),
                    dcc.Location(id='url', refresh=False)
                ], className='banner'),
            ]),

            dbc.Card(id="setting-container",
                     children=[
                               html.H4("Prompt for Eliciting Model's ability"),
                               dcc.Textarea(rows=7, id="system-prompt-input", className="mb-4 prompt-input p-2",
                                            value=current_user.system_prompt),
                               html.H4("Prompt for Handling Dataset"),
                               dcc.Textarea(rows=7, id="prefix-prompt-input", className="mb-4 prompt-input p-2",
                                            value=current_user.prefix_prompt),
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
                               html.H4("Prompt for Generating Follow-up Questions"),
                               dcc.Textarea(rows=2, id="next-question-input-1", className="mb-4 prompt-input p-2",
                                            value=current_user.follow_up_questions_prompt_1),
                               # html.H4("Prompt for Generating Follow-up Questions 2"),
                               # dcc.Textarea(rows=2, id="next-question-input-2", className="mb-4 prompt-input p-2",
                               #              value=current_user.follow_up_questions_prompt_2),
                               dcc.Loading(id="update-prompt-loading", children=html.Div(children=[
                                   dbc.Button("Reset Default", id="reset-prompt-button", className="prompt-button",
                                              n_clicks=0),
                                   dbc.Button("Save", id="update-prompt-button", className="prompt-button", n_clicks=0),
                                   dbc.Button("Home", id="return-home-button", className="prompt-button", n_clicks=0),
                                   ], className="save-button"),
                               ),

                               dbc.Tooltip(
                                   "{{}} matches the field of the user information",
                                   target="tooltip-snapshot",
                               )],
                     className="prompt-card p-4", style={"display": "none"}),

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
                    dbc.Card(id="chat-box", children=[
                        html.Div([
                            # Chat display area
                            html.Div([
                                html.H4("Chat with BiasNavi", className="secondary-title")
                            ], className="query-header"),
                            html.Div([
                                dcc.Dropdown(id='export-format-dropdown', options=[
                                    v.value for v in ConversationFormat],
                                             value=ConversationFormat.SIMPLIFIED_JSON.value),
                                html.Button(
                                    "Export", id="download-button", className="primary-button"),
                                dcc.Download(id="export")
                            ], className="query-header"),
                            dcc.Loading(
                                id="loading-1",
                                children=[
                                    html.Div(id='query-area', className='query-area')],
                                # dcc.Textarea(id='query-area', className='query-area', readOnly=True)],
                                type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                            ),
                            dbc.Toast(
                                "Forget to import a dataset or enter a query?",
                                id="error-toast",
                                header="Reminder",
                                is_open=False,
                                dismissable=True,
                                icon="danger",
                                duration=4000,
                            ),
                            # generated follow-up questions
                            html.Div(id='next-suggested-questions'),

                            # Message input row
                            html.Div([
                                dcc.Input(id='query-input', type='text', className='query-input',
                                          placeholder='Type your message here'),
                                html.Button(html.Span(className="fas fa-paper-plane"), id='send-button',
                                            title="Send your message.", n_clicks=0,
                                            className='send-button'),

                                dcc.Upload(id="upload-rag",
                                           children=html.Button(html.Span(className="fas fa-file"), id='RAG-button',
                                                                title="Upload your document for RAG.", n_clicks=0,
                                                                className='send-button'),
                                           multiple=True),

                                html.Div(id='rag-output'),

                                daq.ToggleSwitch(id='rag-switch', value=False),

                                html.Div(id='rag-switch-output'),
                            ], className="center-align-div"),
                        ], className='query')
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
                        html.H4("Chat History", className="secondary-title"),

                        dbc.CardBody([
                            html.Div(id="chat-history-content")
                        ])
                    ], className="mt-3"),
                    dcc.Store(id='chat-update-trigger', data=0)
                ]),

                # =======================================================
                # data views
                dbc.Col(width=6, id="middle-column", children=[
                    dbc.Card(body=True, id='data-view', className='card', children=[
                        dcc.Loading(id="table-loading", children=[html.Div([
                            html.H5(id="dataset-name", className="dataset-name"),
                            dcc.Input(id='input-start-row', type='number', placeholder='Start row',
                                      style={'margin': '10px', 'width': '10%'}),
                            dcc.Input(id='input-end-row', type='number', placeholder='End row',
                                      style={'margin': '10px', 'width': '10%'}),
                            html.Button('Show Rows', id='show-rows-button',
                                        className='primary-button', style={'margin': '10px'}),
                            html.Button('Save Snapshot', id='open-modal-button',
                                        n_clicks=0, className='primary-button'),
                            html.Button('Download Data', id='download-data-button',
                                        n_clicks=0, className='primary-button', style={'marginLeft': '10px'}),
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
                                                     style_header={'backgroundColor': '#614385', 'color': 'white',
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

                    dbc.Card(body=True, id="report-view", className="card", children=[
                        dcc.Loading(id="report-loading", children=[
                            html.Div([
                                html.H2("Bias Report",
                                        style={'color': '#614385', 'marginBottom': '20px', 'textAlign': 'center'}),
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
                                                                 style_header={'backgroundColor': '#614385',
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

                    dbc.Card(id = "snapshot-view", children=[
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H4("Dataset Snapshots", style={'paddingLeft': 0}, className="secondary-title"),
                                    html.Span(
                                        html.I(className="fas fa-question-circle"),
                                        id="tooltip-snapshot",
                                        style={
                                            "fontSize": "20px",
                                            "color": "#aaa",
                                            "cursor": "pointer",
                                            "marginLeft": "5px",
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
                                    style_header={'backgroundColor': '#614385', 'color': 'white',
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
                                                      n_clicks=0, className='primary-button'),
                                          ], className='right-align-div'),
                            ], id='snapshot-area')
                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),

                    dbc.Card(id="evaluation-view", children=[
                        html.Div([
                            html.Div([
                                html.H4("Dataset Evaluation", className="secondary-title")
                            ], className="query-header"),
                            html.Div([
                                'Snapshot:',
                                dcc.Dropdown(
                                    id='dataset-selection',
                                    style={'width': '100%'},
                                    clearable=False
                                ),
                                'Sensitive Attribute:',
                                dcc.Dropdown(
                                    id='sensi-attr-selection',
                                    style={'width': '100%'},
                                    multi=True,
                                    clearable=False
                                ),
                                'Label:',
                                dcc.Dropdown(
                                    id='label-selection',
                                    style={'width': '100%'},
                                    clearable=False
                                ),
                            ], className='left-align-div'),
                            html.Div([
                                html.Div([
                                    'Task:',
                                    dcc.Dropdown(
                                        ['Classification', 'Regression'],
                                        'Classification',
                                        style={'width': '100%'},
                                        id='task-selection',
                                        clearable=False
                                    ),
                                    'Model:',
                                    dcc.Dropdown(
                                        ['SVM', 'Logistic', 'MLP'],
                                        'SVM',
                                        style={'width': '100%'},
                                        id='model-selection',
                                        clearable=False
                                    ),
                                ], className='left-align-div'),
                                html.Div(id='eval-info'),
                            ], id='evaluation-options'),
                            dcc.Loading(id="table-loading", children=[
                                html.Div(html.Button('Run', id='eval-button',
                                                     n_clicks=0, className='primary-button'),
                                         className='right-align-div'),
                                html.Div(
                                    children=[
                                        html.Div(id='eval-res', style={'marginBottom': '10px', 'marginTop': '10px'}),
                                        html.Div(id='fairness-scores')

                                    ]),
                            ], overlay_style={
                                "visibility": "hidden", "opacity": .8, "backgroundColor": "white"},
                                        custom_spinner=html.H3(
                                            ["Running...", dbc.Spinner(color="primary")]),
                            ),


                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),

                    dbc.Card(id="code-view", children=[
                        html.Div([
                            html.Div([
                                html.H4("Python Sandbox", style={'paddingLeft': 0}, className="secondary-title"),
                                html.Span(
                                    html.I(className="fas fa-question-circle"),
                                    id="tooltip-code",
                                    style={
                                        "fontSize": "20px",
                                        "color": "#aaa",
                                        "cursor": "pointer",
                                        "marginLeft": "5px",
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
                        html.Div([
                            html.H4("Console", className="secondary-title")
                        ], className="query-header"),
                        dcc.Loading(
                            id="loading-1",
                            children=[html.P(id='console-area', className='commands_result')],
                            type="default",
                        ),
                    ], style={'padding': '15px'})
                ]),
            ], id="home-container")
        ], className="body fade-in")
    ])


@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    Input('help-button', 'n_clicks'),
    Input('menu-prompt', 'n_clicks'),
    prevent_initial_call=True
)
def logout_and_redirect(logout_clicks, help_clicks, setting_clicks):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (logout_clicks is not None and logout_clicks > 0) or (help_clicks is not None and help_clicks > 0) or (setting_clicks is not None and setting_clicks > 0):
        if button_id == "logout-button":
            logout_user()
            return "/"
        if button_id == "help-button":
            return "/helps/"
        if button_id == "menu-prompt":
            return "/settings/prompts"

@callback(
    Output("setting-container", "style"),
    Output("home-container", "style"),
    Input("url", "pathname")
)
def show_page_content(pathname):
    if (pathname == "/home"):
        return {'display': 'none'}, {'display': 'flex'}

    if (pathname == "/settings/prompts"):
        return {'display': 'block'}, {'display': 'none'}
    return dash.no_update, dash.no_update


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
                            html.B("Technical Expertise: "),
                            html.Span(
                                user.technical_level or 'Not provided')
                        ], className="mb-2"),
                        html.Li([
                            html.B("Bias Awareness: "),
                            html.Span(
                                user.bias_awareness or 'Not provided')
                        ], className="mb-2"),
                        html.Li([
                            html.B("Interests: "),
                            html.Span(', '.join(user.areas_of_interest)
                                      if user.areas_of_interest else 'None provided')
                        ]),
                    ], className="px-0", style={"marginBottom": "0"}),
                    html.Div(
                        dbc.Button(
                                ["Edit User's Information"],
                                id="profile-edit-info-button",
                                size="sm",
                                className="profile-edit-info-button",
                                href="/survey"
                            ), style={"width": "100%", "display": "flex", "justifyContent": "center"}
                    )
                ], style={"paddingBottom": "0", }),
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


@callback(
    Output('next-question-input-1', "value"),
    Output('system-prompt-input', "value"),
    Output('persona-prompt-input', "value"),
    Output('prefix-prompt-input', "value"),
    Input("reset-prompt-button", "n_clicks"),
    prevent_initial_call=True
)
def reset_default_prompts(n_clicks):
    return [
        DEFAULT_NEXT_QUESTION_PROMPT,
        DEFAULT_SYSTEM_PROMPT,
        DEFAULT_PERSONA_PROMPT,
        DEFAULT_PREFIX_PROMPT
    ]

