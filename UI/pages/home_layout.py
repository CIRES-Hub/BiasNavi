import dash_bootstrap_components as dbc
import dash_editor_components.PythonEditor
from db_models.conversation import Conversation
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, callback_context
import dash_daq as daq
import dash
from flask_login import logout_user, current_user
import dash_editor_components
from agent import ConversationFormat
from constant_prompt import DEFAULT_NEXT_QUESTION_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_PREFIX_PROMPT, \
    DEFAULT_PERSONA_PROMPT
import ast
from UI.pages.components.survey_modal import survey_modal
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path='/home/', title='Home')

pipeline_stages = ["Identify", "Measure", "Surface", "Adapt"]


# Callback to dismiss hero section
@callback(
    Output("hero-dismissed", "data"),
    Input("hero-close", "n_clicks"),
    Input("hero-auto-dismiss", "n_intervals"),
    State("hero-dismissed", "data"),
    prevent_initial_call=True
)
def dismiss_hero_section(close_clicks, auto_dismiss, dismissed):
    ctx = callback_context
    if dismissed:
        raise PreventUpdate
    if ctx.triggered:
        return True
    raise PreventUpdate

# Callback to toggle hero-section display
@callback(
    Output("hero-section", "style"),
    Input("hero-dismissed", "data"),
)
def toggle_hero_section_style(dismissed):
    if dismissed:
        return {"display": "none"}
    return {"position": "relative"}

def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=True, pathname="/"),
        ])
    return html.Div([
        # Home Layout
        dbc.Container(fluid=True, children=[
            dcc.Store(id="hero-dismissed", data=False),
            dcc.Interval(id="hero-auto-dismiss", interval=8000, n_intervals=0, max_intervals=1),
            # ===== Hero Section (ALWAYS PRESENT, STYLE TOGGLE) =====
            html.Div(
                id="hero-section",
                className="hero-section",
                children=[
                    html.Button("×", id="hero-close", n_clicks=0, className="hero-close-btn", style={"position": "absolute", "top": "10px", "right": "18px", "background": "transparent", "border": "none", "fontSize": "2rem", "color": "#fff", "cursor": "pointer", "zIndex": 2}),
                    html.H1("Welcome to BiasNavi"),
                    html.P("Navigate, analyze, and adapt your datasets with ease. Harness the power of modern AI to identify, measure, and mitigate bias in your data workflows.")
                ],
                style={"position": "relative"}
            ),
            # For user wizard
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="wizard-title")),
                    dbc.ModalBody(id="wizard-body", style={"fontSize": "0.7vw"}),
                    dbc.ModalFooter(
                        dbc.Button("Next", id="next-step", className="ms-auto", n_clicks=0)
                    ),
                ],
                id="wizard-modal",
                is_open=False,
                backdrop=False,  # Allow interaction with the underlying page
                style={"position": "fixed !important", "z-index": "1500", "color": "black"},
                # Float above other elements
            ),
            dcc.Store(id="base-styles", data={}),
            html.Div(id="overlay",
                     style={"position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                            "backgroundColor": "rgba(0, 0, 0, 0.7)", "z-index": "100", "display": "none"}),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Upload a CSV Dataset", style={"color": "#614385"})),
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
                    dbc.ModalFooter([
                        html.Div(id="upload-data-error-msg", style={"color": "red"}),
                        dbc.Button("Close", id="close-upload-modal", className="primary-button"),
                    ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'end',
                            'alignItems': 'center'
                        }
                    ),
                ],
                id="upload-modal",
                is_open=True,
                centered=True,
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);",
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Choose the target attribute/label", style={"color": "#614385"})),
                    dbc.ModalBody(
                        dcc.Dropdown(id="label-dropdown")
                    ),
                    dbc.ModalFooter([
                        dbc.Button("Confirm", id="confirm-label-button", className="primary-button"),
                    ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'end',
                            'alignItems': 'center'
                        }
                    ),
                ],
                id="label-modal",
                is_open=False,
                centered=True,
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);",
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Go to Rows", style={"color": "#614385"})),
                    dbc.ModalBody([
                        dcc.Input(id='input-start-row', type='number', placeholder='Start row',
                                  style={'margin': '10px', 'width': '30%'}),
                        dcc.Input(id='input-end-row', type='number', placeholder='End row',
                                  style={'margin': '10px', 'width': '30%'}),
                        ]
                    ),
                    dbc.ModalFooter([
                        dbc.Button("Confirm", id="confirm-row-button", className="primary-button"),
                    ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'end',
                            'alignItems': 'center'
                        }
                    ),
                ],
                id="row-selection-modal",
                is_open=False,
                centered=True,
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);",
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalBody(
                        children=html.Div(id="survey-modal-body"),
                    )
                ],
                id="survey-modal",
                is_open=False,
                centered=True,
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);"
                },
                backdrop_class_name="backdrop-survey-modal",
                content_class_name="content-survey-modal"
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Dataset Statistics"), close_button=True),
                    dbc.ModalBody(children=[html.Div(id="data-stat-body"),
                                            html.Div(id="data-stat-summary", style={"marginTop": "20px"})
                                            ]),
                    dbc.ModalFooter(children=[
                        dbc.Button("Analyze", id={'type': 'spinner-btn', 'index': 1}, className="ml-auto"),
                        dbc.Button("Close", id="data-stat-close", className="ml-auto")]
                    ),
                ],
                id="data-stat-modal",
                is_open=False,
                centered=True,
                size="xl",
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);",
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Exporting Options"),
                    dbc.ModalBody(
                        html.Div([
                            dcc.Dropdown(id='export-format-dropdown', options=[
                                v.value for v in ConversationFormat],
                                         value=ConversationFormat.SIMPLIFIED_JSON.value),
                        ], className="query-header"),
                    ),
                    dbc.ModalFooter([dbc.Button(
                        "Export", id="download-button", className="ml-auto"),
                        dcc.Download(id="export-conversation"), dbc.Button("Close", id="close", className="ml-auto")]),
                ],
                id="export-history-modal",
                centered=True,
                is_open=False,
            ),

            dbc.Modal(
                [
                    dbc.ModalHeader("Commonly Asked Questions"),
                    dbc.ModalBody(
                        dcc.Dropdown(
                            id="question-modal-list",
                            placeholder="Choose a question",
                        )
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Choose", id="question-modal-choose-btn", className="me-2", n_clicks=0),
                            dbc.Button("Close", id="question-modal-close-btn", n_clicks=0),
                        ],
                        className="d-flex justify-content-end"
                    ),
                ],
                id="question-modal",
                is_open=False,  # Initially not open
                centered=True,
            ),

            # =======================================================
            # banner and menu bar layout
            dbc.Row(justify="center", align="center", children=[
                html.Div(children=[
                    html.Img(src='../assets/logo.svg', className="logo"),
                    html.P('BiasNavi', className="title mb-1"),
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
                                [
                                    dbc.DropdownMenuItem("Export Chat History", id="menu-export-chat"),
                                    dbc.DropdownMenuItem(
                                        "Export Dataset Analysis Report")],
                                label="Export",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item',
                                id="menu-export",
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
                                [dbc.DropdownMenuItem("GPT-4o-mini", id="menu-model-gpt4omini"),
                                 dbc.DropdownMenuItem("GPT-4o  ✔", id="menu-model-gpt4o")],
                                label="LLM Models",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item',
                                id="menu-model",
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Hide ChatBox", id="menu-hide-chatbox"),
                                 dbc.DropdownMenuItem(
                                     "Hide Data View", id="menu-hide-dataview"),
                                 dbc.DropdownMenuItem("Hide Right View", id="menu-hide-chartview")],
                                label="View",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item',
                                id = "menu-view",
                            ),
                            dbc.NavLink("Prompts", id="menu-prompt", className='nav-item'),
                            dbc.NavLink("User Profile", id="menu-profile", className='nav-item'),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Wizard", id="menu-help-wizard"),
                                 dbc.DropdownMenuItem("Tutorial", id="menu-help-tutorial",
                                                      href="https://jayhuynh.github.io/biasnavi-website/"), ],
                                label="Help",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item',
                                id="menu-help"
                            ),
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
                     className="prompt-card p-4", style={"display": "none"}),

            # =======================================================
            # chatbox layout
            dbc.Row([
                dbc.Col(width=3, id="left-column", children=[
                    dbc.Card(children=[
                        html.Div(id="output-placeholder"),
                        dbc.Alert(
                            "Only the csv file is supported currently",
                            id="error-file-format",
                            is_open=False,
                            dismissable=True,
                            color="danger",
                            duration=5000,
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
                    dcc.Store(id="username-edit-success", data=False),
                    dcc.Store(id="survey-edit-success", data=False),

                    dbc.Card(id="pipeline-card",children=[

                        # Chat display area
                        html.Div([
                            html.H4("Bias Management Pipeline", className="secondary-title"),
                            html.Span(
                                html.I(className="fas fa-question-circle"),
                                id="tooltip-pipeline",
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
                            "You can manually choose the stage or let the AI assistant to proceed to the next stage. "
                            "The current stage is critical in content generation. The explanation of each stage is as "
                            "follows. Identify: Detect potential bias or fairness issues in the dataset or system. "
                            "Measure: Quantify the magnitude of detected biases using appropriate metrics. Surface: "
                            "Present the identified biases clearly and effectively to the user. Adapt: Provide "
                            "actionable tools or methods for mitigating biases based on user preferences.",
                            target="tooltip-pipeline",
                        ),
                        html.Div(
                            dcc.Slider(
                                id='pipeline-slider',
                                min=0,
                                max=len(pipeline_stages) - 1,
                                step=1,
                                marks={i: {"label": stage, 'style': {'font-size': '16px'}} for i, stage in
                                       enumerate(pipeline_stages)},
                                value=0,  # Default to the first stage
                            ),
                            style={"margin": "20px"}
                        ),
                        html.Div(
                            dbc.Alert(
                                f"The pipeline has proceeded to a new stage.",
                                id="pipeline-alert",
                                is_open=False,
                                dismissable=True,
                                color="primary",
                                duration=5000,
                            ),
                        ),
                        html.Div([html.P("Recommended Operation:", id="recommended-op", className="op-highlight"),
                                  html.Span(
                                      html.I(className="fas fa-question-circle"),
                                      id="tooltip-op",
                                      style={
                                          "fontSize": "20px",
                                          "color": "#aaa",
                                          "cursor": "pointer",
                                          "marginLeft": "5px",
                                          "alignSelf": "center"
                                      }
                                  )],
                                 style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                  "width": "100%"}),
                        dbc.Tooltip(
                            "",
                            target="tooltip-op",
                            id="tooltip-expl",
                        ),


                    ], className='card', style={"padding": "10px"}),

                    dbc.Card(id="chat-box", children=[
                        html.Div([

                            html.Div([
                                html.H4("Chat with BiasNavi", className="secondary-title"),
                                html.Button(id="common-question-btn", children="Common Questions",
                                            style={"backgroundColor": "white", "color": "grey", "border": "none"}, )
                            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                      "width": "100%"}),
                            html.Div(id='query-area', className='query-area'),

                            dbc.Alert(
                                "Forget to import a dataset or enter a query?",
                                id="error-alert",
                                is_open=False,
                                dismissable=True,
                                color="danger",
                                duration=5000,
                            ),
                            # generated follow-up questions



                            # Message input row
                            html.Div([
                                dcc.Loading(
                                    id="loading-1",
                                    children=[
                                        html.Div(id='next-suggested-questions', style={"marginBottom":"20px"}),
                                        html.Div(
                                            style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', "gap":"10px"},
                                            children=[
                                                        dcc.Input(id='query-input', type='text', className='query-input',
                                                                  placeholder='Type your message here'),
                                                        html.Button(html.Span(className="fas fa-paper-plane"), id='send-button',
                                                                    title="Send your message.", n_clicks=0,
                                                                    className='send-button'),

                                                        dcc.Upload(id="upload-rag",
                                                                   children=html.Button(html.Span(className="fas fa-file"),
                                                                                        id='RAG-button',
                                                                                        title="Upload your document for RAG.",
                                                                                        n_clicks=0,
                                                                                        className='send-button'),
                                                                   multiple=True),

                                                        # html.Div(id='rag-output'),
                                                        #
                                                        # daq.ToggleSwitch(id='rag-switch', value=False),
                                                        #
                                                        # html.Div(id='rag-switch-output'),
                                            ])
                                    ],
                                    # dcc.Textarea(id='query-area', className='query-area', readOnly=True)],
                                    type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                                ),

                            ], style={"marginTop":"20px", "marginBottom":"10px"}),
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
                            html.Div([
                                html.H4("RAG View", style={'paddingLeft': 0}, className="secondary-title"),
                                html.Div(
                                    [
                                        daq.ToggleSwitch(
                                            id='rag-switch',
                                            value=False,
                                            color="#67b26f",  # Green gradient for ON (matches your theme)
                                            size=48,  # Bigger for clarity (default is 36)
                                        ),
                                        html.Div(id='rag-switch-status', children="RAG is OFF.")
                                    ],
                                    style={"display": "flex", "alignItems": "center", "gap": "12px"}
                                )

                            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                      "width": "100%"}),
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
                        html.Div([
                            html.Button('Data Statistics', id='data-stat-button',
                                        n_clicks=0, className='primary-button', style={'margin': '10px 10px 10px 0'}),
                            html.Button('Save Snapshot', id='open-modal-button',
                                        n_clicks=0, className='primary-button', style={'margin': '10px'}),
                            html.Button('Reset Label', id='open-label-modal-button',
                                        n_clicks=0, className='primary-button', style={'margin': '10px'}),
                            html.Button('Download', id='download-data-button',
                                        n_clicks=0, className='primary-button', style={'margin': '10px'}),
                            html.Button('Go to Rows', id='show-rows-button',
                                        className='primary-button', style={'margin': '10px'}),

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
                        dcc.Loading(id="table-loading", children=[
                            html.Div(children=[
                                dash_table.DataTable(id='table-overview', page_size=10, page_action='native',
                                                     editable=True, row_deletable=True, column_selectable='single',
                                                     style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial',"padding":"0px 10px"},
                                                     # style_header={'backgroundColor': '#614385', 'color': 'white',
                                                     #               'fontWeight': 'bold'
                                                     #               },
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
                            target_components={"table-overview": ["data", "columns"] }
                        ),
                        dcc.Store("data-view-table-style",data=[
                                                         {
                                                             'if': {'row_index': 'odd'},
                                                             'backgroundColor': '#f2f2f2'
                                                         },
                                                         {
                                                             'if': {'row_index': 'even'},
                                                             'backgroundColor': 'white'
                                                         },
                                                     ]),
                        html.Div(id='datatable-interactivity-container'),
                        dbc.Alert(
                            "",
                            id="data-alert",
                            is_open=False,
                            dismissable=True,
                            color="primary",
                            duration=5000,
                        )
                    ]),

                    dbc.Card(body=True, id="report-view", className="card", children=[
                        html.Div([
                            html.Div([
                                html.H4("Bias Management", className="secondary-title")
                            ], className="query-header"),
                            html.Div(children=[
                                html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'},
                                        children=[
                                        html.Button('Identify Bias', id={'type': 'spinner-btn', 'index': 3},
                                                    n_clicks=0, className='primary-button', style={'margin': '10px 10px 10px 0'},
                                                    title="Detect potential bias or fairness issues in the dataset or system."),
                                        html.Button('Measure Bias', id={'type': 'spinner-btn', 'index': 4},
                                                    n_clicks=0, className='primary-button', style={'margin': '10px', "display": "none"},
                                                    title="Quantify the magnitude of detected biases using appropriate metrics."),
                                        html.Button('Surface Bias', id={'type': 'spinner-btn', 'index': 5},
                                                    n_clicks=0, className='primary-button', style={'margin': '10px', "display": "none"},
                                                    title="Present the identified biases clearly and effectively to the user"),
                                        html.Button('Adapt Bias', id={'type': 'spinner-btn', 'index': 6},
                                                    n_clicks=0, className='primary-button', style={'margin': '10px', "display": "none"},
                                                    title="Provide actionable tools or methods for mitigating biases based on user preferences.")
                                        ]
                                ),

                                dcc.Store(id='sensitive-attr-store', data={}),
                                html.Div(
                                    [
                                        html.Label("Target Attribute:",
                                                   style={"marginRight": "10px", "whiteSpace": "nowrap"}),
                                        # Add margin to the label
                                        dcc.Dropdown(
                                            id='column-names-dropdown',
                                            placeholder="Choose a column as the target attribute",
                                            style={"flex": "1"}  # Allow the dropdown to expand
                                        )
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginTop": "20px",
                                        "marginBottom": "20px"
                                    }
                                ),
                                dbc.Alert(
                                    "",
                                    id="report-alert",
                                    is_open=False,
                                    dismissable=True,
                                    color="warning",
                                    duration=5000,
                                )
                            ]),
                            html.Div(id="bias-identifying-area", className="section"),

                            html.Div(id='bias-measuring-area', className="table-container section"),

                            html.Div(id='bias-surfacing-area', className="section"),

                            html.Div(id='bias-adapting-area', className="section"),

                        ])
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

                    dbc.Card(id="snapshot-view", children=[
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
                                        {"name": "ID", "id": "ver"},
                                        {"name": "Description", "id": "desc"},
                                        {"name": "Timestamp", "id": "time"}
                                    ],
                                    style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial',"padding":"0px 10px"},
                                    # style_header={'backgroundColor': '#614385', 'color': 'white',
                                    #               'fontWeight': 'bold'
                                    #               }, style_table={'overflowX': 'auto'},
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
                            html.H4("Dataset Evaluation", className="secondary-title")
                        ], className="query-header"),
                        dbc.Tabs(
                            [
                            dbc.Tab(children=[
                                html.Div([

                                    html.Div([
                                        'Snapshot:',
                                        dcc.Dropdown(
                                            id='dataset-selection',
                                            style={'width': '70%'},
                                            clearable=False
                                        ),
                                        'Sensitive Attribute:',
                                        dcc.Dropdown(
                                            id='sensi-attr-selection',
                                            style={'width': '100%'},
                                            multi=True,
                                            clearable=False
                                        ),
                                    ], className='left-align-div'),
                                    html.Div([
                                        html.Div([
                                            'Label:',
                                            dcc.Dropdown(
                                                id='label-selection',
                                                style={'width': '100%'},
                                                clearable=False
                                            ),
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

                                    ], id='evaluation-options'),

                                    html.Div(html.Button('Run', id={'type': 'spinner-btn', 'index': 0},
                                                         n_clicks=0, className='primary-button'),
                                             className='right-align-div'),
                                    dbc.Alert(
                                        "",
                                        id="eval-info",
                                        is_open=False,
                                        dismissable=True,
                                        color="danger",
                                        duration=5000,
                                    ),
                                    html.Div(
                                        children=[
                                            html.Div(id='eval-res',
                                                     style={'marginBottom': '10px', 'marginTop': '10px'}),
                                            html.Div(id='fairness-scores'),
                                            html.Div(id='eval-explanation')

                                        ]),

                                ], className='llm-chart', style={'overflowX': 'auto'})
                            ], label="Experiment"),
                            dbc.Tab(children=[
                                dcc.Store(id="experiment-result", data=[]),
                                dash_table.DataTable(
                                    id='experiment-result-table',
                                    columns=[{'name': col, 'id': col} for col in ['Snapshot','Timestamp', "Result", 'Setting']],
                                    row_selectable='multi',
                                    selected_rows=[],
                                    data=[],
                                    style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial', "padding":"0px 10px"},
                                    # style_header={'backgroundColor': '#614385', 'color': 'white',
                                    #               'fontWeight': 'bold'
                                    #               }, style_table={'overflowX': 'auto'},
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
                                html.Div([
                                    html.Button('Compare', id={'type': 'spinner-btn', 'index': 10},
                                                         n_clicks=0, className='primary-button'),

                                    html.Button('Remove All', id="remove-all-result-btn",
                                                         n_clicks=0, className='primary-button'),
                                    ],
                                    className='right-align-div'),
                                dbc.Alert(
                                    "",
                                    id="comparison-alert",
                                    is_open=False,
                                    dismissable=True,
                                    color="danger",
                                    duration=5000,
                                ),
                                html.Div(id="chosen-experiment-res"),
                                html.Div(id='comparison-res'),
                            ],label="Comparison")
                            ]
                        )

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
                            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                      "width": "100%"}),
                            dbc.Tooltip(
                                "The variable df is a reference of the Pandas dataframe of the current dataset. "
                                "Any Modification on it will be reflected in the data view",
                                target="tooltip-code",
                            ),
                        ]),
                        html.Div([
                            html.Div([dash_editor_components.PythonEditor(id='commands-input',
                                                                          style={'overflow': "auto"}, value="")],
                                     className='commands_editor'),
                            html.Div([dbc.Button("Run", id={'type': 'spinner-btn', 'index': 9}, n_clicks=0, className='primary-button')],
                                     className='right-align-div'),
                            ], id="python-code-editor"),
                        html.Div([
                            html.Div([
                                html.H4("Console", className="secondary-title")
                            ], className="query-header"),
                            dcc.Loading(
                                id="loading-1",
                                children=[html.P(id='console-area', className='commands_result')],
                                type="default",
                            ),
                        ], id="python-code-console",style={"display":"none"}),
                    ], style={'padding': '15px'})
                ]),
            ], id="home-container"),
        ], className="body fade-in")
    ])


@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    Input('menu-help', 'n_clicks'),
    Input('menu-prompt', 'n_clicks'),
    prevent_initial_call=True
)
def logout_and_redirect(logout_clicks, help_clicks, setting_clicks):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (logout_clicks is not None and logout_clicks > 0) or (help_clicks is not None and help_clicks > 0) or (
            setting_clicks is not None and setting_clicks > 0):
        if button_id == "logout-button":
            logout_user()
            return "/"
        if button_id == "menu-help":
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
# =survey modal ===================================================

@callback(
    Output("survey-modal-body", "children"),
    Input("survey-edit-success", "data"),
    Input("username-edit-success", "data")
)
def update_survey_content(survey_update, username_update):
    return survey_modal()


# ================================================================
# =Chat history===================================================


def format_message(msg):
    role_class = "user-message" if msg['role'] == 'user' else "assistant-message"
    content = msg.get("content")
    try:
        parsed_content = ast.literal_eval(content)
        if isinstance(parsed_content, dict) and "answer" in parsed_content:
            text = parsed_content["answer"]
    except (ValueError, SyntaxError):
        # If it isn't a dictionary-like string, return the string as is
        text = content
    return html.Div([
        html.Div([
            html.Span(msg['role'].capitalize(), className="message-role"),
        ], className="message-header"),
        dcc.Markdown(text, className="message-content")
    ], className=f"chat-message {role_class}")


@callback(
    Output("chat-history-content", "children"),
    Input("url", "pathname"),
    Input("chat-update-trigger", "data")
)
def update_chat_history(pathname, trigger):
    if (pathname == '/'):
        return dash.no_update
    user_id = str(current_user.id)
    conversations = Conversation.get_user_conversations(user_id)

    if not conversations:
        return [html.P("You don't have any chat history yet.")]

    history_blocks = []
    for idx, conv in enumerate(conversations):
        card_content = [
            dbc.CardHeader([
                html.H5(f"Dataset: {conv.dataset}", className="card-title card-header mb-0"),
                html.Small(f"Model: {conv.model}", className="text-muted"),
                html.Small(f"Last updated: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                           className="text-muted d-block")
            ], className="card-header"),
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
    Output("more-info-icon", "className"),
    Output("profile-collapse", "is_open"),
    Input("profile-more-info-button", "n_clicks"),
    State("profile-collapse", "is_open"),
)
def toggle_collapse(n, is_open):
    if n:
        return ("fas fa-chevron-up" if not is_open else "fas fa-chevron-down"), not is_open
    return "fas fa-chevron-down", is_open


# @callback(
#     Output("commands-input", "disabled"),
#     Output("run-commands", "disabled"),
#     Input("run-commands", "n_clicks"),
#     prevent_initial_call=True
# )
# def toggle_disable(n_clicks):
#     return True, True


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


@callback(
    Output("survey-modal", "is_open"),
    Input("menu-profile", "n_clicks"),
    prevent_initial_call=True
)
def open_survey_modal(n_clicks):
    if n_clicks:
        return True
