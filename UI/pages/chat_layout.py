import dash_bootstrap_components as dbc
import dash_editor_components.PythonEditor
from db_models.conversation import Conversation
from db_models.users import User
from dash import dcc, html, dash_table, callback, Input, Output, State, MATCH, ALL
import dash_daq as daq
import dash
from flask_login import logout_user, current_user

dash.register_page(__name__, path='/chat/', title='Chat')


def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=True, pathname="/login"),
        ])

    return html.Div([
        dbc.Container(fluid=True, style={
            "display": "flex",
            "justifyContent": "center",  # Horizontally center
            "alignItems": "center",      # Vertically center
            "height": "100vh",           # 100% of the viewport height
            "width": "100vw",            # 100% of the viewport width
            "background": "linear-gradient(to right, #614385, #516395)"  # Example background
        }, children=[
            dcc.Location(id='url', refresh=True),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Upload a CSV Dataset", style={"color": "#614385"})),
                    dbc.ModalBody(
                        dcc.Loading(
                            html.Div(
                                dcc.Upload(
                                    id='upload-data-modal-chat',
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
                id="upload-modal-chat",
                is_open=True,
                centered=True,  # This ensures the modal is centered
                style={
                    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.2);"
                }
            ),

            dbc.Col(width=4, children=[
                # Chat Box Card
                dbc.Card(children=[
                    html.Div([
                        # Chat display area
                        html.Div([
                            html.H4("Chat with BiasNavi",
                                    className="secondary-title"),
                            dbc.Button("Log out", id="logout-button-chat", className="primary-button", style={"backgroundColor":"darkred"},n_clicks=0)
                        ], className="query-header",style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                                          "width": "100%"}),

                        dcc.Loading(
                            id="loading-1",
                            children=[
                                html.Div(id='query-area-chat', className='query-area')],
                            type="default",  # Choose from "graph", "cube", "circle", "dot", or "default"
                        ),
                        dbc.Toast(
                            "Forget to import a dataset or enter a query?",
                            id="error-toast-chat",
                            header="Reminder",
                            is_open=False,
                            dismissable=True,
                            icon="danger",
                            duration=4000,
                        ),
                        html.Div(id='next-suggested-questions-chat'),
                        # Message input row
                        html.Div([
                            dcc.Input(id='query-input-chat', type='text', className='query-input',
                                      placeholder='Type your message here'),
                            html.Button(html.Span(className="fas fa-paper-plane"), id='send-button-chat', title="Send your message.", n_clicks=0,
                                        className='send-button'),

                            dcc.Upload(id="upload-rag", children=html.Button(html.Span(className="fas fa-file"), id='RAG-button', title="Upload your document for RAG.", n_clicks=0,
                                                                             className='send-button'),
                                       multiple=True),

                            html.Div(id='rag-output'),

                            daq.ToggleSwitch(id='rag-switch', value=False, style={"display": "none"}),

                            html.Div(id='rag-switch-output'),
                        ], className="center-align-div"),

                    ], className='query')
                ], className='card'),
                # Charts Card
                dbc.Card(children=[
                    html.Div([
                        # Chart display area
                        html.Div([
                            html.H4("Charts", className="secondary-title")
                        ], className="query-header"),
                        html.Div([], id='llm-media-area-chat')
                    ], className='llm-chart', style={'overflowX': 'auto'})
                ], className='card', style={"display": "none"}),
                dbc.Card(id="rag-card", style={'display': 'none'}, children=[
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
            ])
        ])
    ])

