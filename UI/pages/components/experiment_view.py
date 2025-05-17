import dash_bootstrap_components as dbc
from dash import dcc, html,dash_table

def experiment_view():
    return dbc.Card(id="evaluation-view", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 9},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Dataset Evaluation", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 9},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [


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
                        ], label="Experiment", className="scrollable-area"),
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
                        ],label="Comparison", className="scrollable-area")
                    ]
                )]
            ),
            id={"type": "collapse-card", "index": 9},
            is_open=True
        )
    ], className='card')