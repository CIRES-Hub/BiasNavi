import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import dash_daq as daq


def get_layout():
    return dbc.Container(fluid=True, children=[
        # =======================================================
        # banner and menu bar layout
        dbc.Row(justify="center", align="center", className="banner-row", children=[
            html.Div(children=[
                html.Img(src='../assets/logo.svg', className="logo"),
                html.P('BiasNavi', className="title"),
                # html.P('Navigate your way through biases in your data', className='lead')
                dbc.Nav(
                    [
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("Import Dataset", id="menu-import-data")],
                            label="Import",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                        ),
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("Export Chat History"), dbc.DropdownMenuItem("Export Dataset "
                                                                                               "Analysis Report")],
                            label="Export",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                        ),
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("Predefined Prompt 1"), dbc.DropdownMenuItem("Predefined Prompt 2"),
                             dbc.DropdownMenuItem("Custom Prompt")],
                            label="Prompts",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                        ),
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("OpenAI GPT 3.5"), dbc.DropdownMenuItem("OpenAI GPT 4.0"),
                             dbc.DropdownMenuItem("Llama 3")],
                            label="LLM Models",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                        ),
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("Hide ChatBox", id="menu-hide-chatbox"),
                             dbc.DropdownMenuItem("Hide Data View",id="menu-hide-dataview"),
                             dbc.DropdownMenuItem("Hide Chart View",id="menu-hide-chartview")],
                            label="View",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                        ),
                        dbc.NavLink("Help", href="", className='nav-item'),
                        dbc.NavLink("About CIRES", href="https://cires.org.au/", className='nav-item'),
                    ],
                    className='navbar'
                ),
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
                            html.H4("Chat with LLM", className="query-title"),
                            html.Button("Export", id="download-button", className="download-button"),
                            dcc.Download(id="export")
                        ], className="query-header"),
                        dcc.Loading(
                            id="loading-1",
                            children=[html.Div(id='query-area', className='query-area')],
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

                            html.Button('Send', id='send-button', n_clicks=0, className='send-button'),
                            dcc.Upload(id="upload-rag",
                                       children=html.Button('RAG', id='RAG-button', n_clicks=0, className='RAG-button'),
                                       multiple=True), html.Div(id='rag-output'),
                            daq.ToggleSwitch(
                                id='rag-switch',
                                style={'marginLeft': '10px'},
                                value=False,
                            ),
                            html.Div(id='rag-switch-output', style={'marginLeft': '10px'}),
                        ], className="query-div"),
                    ], className='query')
                ], className='card'),

                #RAG card
                dbc.Card(id="rag-card", style={'display': 'block'}, children=[
                    html.Div([
                        # RAG display area
                        html.H4("RAG Documents", className="query-title"),
                        dcc.Loading(
                            id="loading-2",
                            children=[html.Div(id='RAG-area', className='RAG-area')],
                            type="dot",  # Choose from "graph", "cube", "circle", "dot", or "default"
                        ),
                        # Message input row

                    ], className='query')
                ], className='card'),
            ]),

            # =======================================================
            #data views
            dbc.Col(width=6, id="middle-column", children=[
                dbc.Card(body=True, className='card', children=[
                    html.Div([
                        dcc.Input(id='input-start-row', type='number', placeholder='Start row',
                                  style={'margin-right': '10px'}),
                        dcc.Input(id='input-end-row', type='number', placeholder='End row',
                                  style={'margin-right': '10px'}),
                        html.Button('Show Rows', id='show-rows-button', className='load-button')
                    ], style={'marginBottom': '16px', 'height': '45px'}),
                    dash_table.DataTable(id='table-overview', page_size=25, page_action='native',
                                         style_cell={'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                         style_header={'backgroundColor': 'darkslateblue', 'color': 'white',
                                                       'fontWeight': 'bold'
                                                       }, style_table={'overflowX': 'auto'}),
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
                            html.H4("LLM Charts", className="query-title"),
                        ], className="query-header"),
                    ], className='llm-chart')
                ], className='card'),
            ]),

        ])
    ], className="body")
