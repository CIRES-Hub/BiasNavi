import dash_bootstrap_components as dbc
from dash import dcc, html,dash_table

def dataset_snapshot():
    return dbc.Card(id="snapshot-view", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 8},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.Div([
                    html.H4("Dataset Snapshots", style={"margin": 0}, className="secondary-title"),
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
            ],
                id={"type": "toggle-btn", "index": 8},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [
                    html.Div([

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
                    ], className='llm-chart', style={'overflowX': 'auto'})]
            ),
            id={"type": "collapse-card", "index": 8},
            is_open=True
        )
    ], className='card')