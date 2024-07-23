import dash_bootstrap_components as dbc
from models.conversation import Conversation
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, ALL
import dash_daq as daq
import dash
from flask_login import logout_user, current_user
from dash.exceptions import PreventUpdate

from agent import ConversationFormat
dash.register_page(__name__, path='/home/', title='Home')


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
                                [dbc.DropdownMenuItem("Predefined Prompt 1"), dbc.DropdownMenuItem("Predefined Prompt 2"),
                                 dbc.DropdownMenuItem("Custom Prompt")],
                                label="Prompts",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("GPT-3.5", id="menu-model-gpt3dot5"), dbc.DropdownMenuItem("GPT-4", id="menu-model-gpt4"),
                                 dbc.DropdownMenuItem("GPT-4o ✔", id="menu-model-gpt4o")],
                                label="LLM Models",
                                nav=True,
                                toggleClassName="dropdown-toggle",
                                className='menu-item'
                            ),
                            dbc.DropdownMenu(
                                [dbc.DropdownMenuItem("Hide ChatBox", id="menu-hide-chatbox"),
                                 dbc.DropdownMenuItem("Hide Data View", id="menu-hide-dataview"),
                                 dbc.DropdownMenuItem("Hide Chart View", id="menu-hide-chartview")],
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
                    dbc.Card(children=[
                        html.Div([
                            # Chat display area
                            html.Div([
                                html.H4("Chat with BiasNavi", className="query-title")
                            ], className="query-header"),
                            html.Div([
                                dcc.Dropdown(id='export-format-dropdown', options=[v.value for v in ConversationFormat], value=ConversationFormat.SIMPLIFIED_JSON.value),
                                html.Button("Export", id="download-button", className="download-button"),
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
                            # Message input row
                            dcc.Input(id='query-input', type='text', className='query-input',
                                      placeholder='Type a query...'),

                            html.Div([

                                html.Button('Send', id='send-button',
                                            n_clicks=0, className='send-button'),
                                dcc.Upload(id="upload-rag",
                                           children=html.Button(
                                               'RAG', id='RAG-button', n_clicks=0, className='RAG-button'),
                                           multiple=True), html.Div(id='rag-output'),
                                daq.ToggleSwitch(
                                    id='rag-switch',
                                    style={'marginLeft': '10px'},
                                    value=False,
                                ),
                                html.Div(id='rag-switch-output',
                                         style={'marginLeft': '10px'}),
                            ], className="query-div"),
                        ], className='query')
                    ], className='card'),

                    # RAG card
                    dbc.Card(id="rag-card", style={'display': 'block'}, children=[
                        html.Div([
                            # RAG display area
                            html.H4("RAG Documents", className="query-title"),
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
                        html.H4("Chat History"),
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
                            dcc.Input(id='input-start-row', type='number', placeholder='Start row',
                                      style={'marginRight': '10px'}),
                            dcc.Input(id='input-end-row', type='number', placeholder='End row',
                                      style={'marginRight': '10px'}),
                            html.Button('Show Rows', id='show-rows-button',
                                        className='load-button')
                        ], style={'marginBottom': '16px', 'height': '45px'}),
                        dash_table.DataTable(id='table-overview', page_size=25, page_action='native',
                                         style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                         style_header={'backgroundColor': 'darkslateblue', 'color': 'white',
                                                       'fontWeight': 'bold'
                                                       }, style_table={'overflowX': 'auto'}),
                        html.Div(id="bias-report",className="bias-report-area",children=[]),
                        html.Img(id="multi_dist_plot",style={'maxWidth': '100%', 'height': 'auto'}),
                        dash_table.DataTable(id='bias-overview', page_size=25, page_action='native',
                                             style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                             style_header={'backgroundColor': 'darkslateblue', 'color': 'white',
                                                           'fontWeight': 'bold'
                                                           }, style_table={'overflowX': 'auto'}),
                        ],
                        overlay_style={"visibility": "hidden", "opacity": .8, "backgroundColor": "white"},
                        custom_spinner=html.H2(["Loading data and identifying bias...", dbc.Spinner(color="primary")]),
                        ),
                    ]),
                    dbc.Card(body=True, children=[
                        # dcc.Tabs(id='tabs-figures', value='single', children=[
                        #     dcc.Tab(label='Tab one', value='single'),
                        #     dcc.Tab(label='Tab two', value='pair'),
                        # ]),
                        # html.Div(id='tabs-output'),
                        "Select the attribute to visualize:\n",
                        dcc.Dropdown(id='column-names-dropdown'),
                        dcc.Graph(id='bar-chart'),
                        dcc.Graph(id='pie-chart')
                    ], className='visualization')
                ]),

                dbc.Col(width=3, id="right-column", children=[
                    dbc.Card(children=[
                        html.Div([
                            # Chat display area
                            html.Div([
                                html.H4("LLM Charts", className="query-title")
                            ], className="query-header"),
                            html.Div([], id='llm-media-area')
                        ], className='llm-chart', style={'overflowX': 'auto'})
                    ], className='card'),
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
        collapse_id = f"collapse-{idx}"
        button_id = f"button-{idx}"

        card_content = [
            dbc.CardHeader(f"Dataset: {conv.dataset}"),
            dbc.CardBody([
                html.H5(f"Model: {conv.model}", className="card-title"),
                html.P(f"Last updated: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}", className="card-text"),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        html.Ul([html.Li(f"{msg['role']}: {msg['content']}", className="mb-2") for msg in conv.messages])
                    ])),
                    id={"type": "collapse", "index": idx},
                    is_open=False,
                ),
                dbc.Button(
                    "Show Messages",
                    id={"type": "collapse-button", "index": idx},
                    className="mt-3",
                    color="primary",
                    n_clicks=0,
                ),
            ])
        ]

        history_blocks.append(dbc.Card(card_content, className="mb-3"))

    return history_blocks


@callback(
    Output({"type": "collapse", "index": MATCH}, "is_open"),
    Input({"type": "collapse-button", "index": MATCH}, "n_clicks"),
    State({"type": "collapse", "index": MATCH}, "is_open"),
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
