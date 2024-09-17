from UI.app import app
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from UI.variable import global_vars
from UI.functions import *


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
        # Create a plotly figure (example figure)
        # fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[i + 1, i + 2, i + 3], mode='lines+markers')])
        # fig.update_layout(title=f'Graph {i + 1}')

        # Create a dcc.Graph component with the figure
        graph = dcc.Graph(id=f'graph-{i}', figure=fig)

        # Append the graph to the list of graphs
        graphs.append(graph)
    graphs += [
        html.Div(html.Button('Explain Charts', id='explain_graph_button', n_clicks=0, className='primary-button'),
                 className='right-align-div'), ]
    warning_msg = ""
    if warning:
        warning_msg = html.P([
            f"Warning: The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values cannot be visualized due to heavy computation load."],
            style={'color': 'red'})
    return graphs, warning_msg, bias_stats.to_dict('records'), bias_report_content, styles
