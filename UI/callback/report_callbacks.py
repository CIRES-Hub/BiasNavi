from UI.app import app
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from UI.functions import *
from dash import MATCH
import plotly.io as pio
import base64
from flask_login import current_user


@app.callback(
    Output('graphs-container', 'children'),
    Output('plot-exception-msg', 'children'),
    Output('bias-stats', 'children'),
    Output('bias-report', 'children'),
    Output('table-overview', 'style_data_conditional'),
    Input('column-names-dropdown', 'value'),
    Input('table-overview', 'style_data_conditional'),
    prevent_initial_call=True
)
def generate_bias_report(target, styles):
    if global_vars.df[target].unique().size > 100:
        return [], html.P([
            "INFO: The selected target has more than 100 unique values, which cannot be plotted due to heavy computation load."],
            style={'color': 'gray'}), [], "", styles
    sensitive_attrs = identify_sensitive_attributes(global_vars.df, target)
    attr_text = ','.join(sensitive_attrs)
    query = f"""
            We have manually identified certain attributes in the dataset including {attr_text}, which may influence the fairness of the target attribute {target}. 
            Based on the dataset and our prior discussions, could you confirm if these attributes are indeed sensitive? 
            Additionally, feel free to reason whether other attributes could be included or if any of the identified sensitive attributes have been misclassified.            
            Please format your output as follows: list the sensitive attributes separated by commas, followed by a period. 
            Then, provide an explanation of why these attributes are considered sensitive.
            """
    answer, media, suggestions, stage = query_llm(query, global_vars.current_stage, current_user.id)

    if not sensitive_attrs:
        return [], html.P(["No sensitive attributes are detected."]), [], [], styles
    column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                    sensitive_attrs]
    styles += column_style

    # draw_multi_dist_plot(global_vars.df, "decile_score", sensitive_attrs)

    bias_report_content = html.Div([
        html.Br(),
        html.H3("Identified sensitive attributes", style={'textAlign': 'center'}),
        dcc.Markdown(answer)
    ])

    if target in sensitive_attrs:
        return [], html.P(["INFO: The selected target attribute must not be in the sensitive attributes."],
                          style={'color': 'gray'}), [], bias_report_content, styles

    refined_attrs = []
    warning = False
    filtered_attrs = []
    for attr in sensitive_attrs:
        if global_vars.df[attr].unique().size < 100:
            refined_attrs.append(attr)
        else:
            warning = True
            filtered_attrs.append(attr)

    figures = draw_multi_dist_plot(global_vars.df, target, refined_attrs)
    graphs = [html.Hr(),
              html.H3("Distributions", style={'textAlign': 'center'})]
    for i, fig in enumerate(figures):
        # Create a dcc.Graph component with the figure
        graphs.append(dcc.Graph(id={"type": "report-graph", "index": str(i)}, figure=fig))
        graphs.append(dcc.Loading(
            html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display": "none"})))
        graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0,
                                  className='primary-button'))

    bias_stats = [calculate_demographic_report(global_vars.df, target, [refined_attr]) for refined_attr in
                  refined_attrs]
    tables = []
    for table_id, stat in enumerate(bias_stats):
        data_table = dash_table.DataTable(id={"type": "report-table", "index": str(table_id)}, page_size=25,
                                          page_action='native',
                                          data=stat.to_dict('records'),
                                          sort_action='native',
                                          style_cell={'textAlign': 'center',
                                                      'fontFamiliy': 'Arial'},
                                          style_header={'backgroundColor': '#614385',
                                                        'color': 'white',
                                                        'fontWeight': 'bold'
                                                        }, style_table={'overflowX': 'auto'},
                                          style_data_conditional=[
                                              {
                                                  'if': {'row_index': 'odd'},
                                                  'backgroundColor': '#f2f2f2'
                                              },
                                              {
                                                  'if': {'row_index': 'even'},
                                                  'backgroundColor': 'white'
                                              },
                                          ],
                                          )
        tables.append(data_table)
        tables.append(dcc.Loading(
            html.Div([], id={"type": "report-table-explanation", "index": str(table_id)}, style={"display": "none"})))
        tables.append(html.Button('Explain', id={"type": "report-table-button", "index": str(table_id)}, n_clicks=0,
                                  className='primary-button'))

    warning_msg = ""
    if warning:
        warning_msg = html.P([
            f"INFO: The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values cannot be visualized due to heavy computation load."],
            style={'color': 'gray'})
    return graphs, warning_msg, tables, bias_report_content, styles


@app.callback(
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'style'),
    Input({'type': 'report-graph-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'report-graph', 'index': MATCH}, 'figure'),
    prevent_initial_call=True
)
def explain_report_figure(n_clicks, fig):
    if n_clicks and n_clicks > 0 and fig is not None:
        img_bytes = pio.to_image(fig, format='png')
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        explanation = global_vars.agent.describe_image('Describe this subgroup distribution chart.',
                                                       f"data:image/png;base64,{encoded_img}")
        return dcc.Markdown(explanation.content, className="chart-explanation"), {"display": "block"}


@app.callback(
    Output({'type': 'report-table-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'report-table-explanation', 'index': MATCH}, 'style'),
    Input({'type': 'report-table-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'report-table', 'index': MATCH}, 'data'),
    prevent_initial_call=True
)
def explain_report_table(n_clicks, tb):
    if n_clicks and n_clicks > 0 and tb is not None:
        data_string = "\n".join(
            [f"Row {i + 1}: {row}" for i, row in enumerate(tb)]
        )
        query = f"Explain this table data {data_string} given the distance metric in the table header. The distance figure is calculated by comparing the distribution of the subgraph with the distribution of all."
        answer, media, suggestions, stage = query_llm(query, global_vars.current_stage, current_user.id)
        return dcc.Markdown(answer, className="chart-explanation"), {"display": "block"}
