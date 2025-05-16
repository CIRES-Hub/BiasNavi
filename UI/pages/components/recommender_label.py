import dash_bootstrap_components as dbc
from dash import dcc, html

def recommender_label():
    return dbc.Card(id="recommender-label",children=[
        html.Div([html.P("Next:", id="recommended-op", className="op-highlight"),
                  html.Span(
                      html.I(className="fas fa-question-circle"),
                      id="tooltip-op",
                      style={
                          "fontSize": "20px",
                          "color": "#aaa",
                          "cursor": "pointer",
                          "marginLeft": "5px",
                          "alignSelf": "center"
                      }
                  )],
                 style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                        "width": "100%", "padding": "0pt 10pt 0pt 0pt"}),
        dbc.Tooltip(
            "",
            target="tooltip-op",
            id="tooltip-expl",
        )

    ], className='card',  style={"padding": "0pt 0pt 0pt 5pt"})