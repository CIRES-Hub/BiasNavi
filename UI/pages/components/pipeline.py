import dash_bootstrap_components as dbc
from dash import dcc, html

def bias_pipeline():
    pipeline_stages = ["Identify", "Measure", "Surface", "Adapt"]
    return dbc.Card(id="pipeline-card",children=[
        dbc.CardHeader(
            html.Div([
                html.I(className="bi bi-chevron-down", id={"type": "toggle-icon", "index": 4},
                       style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}),
                html.Div([
                    html.H4("Bias Management Pipeline", style={"margin": 0}, className="secondary-title"),
                    html.Span(
                        html.I(className="fas fa-question-circle"),
                        id="tooltip-pipeline",
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
                    "You can manually choose the stage or let the AI assistant to proceed to the next stage. "
                    "The current stage is critical in content generation. The explanation of each stage is as "
                    "follows. Identify: Detect potential bias or fairness issues in the dataset or system. "
                    "Measure: Quantify the magnitude of detected biases using appropriate metrics. Surface: "
                    "Present the identified biases clearly and effectively to the user. Adapt: Provide "
                    "actionable tools or methods for mitigating biases based on user preferences.",
                    target="tooltip-pipeline",
                ),
            ],
                id={"type": "toggle-btn", "index": 4},
                style={"display": "flex", "alignItems": "center"}
            ),
            style={"backgroundColor": "white", "padding": "0.25rem 0.25rem", "borderBottom": "none"}
        ),

        dbc.Collapse(
            dbc.CardBody(
                [
                    html.Div(
                        dcc.Slider(
                            id='pipeline-slider',
                            min=0,
                            max=len(pipeline_stages) - 1,
                            step=1,
                            marks={i: {"label": stage, 'style': {'font-size': '16px'}} for i, stage in
                                   enumerate(pipeline_stages)},
                            value=0,  # Default to the first stage
                        ),
                        style={"margin": "20px"}
                    ),
                    html.Div(
                        dbc.Alert(
                            f"The pipeline has proceeded to a new stage.",
                            id="pipeline-alert",
                            is_open=False,
                            dismissable=True,
                            color="primary",
                            duration=5000,
                        ),
                    ),
                    html.Div([html.P("Recommended Operation:", id="recommended-op", className="op-highlight"),
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
                                    "width": "100%"}),
                    dbc.Tooltip(
                        "",
                        target="tooltip-op",
                        id="tooltip-expl",
                    ),]
            ),
            id={"type": "collapse-card", "index": 4},
            is_open=True
        )

    ], className='card', style={"padding": "10px"})