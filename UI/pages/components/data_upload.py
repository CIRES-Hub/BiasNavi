import dash_bootstrap_components as dbc
from dash import dcc, html

def data_upload():
    return  dbc.Card(children=[
                html.Div(id="output-placeholder"),
                dbc.Alert(
                    "Only the csv file is supported currently",
                    id="error-file-format",
                    is_open=False,
                    dismissable=True,
                    color="danger",
                    duration=5000,
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
                )], className='card', style={"display": "none"})