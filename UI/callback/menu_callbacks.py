import time
import dash
from UI.app import app
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import ConversationFormat, DatasetAgent
import datetime
from dash import callback_context, MATCH
import io
from RAG import RAG
from dash import dcc, html, dash_table
import pandas as pd
from UI.variable import global_vars
from flask_login import current_user
from UI.functions import *
from utils.data_wrangler import DataWrangler


@app.callback(
    [Output('left-column', 'style'),
     Output('menu-hide-chatbox', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-chatbox', 'n_clicks')],
    [State('menu-hide-chatbox', 'children')],
    prevent_initial_call=True
)
def hide_chatbox(n_clicks, label):
    if label == 'Show ChatBox':
        return {'display': 'block'}, "Hide ChatBox", 3, 6, 3
    else:
        return {'display': 'none'}, "Show ChatBox", 0, 9, 3


@app.callback(
    [Output('middle-column', 'style'),
     Output('menu-hide-dataview', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-dataview', 'n_clicks')],
    [State('menu-hide-dataview', 'children')],
    prevent_initial_call=True
)
def hide_dataviews(n_clicks, label):
    if label == 'Show Data View':
        return {'display': 'block'}, "Hide Data View", 3, 6, 3
    else:
        return {'display': 'none'}, "Show Data View", 6, 0, 6


@app.callback(
    [Output('right-column', 'style'),
     Output('menu-hide-chartview', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-chartview', 'n_clicks')],
    [State('menu-hide-chartview', 'children')],
    prevent_initial_call=True
)
def hide_chartview(n_clicks, label):
    if label == 'Show Chart View':
        return {'display': 'block'}, "Hide Chart View", 3, 6, 3
    else:
        return {'display': 'none'}, "Show Chart View", 3, 9, 0


@app.callback(
    [Output('menu-model-gpt4omini', 'children', allow_duplicate=True),
     Output('menu-model-gpt4', 'children', allow_duplicate=True),
     Output('menu-model-gpt4o', 'children', allow_duplicate=True)],
    [Input('menu-model-gpt4omini', 'n_clicks'),
     Input('menu-model-gpt4', 'n_clicks'),
     Input('menu-model-gpt4o', 'n_clicks')],
    prevent_initial_call=True
)
def change_llm_model(n_clicks_gpt3dot5, n_clicks_gpt4, n_clicks_gpt4o):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if clicked_id == 'menu-model-gpt4omini':
        global_vars.agent.set_llm_model('gpt4omini')
        return "GPT-4o-mini ✔", "GPT-4", "GPT-4o"
    elif clicked_id == 'menu-model-gpt4':
        global_vars.agent.set_llm_model('gpt4')
        return "GPT-4o-mini", "GPT-4 ✔", "GPT-4o"
    elif clicked_id == 'menu-model-gpt4o':
        global_vars.agent.set_llm_model('gpt4o')
        return "GPT-4o-mini", "GPT-4", "GPT-4o ✔"

    raise dash.exceptions.PreventUpdate
