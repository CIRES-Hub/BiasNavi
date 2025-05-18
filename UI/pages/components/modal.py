import dash_bootstrap_components as dbc
from dash import dcc, html
from agent import ConversationFormat

def homepage_modal():
    return html.Div(
        [# For user wizard
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
            )
        ]
    )