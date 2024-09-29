import dash_bootstrap_components as dbc
import dash_editor_components.PythonEditor
from db_models.conversation import Conversation
from db_models.users import User
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, ALL
import dash_daq as daq
import dash
from flask_login import logout_user, current_user
from dash.exceptions import PreventUpdate
import dash_editor_components
from agent import ConversationFormat

dash.register_page(__name__, path='/chat/', title='Chat')


def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=True, pathname="/login"),
        ])
    return html.Div([
        dbc.Container(fluid=True, children=[
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
                            dbc.NavLink("Prompts", id="setting-button", href="/settings/prompts", external_link=True,
                                        target="_blank", className='nav-item'),
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
            dbc.Col(width=4, id = "middle-column", children=[
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
                                "Export", id="download-button", className="primary-button"),
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
                            "Forget to import a dataset or enter a query?",
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



                        html.Div([
                            dcc.Input(id='query-input', type='text', className='query-input',
                                      placeholder='Type your message here'),
                            html.Button(html.Span(className="fas fa-paper-plane"), id='send-button', title="Send your message.", n_clicks=0,
                                        className='send-button'),

                            dcc.Upload(id="upload-rag", children=html.Button(html.Span(className="fas fa-file"), id='RAG-button', title="Upload your document for RAG.", n_clicks=0,
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
                    html.H4("Chat History",
                            className="secondary-title"),

                    dbc.CardBody([
                        html.Div(id="chat-history-content")
                    ])
                ], className="mt-3"),
                dcc.Store(id='chat-update-trigger', data=0)
            ])
        ])
    ])
