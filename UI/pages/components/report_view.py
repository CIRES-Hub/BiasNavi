import dash_bootstrap_components as dbc
from dash import dcc, html

def report_view():
    return dbc.Card(body=True, id="report-view", className="card", children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 2},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.H4("Bias Management", style={"margin": 0}, className="secondary-title")
            ],
                id={"type": "toggle-btn", "index": 2},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem","borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.Label("Target Attribute:",
                                   style={"marginRight": "10px", "whiteSpace": "nowrap"}),
                        dcc.Dropdown(
                            id='column-names-dropdown',
                            placeholder="Choose a column as the target attribute",
                            style={"flex": "1"}
                        )
                    ], style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginTop": "20px",
                        "marginBottom": "20px"
                    }),

                    # Alert for bias report


                    # Output areas
                    html.Div(id="bias-identifying-area", className="section"),
                    html.Div(id='bias-measuring-area', className="section"),
                    html.Div(id='bias-surfacing-area', className="section"),
                    html.Div(id='bias-adapting-area', className="section"),
                ])
            ]),
            id={"type": "collapse-card", "index": 2},
            is_open=True
        ),
    ], style={"display": "none"})