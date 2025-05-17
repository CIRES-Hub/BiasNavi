import dash
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import dcc, html

from UI.pages.components.menu import menu
from UI.pages.components.modal import homepage_modal
from UI.pages.components.prompt_card import prompt_card
from UI.pages.components.pipeline import bias_pipeline
from UI.pages.components.chatbox import chatbox
from UI.pages.components.data_upload import data_upload
from UI.pages.components.rag_card import rag
from UI.pages.components.hero_section import hero_section
from UI.pages.components.data_view import data_view
from UI.pages.components.report_view import report_view
from UI.pages.components.dataset_snapshot import dataset_snapshot
from UI.pages.components.experiment_view import experiment_view
from UI.pages.components.code_view import code_view
from UI.pages.components.chat_history import chat_history
from UI.functions import format_message

dash.register_page(__name__, path='/home/', title='Home')

def layout():
    if not current_user.is_authenticated:
        return html.Div([
            dcc.Location(id="redirect-to-login",
                         refresh=True, pathname="/"),
        ])
    return html.Div([
        # Home Layout
        dbc.Container(fluid=True, children=[
            hero_section(),
            # ==========================================
            # banner and menu bar layout
            menu(),
            # prompt page (hide)
            prompt_card(),
            # all kinds of modals
            homepage_modal(),

            # =======================================================
            # chatbox layout
            dbc.Row([
                dbc.Col(width=5, id="left-column", children=[
                    # data upload
                    data_upload(),
                    dcc.Store(id="username-edit-success", data=False),
                    dcc.Store(id="survey-edit-success", data=False),

                    # pipeline widget
                    bias_pipeline(), #invisible by default
                    # chat box
                    chatbox(),
                    # RAG card
                    rag(), #invisible by default
                    # chat history
                    chat_history(), #invisible by default

                    dcc.Store(id='chat-update-trigger', data=0)
                ]),
                # =======================================================
                dbc.Col(width=7, id="middle-column", children=[
                    # data views
                    data_view(),
                    # report view
                    report_view() #invisible by default
                ]),

                dbc.Col(width=0, id="right-column", children=[
                    # data snapshot
                    dataset_snapshot(),
                    #experiment view
                    experiment_view(),
                    #chart and code
                    code_view(),
                ], style={"display": "none"}),
            ], id="home-container"),
        ], className="body fade-in")
    ])