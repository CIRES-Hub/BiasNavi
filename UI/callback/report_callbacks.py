from UI.app import app
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from UI.variable import global_vars
from UI.functions import *
from dash import callback_context, MATCH, ALL, ctx
import plotly.io as pio
import base64

@app.callback(
    Output('graphs-container', 'children'),
    Output('plot-exception-msg', 'children'),
    Output('bias-overview', 'data'),
    Output('bias-report', 'children'),
    Output('table-overview', 'style_data_conditional'),
    Input('column-names-dropdown', 'value'),
    Input('table-overview', 'style_data_conditional'),
    prevent_initial_call=True
)
def generate_bias_report(target, styles):
    if global_vars.df[target].unique().size > 100:
        return [], html.P([
            "Warning: The selected target has more than 100 unique values, which cannot be plotted due to heavy computation load."],
            style={'color': 'red'}), [], "", styles
    sensitive_attrs = identify_sensitive_attributes(global_vars.df, target)
    if not sensitive_attrs:
        return [], html.P(["No sensitive attributes are detected."]), [], [], styles
    column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                    sensitive_attrs]
    styles += column_style
    bias_identification = " ".join(sensitive_attrs)

    # draw_multi_dist_plot(global_vars.df, "decile_score", sensitive_attrs)

    bias_report_content = html.Div([
        html.Br(),
        html.H3("Identified sensitive attributes", style={'textAlign': 'center'}),
        html.P([
            html.B(f"{bias_identification}. ", style={'color': 'tomato'}),
            "When making decisions, it should be cautious to use these attributes."
        ])
    ])

    if target in sensitive_attrs:
        return [], html.P(["Warning: The selected target attribute must not be in the sensitive attributes."],
                          style={'color': 'red'}), [], bias_report_content, styles

    refined_attrs = []
    warning = False
    filtered_attrs = []
    for attr in sensitive_attrs:
        if global_vars.df[attr].unique().size < 100:
            refined_attrs.append(attr)
        else:
            warning = True
            filtered_attrs.append(attr)
    bias_stats = calculate_demographic_report(global_vars.df, target, refined_attrs)
    figures = draw_multi_dist_plot(global_vars.df, target, refined_attrs)
    graphs = [html.Hr(),
              html.H3("Distributions", style={'textAlign': 'center'})]
    for i, fig in enumerate(figures):
        # Create a dcc.Graph component with the figure
        graphs.append(dcc.Graph(id={"type": "report-graph", "index": str(i)}, figure=fig))
        graphs.append(dcc.Loading(
            html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display":"none"})))
        graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0, className='primary-button'))

    warning_msg = ""
    if warning:
        warning_msg = html.P([
            f"Warning: The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values cannot be visualized due to heavy computation load."],
            style={'color': 'red'})
    return graphs, warning_msg, bias_stats.to_dict('records'), bias_report_content, styles


@app.callback(
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'style'),
    Input({'type': 'report-graph-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'report-graph', 'index': MATCH}, 'figure'),
    prevent_initial_call=True
)
def show_figure_modal(n_clicks, fig):
    if n_clicks and n_clicks > 0 and fig is not None:
        img_bytes = pio.to_image(fig, format='png')
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        explanation = global_vars.agent.describe_image('Describe this subgroup distribution chart.', f"data:image/png;base64,{encoded_img}")
        return dcc.Markdown(explanation.content,className="chart-explanation"), {"display": "block"}