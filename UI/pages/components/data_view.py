import dash_bootstrap_components as dbc
from dash import dcc, html,dash_table

def data_view():
    return dbc.Card(body=True, id='data-view', className='card', children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 1},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Data View", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 1},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem","borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [
                    html.Div([
                        html.Button('Data Statistics', id='data-stat-button',
                                    n_clicks=0, className='primary-button', style={'margin': '10px'}),
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
                            style={"margin": "10px"}),
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
                ]
            ),
            id={"type": "collapse-card", "index": 1},
            is_open=True
        ),

    ])