import dash
from UI.app import app
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from UI.functions import *
from dash import MATCH
import plotly.io as pio
import base64
from flask_login import current_user
import dash_bootstrap_components as dbc

from bias.identify import identify_sensitive_attributes
from bias.surface import draw_multi_dist_plot
from bias.measure import calculate_demographic_report
from bias.adapt import adapt_data


@app.callback(
    Output('bias-identifying-area', 'children'),
    Output('table-overview', 'style_data_conditional'),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output('data-alert', 'children', allow_duplicate=True),
    Output('data-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 3}, 'children', allow_duplicate=True),
    Output("sensitive-attr-store", 'data', allow_duplicate=True),
    Output("recommended-op", "children", allow_duplicate=True),
    Output("tooltip-expl", "children", allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 3}, 'children'),
    State('column-names-dropdown', 'value'),
    State('data-view-table-style', 'data'),
    prevent_initial_call=True
)
def identify_bias(_, target, styles):
    if global_vars.df is None:
        return "", dash.no_update, "No dataset is loaded.", True, dash.no_update, dash.no_update, "Identify Bias", {}, dash.no_update, dash.no_update
    if target is None:
        return "", dash.no_update, "Please choose a target before identifying bias.", True, dash.no_update, dash.no_update, "Identify Bias", {}, dash.no_update, dash.no_update
    sensitive_attrs = identify_sensitive_attributes(global_vars.df, target)
    if not sensitive_attrs:
        return [], dash.no_update, "No sensitive attributes are detected.", True, dash.no_update, dash.no_update, "Identify Bias", {}, dash.no_update, dash.no_update
    if target in sensitive_attrs:
        return [], dash.no_update, "The selected target is identified sensitive. Cannot Proceed!", True, dash.no_update, dash.no_update, "Identify Bias", {}, dash.no_update, dash.no_update

    attr_text = ','.join(sensitive_attrs)
    query = f"""
                We have identified certain attributes in the dataset including {attr_text}, which may 
                influence the fairness of the target attribute {target}. Based on the dataset and our prior 
                discussions, could you confirm if these attributes are indeed sensitive? Additionally, feel free to 
                reason whether other attributes could be included or if any of the identified sensitive attributes 
                have been misclassified. Please format your output as follows: First, highlight the sensitive 
                attributes. Then, provide an explanation of why these attributes are considered sensitive."""
    answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
    answer = format_reply_to_markdown(answer)
    column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                    sensitive_attrs]
    styles += column_style
    bias_report_content = html.Div([
        dcc.Markdown(answer, className="llm-text", style={"marginBottom": "20px"}),
    ])
    global_vars.agent.add_user_action_to_history("I have identified bias in this dataset.")

    sensitive_attrs_dropdown = dcc.Dropdown(
        id='identified-attrs-dropdown',
        style={'width': '100%'},
        options=[{'label': col, 'value': col} for col in global_vars.df.columns],
        multi=True,
        value=sensitive_attrs,
        clearable=True,
        placeholder="", )

    return html.Div([
    html.Div(
        [
            html.I(
                className="bi bi-chevron-down",
                id={"type": "toggle-msg-icon", "index": 1},
                style={
                    "cursor": "pointer",
                    "marginRight": "8px",
                    "fontSize": "1.2rem"
                }
            ),
            html.H4(
                "Result of Bias Identifying",
                style={"margin": 0}
            )
        ],
        id={"type": "toggle-msg-btn", "index": 1},
        style={
            "display": "flex",
            "alignItems": "center"
        }
    ),
    dbc.Collapse(
        [
            bias_report_content,
            html.B(
                "You can add or remove sensitive attributes here.",
                style={"marginBottom": "20px"}
            ),
            sensitive_attrs_dropdown
        ],
        id={"type": "collapse-msg", "index": 1},
        is_open=True
    )
]), styles, "", False, "The sensitive attributes are highlighted in the data view.", True, "Identify Bias", {"sensitive_attrs": sensitive_attrs}, op, expl


@app.callback(
    Output('sensitive-attr-store', 'data', allow_duplicate=True),
    Output('table-overview', 'style_data_conditional',allow_duplicate=True),
    Input('identified-attrs-dropdown', 'value'),
    State('data-view-table-style', 'data'),
    prevent_initial_call=True,
)
def update_sensitive_attrs(attrs, styles):
    column_style = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                    attrs]
    styles += column_style
    return {"sensitive_attrs": attrs}, styles


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
        return "", "No dataset is loaded.", True, "Measure Bias"
    if target is None:
        return "", "Please choose a target before measuring bias.", True, "Measure Bias"
    if sensitive_attrs == {}:
        return "", "No biases are identified. Please identify bias first.", True, "Measure Bias"
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
                                                      'fontFamiliy': 'Arial', "padding":"0px 10px"},
                                          # style_header={'backgroundColor': '#614385',
                                          #               'color': 'white',
                                          #               'fontWeight': 'bold'
                                          #               },
                                          style_table={'overflowX': 'auto',"marginTop":"10pt"},
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
        tables.append(
            html.Div([], id={"type": "report-table-explanation", "index": str(table_id)},
                     style={"display": "none", "marginBottom": "10pt"}))
        tables.append(html.Button(
            'Explain',
            id={"type": "report-table-button", "index": str(table_id)},
            n_clicks=0,
            className='primary-button',
            style={
                "margin": "10pt 0",
                "marginLeft": "auto",
                "marginRight": "0"
            }
        ))


    warning_msg = ""
    if warning:
        warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values are not presented due to space limit.",
    global_vars.agent.add_user_action_to_history("I have measured the bias in this dataset.")
    return html.Div([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-chevron-down",
                                id={"type": "toggle-msg-icon", "index": 2},
                                style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}
                            ),
                            html.H4("Result of Bias Measuring",style={"margin": 0})
                        ],
                        id={"type": "toggle-msg-btn", "index": 2},
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    dbc.Collapse(
                        tables,
                        id={"type": "collapse-msg", "index": 2},
                        is_open=True
                    )
                ]), warning_msg, warning, "Measure Bias"




@app.callback(
    Output('bias-surfacing-area', 'children'),
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
        graphs.append(
            html.Div([], id={"type": "report-graph-explanation", "index": str(i)}, style={"display": "none","marginBottom":"10pt"}))
        graphs.append(html.Button('Explain', id={"type": "report-graph-button", "index": str(i)}, n_clicks=0,
                                  className='primary-button'))
    warning_msg = ""
    if warning:
        warning_msg = f"The sensitive attribute(s): {', '.join(filtered_attrs)} with more than 100 unique values are not presented due to space limit.",
    global_vars.agent.add_user_action_to_history("I have measured the bias in this dataset.")
    return html.Div([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-chevron-down",
                                id={"type": "toggle-msg-icon", "index": 3},
                                style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}
                            ),
                            html.H4("Result of Bias Surfacing",style={"margin": 0})
                        ],
                        id={"type": "toggle-msg-btn", "index": 3},
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    dbc.Collapse(
                        graphs,
                        id={"type": "collapse-msg", "index": 3},
                        is_open=True
                    )
                ]), warning_msg, warning, "Surface Bias"


@app.callback(
    Output('bias-adapting-area', 'children'),
    Output('report-alert', 'children', allow_duplicate=True),
    Output('report-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 6}, 'children', allow_duplicate=True),
    Output("recommended-op", "children", allow_duplicate=True),
    Output("tooltip-expl", "children", allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 6}, 'children'),
    State('column-names-dropdown', 'value'),
    State('sensitive-attr-store', 'data'),
    prevent_initial_call=True
)
def adapt_bias(_, target, sensitive_attrs):
    if global_vars.df is None:
        return "", "No dataset is loaded.", True, "Adapt Bias", dash.no_update, dash.no_update
    if target is None:
        return "", "Please choose a target before adapting bias.", True, "Adapt Bias", dash.no_update, dash.no_update
    if sensitive_attrs == {}:
        return "", "No biases are identified. Please Identify bias first.", True, "Adapt Bias", dash.no_update, dash.no_update

    query = f""" Adapting bias will provide the user with a set of tools which allows them to interact with existing 
    biased results and to adapt them for bias in their preferred ways. Given these sensitive attributes 
    {",".join(sensitive_attrs)} and past analysis, could you recommend one of the following actions integrated in 
    BiasNavi: Evaluate the dataset to get more insights; Perform undersampling or oversampling to address class 
    imbalance; Augment new data instances for insufficient classes;

    or other actions to adapt bias? In your answer, you should highlight the recommended action. If the recommended 
    action is integrated in BiasNavi, you do not need to tell how to do it and just explain why I should take that 
    action."""
    answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
    answer = format_reply_to_markdown(answer)

    suggested_action = html.Div([
        dcc.Markdown(answer, className="llm-text", style={"marginBottom": "20px"}),
    ])

    button_area = html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', "marginTop":"20pt"}, children=[
        dcc.Loading(children=[
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start', 'gap': '15px'},
                     children=[
                         html.Div(style={'display': 'flex', 'gap': '10px'},
                                  children=[
                                      html.Button('Undersample', id="undersample-btn",
                                                  className='primary-button', style={'margin': '5px'},
                                                  title="Reduces the size of the majority class by randomly removing "
                                                        "samples to balance the dataset."),
                                      html.Button('Oversample', id="oversample-btn",
                                                  className='primary-button', style={'margin': '5px'},
                                                  title="Increases the size of the minority class by replicating its "
                                                        "samples or generating synthetic samples."),
                                      html.Button('Augmentation (SMOTE)', id="smote-btn",
                                                  className='primary-button', style={'margin': '5px'},
                                                  title="Generates synthetic samples for the minority class rather than "
                                                        "simply duplicating existing samples."),
                                  ]),
                         dcc.Dropdown(
                             id='adapting-attrs-dropdown',
                             style={'width': '100%', 'marginBottom': '20px'},
                             options=[{'label': col, 'value': col} for col in sensitive_attrs["sensitive_attrs"]],
                             placeholder="Choose the attribute(s) to adapt to...",
                         )
                     ]),

            dbc.Alert(
                "",
                id="adapting-alert",
                is_open=False,
                dismissable=True,
                color="primary",
                duration=5000,
            ),
        ]),
    ])

    global_vars.agent.add_user_action_to_history("I have started to adapt the bias in this dataset.")
    return  html.Div([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-chevron-down",
                                id={"type": "toggle-msg-icon", "index": 4},
                                style={"cursor": "pointer", "marginRight": "8px", "fontSize": "1.2rem"}
                            ),
                            html.H4("Result of Adapting Bias",style={"margin": 0})
                        ],
                        id={"type": "toggle-msg-btn", "index": 4},
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    dbc.Collapse(
                        [button_area,
                        suggested_action],
                        id={"type": "collapse-msg", "index": 4},
                        is_open=True
                    )
                ]), dash.no_update, dash.no_update, "Adapt Bias", op, expl



@app.callback(
    Output('data-alert', 'children', allow_duplicate=True),
    Output('data-alert', 'is_open', allow_duplicate=True),
    Output('adapting-alert', 'children', allow_duplicate=True),
    Output('adapting-alert', 'is_open', allow_duplicate=True),
    Output('table-overview', 'data', allow_duplicate=True),
    Output('table-overview', 'columns', allow_duplicate=True),
    Input("smote-btn", 'n_clicks'),
    Input("oversample-btn", 'n_clicks'),
    Input("undersample-btn", 'n_clicks'),
    State('adapting-attrs-dropdown', 'value'),
    prevent_initial_call=True
)
def handle_sampling(smote_clicks, oversample_clicks, undersample_clicks, attr):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [dash.no_update] * 6

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if not smote_clicks and not oversample_clicks and not undersample_clicks:
        return [dash.no_update] * 6
    if global_vars.df is None:
        return dash.no_update, False, "Please upload a dataset first!", True, dash.no_update, dash.no_update
    if attr is None:
        return dash.no_update, False, "Please choose a sensitive attribute!", True, dash.no_update, dash.no_update


    if button_id == "smote-btn":
        new_data = adapt_data(global_vars.df, attr, 'smote')
        global_vars.agent.add_user_action_to_history(f"I have performed SMOTE on the dataset based on the identified sensitive attribute {attr}.")
        adapting_message = "New data have been augmented."
    elif button_id == "oversample-btn":
        new_data = adapt_data(global_vars.df, attr, 'oversample')
        adapting_message = "Oversampling is completed."
        global_vars.agent.add_user_action_to_history(
            f"I have performed oversampling on the dataset based on the identified sensitive attribute {attr}.")
    elif button_id == "undersample-btn":
        new_data = adapt_data(global_vars.df, attr, 'undersample')
        adapting_message = "Undersampling is completed."
        global_vars.agent.add_user_action_to_history(
            f"I have performed undersampling on the dataset based on the identified sensitive attribute {attr}.")
    else:
        return [dash.no_update] * 6

    global_vars.df = new_data
    return (
        "The data have been updated.",
        True,
        adapting_message,
        True,
        global_vars.df.to_dict('records'),
        [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns]
    )


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
    Output({'type': 'report-graph-button', 'index': MATCH}, 'children', allow_duplicate=True),
    Input({'type': 'report-graph-button', 'index': MATCH}, 'children'),
    State({'type': 'report-graph', 'index': MATCH}, 'figure'),
    prevent_initial_call=True
)
def explain_report_figure(n_clicks, fig):
    if fig is not None:
        img_bytes = pio.to_image(fig, format='png')
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        explanation = global_vars.agent.describe_image('Describe this subgroup distribution chart.',
                                                       f"data:image/png;base64,{encoded_img}")
        explanation = format_reply_to_markdown(explanation.content)
        global_vars.agent.add_user_action_to_history("I have analyzed the result of bias surfacing and get the "
                                                     "following analysis." + explanation)
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
        answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
        answer = format_reply_to_markdown(answer)
        global_vars.agent.add_user_action_to_history("I have analyzed the result of bias measuring.")
        return dcc.Markdown(answer, className="llm-text"), {"display": "block"}, "Explain"
