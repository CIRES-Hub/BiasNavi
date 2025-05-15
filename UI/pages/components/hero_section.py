import dash_bootstrap_components as dbc
from dash import dcc, html

def hero_section():
    return html.Div([
            dcc.Store(id="hero-dismissed", data=False),
            dcc.Interval(id="hero-auto-dismiss", interval=8000, n_intervals=0, max_intervals=1),
            # ===== Hero Section (ALWAYS PRESENT, STYLE TOGGLE) =====
            html.Div(
                id="hero-section",
                className="hero-section",
                children=[
                    html.Button("×", id="hero-close", n_clicks=0, className="hero-close-btn",
                                style={"position": "absolute", "top": "10px", "right": "18px",
                                       "background": "transparent", "border": "none", "fontSize": "2rem",
                                       "color": "#fff", "cursor": "pointer", "zIndex": 2}),
                    html.H1("Welcome to BiasNavi"),
                    html.P(
                        "Navigate, analyze, and adapt your datasets with ease. Harness the power of modern AI to identify, measure, and mitigate bias in your data workflows.")
                ],
                style={"position": "relative"}
            )
        ])
