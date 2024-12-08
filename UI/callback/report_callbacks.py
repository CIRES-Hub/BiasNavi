import dash

from UI.app import app
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from UI.functions import *
from dash import MATCH
import plotly.io as pio
import base64
from flask_login import current_user


@app.callback(
    Output('bias-identifying-area', 'children'),
    Output('table-overview', 'style_data_conditional'),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output('data-alert', 'children', allow_duplicate=True),
    Output('data-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 3}, 'children', allow_duplicate=True),
    Output("sensitive-attr-store", 'data'),
    Input({'type': 'spinner-btn', 'index': 3}, 'children'),
    State('column-names-dropdown', 'value'),
    State('table-overview', 'style_data_conditional'),
    prevent_initial_call=True
)
def identify_bias(_, target, styles):
    if global_vars.df is None:
        return "", dash.no_update, "No dataset is loaded.", True, dash.no_update, dash.no_update, "Identify Bias", {}
    if target is None:
        return "", dash.no_update, "Please choose a target before identifying bias.", True, dash.no_update, dash.no_update, "Identify Bias", {}
    sensitive_attrs = identify_sensitive_attributes(global_vars.df, target)
    if not sensitive_attrs:
        return [], dash.no_update, "No sensitive attributes are detected.", True, dash.no_update, dash.no_update, "Identify Bias", {}
    if target in sensitive_attrs:
        return [], dash.no_update, "The selected target is identified sensitive. Cannot Proceed!", True, dash.no_update, dash.no_update, "Identify Bias", {}

    attr_text = ','.join(sensitive_attrs)
    query = f"""
                We have manually identified certain attributes in the dataset including {attr_text}, which may 
                influence the fairness of the target attribute {target}. Based on the dataset and our prior 
                discussions, could you confirm if these attributes are indeed sensitive? Additionally, feel free to 
                reason whether other attributes could be included or if any of the identified sensitive attributes 
                have been misclassified. Please format your output as follows: First, highlight the sensitive 
                attributes. Then, provide an explanation of why these attributes are considered sensitive."""
    answer, media, suggestions, stage = query_llm(query, global_vars.current_stage, current_user.id)
    answer = format_reply_to_markdown(answer)
    column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                    sensitive_attrs]
    styles += column_style
    bias_report_content = html.Div([
        dcc.Markdown(answer, className="llm-text", style={"marginBottom": "30px"}),
    ])
    global_vars.agent.add_user_action_to_history("I have identified bias in this dataset")
    return [html.H4("Result of Bias Identifying"), bias_report_content], styles, "", False, "The sensitive attributes are highlighted in the data view.", True, "Identify Bias", {"sensitive_attrs": sensitive_attrs}


@app.callback(
    Output('bias-measuring-area', 'children', allow_duplicate=True),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 4}, 'children', allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 4}, 'children'),
    State('column-names-dropdown', 'value'),
    State('sensitive-attr-store', 'data'),
    prevent_initial_call=True
)
def measure_bias(_, target, sensitive_attrs):
    if global_vars.df is None:
        return "",  "No dataset is loaded.", True, "Measure Bias"
    if target is None:
        return "", "Please choose a target before measuring bias.", True, "Measure Bias"
    if sensitive_attrs == {}:
        return "",  "No biases are identified. Please identify bias first.", True, "Measure Bias"
    refined_attrs = []
    filtered_attrs = []
    warning = False
    for attr in sensitive_attrs["sensitive_attrs"]:
        if global_vars.df[attr].unique().size < 100:
            refined_attrs.append(attr)
        else:
            warning = True
            filtered_attrs.append(attr)
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
        tables.append(html.Button('Explain', id={"type": "report-table-button", "index": str(table_id)}, n_clicks=0,
                                  className='primary-button'))
        tables.append(html.Div([], id={"type": "report-table-explanation", "index": str(table_id)}, style={"display": "none"}))


    warning_msg = ""
    if warning:
        warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values are not presented due to space limit.",
    global_vars.agent.add_user_action_to_history("I have measured the bias in this dataset.")
    return [html.H4("Result of Bias Measuring")] + tables, warning_msg, warning, "Measure Bias"


@app.callback(
    Output('bias-surfacing-area', 'children', allow_duplicate=True),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 5}, 'children', allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 5}, 'children'),
    State('column-names-dropdown', 'value'),
    State('sensitive-attr-store', 'data'),
    prevent_initial_call=True
)
def surface_bias(_, target, sensitive_attrs):
    if global_vars.df is None:
        return "", dash.no_update, "No dataset is loaded.", True, "Surface Bias"
    if target is None:
        return "", dash.no_update, "Please choose a target before surfacing bias.", True, "Surface Bias"
    if sensitive_attrs == {}:
        return "", dash.no_update, "No biases are identified. Please Identify bias first.", True, "Surface Bias"
    refined_attrs = []
    filtered_attrs = []
    warning = False
    for attr in sensitive_attrs["sensitive_attrs"]:
        if global_vars.df[attr].unique().size < 100:
            refined_attrs.append(attr)
        else:
            warning = True
            filtered_attrs.append(attr)
    figures = draw_multi_dist_plot(global_vars.df, target, refined_attrs)
    graphs = []
    for i, fig in enumerate(figures):
        # Create a dcc.Graph component with the figure
        graphs.append(dcc.Graph(id={"type": "report-graph", "index": str(i)}, figure=fig))
        graphs.append(dcc.Loading(
            html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display": "none"})))
        graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0,
                                  className='primary-button'))
    warning_msg = ""
    if warning:
        warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values are not presented due to space limit.",
    global_vars.agent.add_user_action_to_history("I have measured the bias in this dataset.")
    return [html.H4("Result of Bias Surfacing")] + graphs, warning_msg, warning, "Surface Bias"

@app.callback(
    Output('bias-adapting-area', 'children', allow_duplicate=True),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 6}, 'children', allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 6}, 'children'),
    State('column-names-dropdown', 'value'),
    State('sensitive-attr-store', 'data'),
    prevent_initial_call=True
)
def adapt_bias(_, target, sensitive_attrs):
    if global_vars.df is None:
        return "", "No dataset is loaded.", True, "Adapt Bias"
    if target is None:
        return "", "Please choose a target before adapting bias.", True, "Adapt Bias"
    if sensitive_attrs == {}:
        return "", "No biases are identified. Please Identify bias first.", True, "Adapt Bias"

    button_area = html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'},children=[
                                    html.Button('Undersample', id={'type': 'bias-adapt-btn', 'index': 0},
                                                n_clicks=0, className='primary-button', style={'margin': '10px'}),
                                    html.Button('Oversample', id={'type': 'bias-adapt-btn', 'index': 1},
                                                n_clicks=0, className='primary-button', style={'margin': '10px'}),
                                    html.Button('Augmentation', id={'type': 'bias-adapt-btn', 'index': 2},
                                                n_clicks=0, className='primary-button', style={'margin': '10px'}),
                                   ]
                                )

    global_vars.agent.add_user_action_to_history("I have started to adapt the bias in this dataset.")
    return [html.H4("Result of Adapting Surfacing"), button_area], dash.no_update, dash.no_update, "Adapt Bias"

# @app.callback(
#     Output('bias-surfacing-area', 'children', allow_duplicate=True),
#     Output('report-alert', 'children', allow_duplicate=True),
#     Output('report-alert', 'is_open', allow_duplicate=True),
#     Output({'type': 'spinner-btn', 'index': 5}, 'children', allow_duplicate=True),
#     Input({'type': 'spinner-btn', 'index': 5}, 'children'),
#     State('column-names-dropdown', 'value'),
#     State('sensitive-attr-store', 'data'),
#     prevent_initial_call=True
# )
# def surface_bias(_, target, sensitive_attrs):
#     if global_vars.df is None:
#         return "", "No dataset is loaded.", True, "Surface Bias"
#     if target is None:
#         return "", "Please choose a target before surfacing bias.", True, "Surface Bias"
#     if sensitive_attrs == {}:
#         return "", "No biases are identified. Please Identify bias first.", True, "Surface Bias"
#     refined_attrs = []
#     filtered_attrs = []
#     warning = False
#     for attr in sensitive_attrs["sensitive_attrs"]:
#         if global_vars.df[attr].unique().size < 100:
#             refined_attrs.append(attr)
#         else:
#             warning = True
#             filtered_attrs.append(attr)
#     figures = draw_multi_dist_plot(global_vars.df, target, refined_attrs)
#     graphs = []
#     for i, fig in enumerate(figures):
#         # Create a dcc.Graph component with the figure
#         graphs.append(dcc.Graph(id={"type": "report-graph", "index": str(i)}, figure=fig))
#         graphs.append(dcc.Loading(
#             html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display": "none"})))
#         graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0,
#                                   className='primary-button'))
#     warning_msg = ""
#     if warning:
#         warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values are not presented due to space limit.",
#     global_vars.agent.add_user_action_to_history("I have measured the bias in this dataset.")
#     return [html.H4("Result of Bias Surfacing")] + graphs, warning_msg, warning, "Measure Bias"

# @app.callback(
#     Output('graphs-container', 'children'),
#     Output('report-alert', 'children', allow_duplicate=True),
#     Output('report-alert', 'is_open'),
#     Output('bias-stats', 'children'),
#     Output('bias-report', 'children'),
#     Output('table-overview', 'style_data_conditional'),
#     Input('column-names-dropdown', 'value'),
#     Input('table-overview', 'style_data_conditional'),
#     prevent_initial_call=True
# )
# def generate_bias_report(target, styles):
#     if global_vars.df[target].unique().size > 100:
#         return [], "The selected target has more than 100 unique values, which cannot be plotted due to heavy computation load.", True, [], "", styles
#     sensitive_attrs = identify_sensitive_attributes(global_vars.df, target)
#     attr_text = ','.join(sensitive_attrs)
#     query = f"""
#             We have manually identified certain attributes in the dataset including {attr_text}, which may influence the fairness of the target attribute {target}.
#             Based on the dataset and our prior discussions, could you confirm if these attributes are indeed sensitive?
#             Additionally, feel free to reason whether other attributes could be included or if any of the identified sensitive attributes have been misclassified.
#             Please format your output as follows: list the sensitive attributes separated by commas, followed by a period.
#             Then, provide an explanation of why these attributes are considered sensitive.
#             """
#     answer, media, suggestions, stage = query_llm(query, global_vars.current_stage, current_user.id)
#
#     if not sensitive_attrs:
#         return [], "No sensitive attributes are detected.", True, [], [], styles
#     column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
#                     sensitive_attrs]
#     styles += column_style
#
#     # draw_multi_dist_plot(global_vars.df, "decile_score", sensitive_attrs)
#
#     bias_report_content = html.Div([
#         html.Br(),
#         html.H3("Identified sensitive attributes", style={'textAlign': 'center'}),
#         dcc.Markdown(answer)
#     ])
#
#     if target in sensitive_attrs:
#         return [], "The selected target attribute must not be in the sensitive attributes.", True, [], bias_report_content, styles
#
#     refined_attrs = []
#     warning = False
#     filtered_attrs = []
#     for attr in sensitive_attrs:
#         if global_vars.df[attr].unique().size < 100:
#             refined_attrs.append(attr)
#         else:
#             warning = True
#             filtered_attrs.append(attr)
#
#     figures = draw_multi_dist_plot(global_vars.df, target, refined_attrs)
#     graphs = [html.Hr(),
#               html.H3("Distributions", style={'textAlign': 'center'})]
#     for i, fig in enumerate(figures):
#         # Create a dcc.Graph component with the figure
#         graphs.append(dcc.Graph(id={"type": "report-graph", "index": str(i)}, figure=fig))
#         graphs.append(dcc.Loading(
#             html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display": "none"})))
#         graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0,
#                                   className='primary-button'))
#
#     bias_stats = [calculate_demographic_report(global_vars.df, target, [refined_attr]) for refined_attr in
#                   refined_attrs]
#     tables = []
#     for table_id, stat in enumerate(bias_stats):
#         data_table = dash_table.DataTable(id={"type": "report-table", "index": str(table_id)}, page_size=25,
#                                           page_action='native',
#                                           data=stat.to_dict('records'),
#                                           sort_action='native',
#                                           style_cell={'textAlign': 'center',
#                                                       'fontFamiliy': 'Arial'},
#                                           style_header={'backgroundColor': '#614385',
#                                                         'color': 'white',
#                                                         'fontWeight': 'bold'
#                                                         }, style_table={'overflowX': 'auto'},
#                                           style_data_conditional=[
#                                               {
#                                                   'if': {'row_index': 'odd'},
#                                                   'backgroundColor': '#f2f2f2'
#                                               },
#                                               {
#                                                   'if': {'row_index': 'even'},
#                                                   'backgroundColor': 'white'
#                                               },
#                                           ],
#                                           )
#         tables.append(data_table)
#         tables.append(dcc.Loading(
#             html.Div([], id={"type": "report-table-explanation", "index": str(table_id)}, style={"display": "none"})))
#         tables.append(html.Button('Explain', id={"type": "report-table-button", "index": str(table_id)}, n_clicks=0,
#                                   className='primary-button'))
#
#     warning_msg = ""
#     if warning:
#         warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values cannot be visualized due to heavy computation load.",
#     return graphs, warning_msg, True if warning else False, tables, bias_report_content, styles


@app.callback(
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'report-graph-explanation', 'index': MATCH}, 'style'),
    Output({'type': 'report-graph-button', 'index': MATCH}, 'children',allow_duplicate=True),
    Input({'type': 'report-graph-button', 'index': MATCH}, 'children'),
    State({'type': 'report-graph', 'index': MATCH}, 'figure'),
    prevent_initial_call=True
)
def explain_report_figure(n_clicks, fig):
    if n_clicks and n_clicks > 0 and fig is not None:
        img_bytes = pio.to_image(fig, format='png')
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        explanation = global_vars.agent.describe_image('Describe this subgroup distribution chart.',
                                                       f"data:image/png;base64,{encoded_img}")
        explanation = format_reply_to_markdown(explanation.content)
        global_vars.agent.add_user_action_to_history("I have analyzed the result of bias surfacing and get the "
                                                     "following analysis."+explanation)
        return dcc.Markdown(explanation, className="llm-text"), {"display": "block"}, "Explain"


@app.callback(
    Output({'type': 'report-table-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'report-table-explanation', 'index': MATCH}, 'style'),
    Output({'type': 'report-table-button', 'index': MATCH}, 'children', allow_duplicate=True),
    Input({'type': 'report-table-button', 'index': MATCH}, 'children'),
    State({'type': 'report-table', 'index': MATCH}, 'data'),
    prevent_initial_call=True
)
def explain_report_table(_, tb):
    if tb is not None:
        data_string = "\n".join(
            [f"Row {i + 1}: {row}" for i, row in enumerate(tb)]
        )
        query = f"Explain this table data {data_string} given the distance metric in the table header. The distance figure is calculated by comparing the distribution of the subgraph with the distribution of all."
        answer, media, suggestions, stage = query_llm(query, global_vars.current_stage, current_user.id)
        answer = format_reply_to_markdown(answer)
        global_vars.agent.add_user_action_to_history("I have analyzed the result of bias measuring.")
        return dcc.Markdown(answer, className="llm-text"), {"display": "block"}, "Explain"
