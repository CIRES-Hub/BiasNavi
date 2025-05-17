import dash
from UI.app import app
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import DatasetAgent
import datetime
from dash import callback_context
import io
from dash import dcc, html, dash_table
import pandas as pd
from UI.functions import *
import dash_bootstrap_components as dbc
from flask_login import current_user
from utils.dataset_eval import DatasetEval
from dash.dash_table.Format import Format, Scheme
from UI.functions import query_llm
import time
import random
import pandas as pd
import numpy as np


@app.callback(
    [Output('table-overview', 'data', allow_duplicate=True),
     Output('table-overview', 'columns'),
     Output('column-names-dropdown', 'options',allow_duplicate=True),
     Output('error-file-format', 'is_open'),
     Output('snapshot-table', 'data'),
     Output('dataset-selection', 'options'),

     # Output('console-area', 'children', allow_duplicate=True),
     # Output("commands-input", "disabled", allow_duplicate=True),
     # Output("run-commands", "disabled", allow_duplicate=True),
     Output("upload-modal", "is_open"),
     Output("upload-data-modal", "style"),
     Output("upload-data-error-msg", "children"),
     Output('query-area', 'children', allow_duplicate=True),
     Output("pipeline-slider", "value", allow_duplicate=True),
     Output("recommended-op", "children", allow_duplicate=True),
     Output("tooltip-expl", "children", allow_duplicate=True),
     Output('label-dropdown', 'options',allow_duplicate=True),
     Output("label-modal", "is_open", allow_duplicate=True),
     Output("row-selection-modal", "is_open", allow_duplicate=True),],
    [Input('upload-data', 'contents'),
     Input('upload-data-modal', 'contents'),
     Input('confirm-row-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('upload-data-modal', 'filename'),
     State('input-start-row', 'value'),
     State('input-end-row', 'value'),
     State('snapshot-table', 'data'),
     State('query-area', 'children'),
     ],
    prevent_initial_call=True,
)
def import_data_and_update_table(list_of_contents, list_of_contents_modal, n_clicks, list_of_names, list_of_names_modal,
                                 start_row, end_row, snapshot_data, chat_content):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'upload-data' or triggered_id == 'upload-data-modal':
        if triggered_id == 'upload-data':
            if not list_of_contents or not list_of_names:
                return [], [], [], False, [], [], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update

            # Process the first file only
            contents = list_of_contents[0]
            filename = list_of_names[0]
        elif triggered_id == 'upload-data-modal':
            if not list_of_contents_modal or not list_of_names_modal:
                return [], [], [], False, [], [], dash.no_update, dash.no_update, "Error: Cannot find the dataset.", dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update

            # Process the first file only
            contents = list_of_contents_modal[0]
            filename = list_of_names_modal[0]

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if 'csv' not in filename:
            return [], [], [], False, [], [], dash.no_update, dash.no_update, "Error: Not a CSV file.", dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update,dash.no_update

        raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        global_vars.file_name = filename
        global_vars.dialog.append("DATASET: " + filename + '\n')
        global_vars.dialog.append("=" * 100 + '\n')
        curtime = datetime.datetime.now()
        formatted_date_time = curtime.strftime("%Y-%m-%d %H:%M:%S")
        global_vars.data_snapshots = [raw_data]
        # global_vars.df = DataWrangler.fill_missing_values(raw_data)
        global_vars.df = raw_data  # DataWrangler.fill_missing_values(raw_data)
        global_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
        global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name,
                                         conversation_session=global_vars.conversation_session)
        global_vars.current_stage = "Identify"
        if chat_content is None:
            chat_content = []
        chat_content.append(dcc.Markdown("The dataset has been successfully uploaded! 🎉 Let's dive into exploring it. You can "
                            "ask anything else you'd like to know about the dataset!", className="llm-msg"))
        return (
            global_vars.df.to_dict('records'),
            [{"name": col, "id": col, 'deletable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            [{'ver': '1', 'desc': 'Original', 'time': formatted_date_time}],
            ['1'],
            False,
            dash.no_update,
            "",
            chat_content,
            0,
            "Suggestion: Check Data Statistics",
            "Checking data statistics is essential in the Identify stage as it provides a foundational understanding of the dataset, helping to reveal initial disparities, patterns, or anomalies that might indicate bias.",
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            True,
            dash.no_update

        )

    elif triggered_id == 'confirm-row-button':
        if global_vars.df is None:
            return [], [], [], False, [], [], dash.no_update, dash.no_update, "No data is loaded.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        start_row = int(start_row) - 1 if start_row else 0
        end_row = int(end_row) if end_row else len(global_vars.df)

        if start_row < 0 or start_row >= end_row:
            return (
                [],
                [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                [{'label': col, 'value': col} for col in global_vars.df.columns],
                False,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                "",
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update
            )
        if end_row > len(global_vars.df):
            end_row = len(global_vars.df)

        xdf = global_vars.df.iloc[start_row:end_row]
        return (
            xdf.to_dict('records'),
            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            "",
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            False
        )

    return [], [], [], False, [], [], dash.no_update, dash.no_update, "", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('label-modal', 'is_open', allow_duplicate=True),
    Output('column-names-dropdown', 'value', allow_duplicate=True),
    Output('label-selection', 'value', allow_duplicate=True),
    Input('confirm-label-button', 'n_clicks'),
    Input('label-dropdown', 'value'),
    prevent_initial_call=True,
)
def confirm_label(n_click, label):
    global_vars.label = label
    global_vars.agent.add_user_action_to_history(
        f"The user set the target attribute of the dataset as: {label}")
    return False, label, label

@app.callback(
    Output('label-modal', 'is_open', allow_duplicate=True),
    Input('open-label-modal-button', 'n_clicks'),
    prevent_initial_call=True,
)
def open_label_modal(n_click):
    return True

@app.callback(
    Output('row-selection-modal', 'is_open', allow_duplicate=True),
    Input('show-rows-button', 'n_clicks'),
    prevent_initial_call=True,
)
def open_row_selection_modal(n_click):
    return True

@app.callback(
    Output('data-alert', 'children'),
    Output('data-alert', 'is_open'),
    Input('table-overview', 'data'),
    Input('table-overview', 'columns'),
    prevent_initial_call=True,
)
def table_updated(data, columns):
    if not data:
        return dash.no_update, dash.no_update
    new_df = pd.DataFrame(data)
    global_vars.df = new_df
    return dash.no_update,dash.no_update

@app.callback(
    Output("snapshot-modal", "is_open"),
    [Input("open-modal-button", "n_clicks"),
     Input("close-snapshot-modal", "n_clicks"),
     Input("save-snapshot-button", "n_clicks")],
    [State("snapshot-modal", "is_open")]
)
def toggle_snapshot_modal(open_click, close_click, save_click, is_open):
    if open_click or close_click or save_click:
        return not is_open
    return is_open


@app.callback(
    Output('snapshot-table', 'data', allow_duplicate=True),
    Output('dataset-selection', 'options', allow_duplicate=True),
    [Input("save-snapshot-button", "n_clicks")],
    [State("snapshot-name-input", "value"),
     State('table-overview', 'data'),
     State('snapshot-table', 'data'),
     State('dataset-selection', 'options')],
    prevent_initial_call=True,
)
def save_data_snapshot(n_clicks, new_name, rows, snapshots, dataset_version):
    if n_clicks > 0 and new_name:
        df = pd.DataFrame(rows)
        global_vars.data_snapshots.append(df)
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        snapshots.append(
            {'ver': f'{len(snapshots) + 1}', 'desc': new_name, 'time': formatted_date_time})
        dataset_version.append(f'{len(snapshots)}')
        return snapshots, dataset_version
    return dash.no_update, dash.no_update


@app.callback(
    Output('snapshot-table', 'data', allow_duplicate=True),
    Output('dataset-selection', 'options', allow_duplicate=True),
    Input('delete-snapshot-button', 'n_clicks'),
    State('snapshot-table', 'selected_rows'),
    State('snapshot-table', 'data'),
    prevent_initial_call=True,
)
def delete_snapshot(n_clicks, selected_rows, snapshots):
    if n_clicks > 0 and selected_rows:
        # Find the index of the selected row and delete it from the data
        row_to_delete = selected_rows[0]
        del snapshots[row_to_delete]
        del global_vars.data_snapshots[row_to_delete]
        snapshots = [{'ver': f'{i + 1}', 'desc': item['desc'], 'time': item['time']} for i, item in
                     enumerate(snapshots)]
        return snapshots, [f'{i + 1}' for i in range(len(snapshots))]
    return dash.no_update, dash.no_update


@app.callback(
    Output('table-overview', 'columns', allow_duplicate=True, ),
    Output('table-overview', 'data', allow_duplicate=True, ),
    Output('data-alert', 'children', allow_duplicate=True),
    Output('data-alert', 'is_open', allow_duplicate=True),
    Input('restore-snapshot-button', 'n_clicks'),
    State('snapshot-table', 'selected_rows'),
    prevent_initial_call=True,
)
def restore_data_snapshot(n_clicks, selected_rows):
    if n_clicks > 0 and selected_rows:
        row_id = selected_rows[0]
        chosen_snapshot = global_vars.data_snapshots[row_id]
        global_vars.df = chosen_snapshot
        return [{"name": i, "id": i, 'deletable': True, 'renamable': True} for i in
                chosen_snapshot.columns], chosen_snapshot.to_dict('records'), f"The data snapshot with ID {row_id+1} has been restored", True
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output('download-data-csv', 'data'),
    [Input('download-data-button', 'n_clicks')],
    [State('table-overview', 'data')]
)
def download_csv(n_clicks, rows):
    if n_clicks > 0:
        # Convert the data to a DataFrame and generate the CSV file
        df = pd.DataFrame(rows)
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return dcc.send_data_frame(df.to_csv, f'{formatted_date_time}_edited_{global_vars.file_name}')
    return None


@app.callback(
    Output('datatable-interactivity-container', 'children'),
    Input('table-overview', 'active_cell')
)
def update_histogram(active_cell):
    if active_cell is None:
        return []

    column_id = active_cell['column_id']
    col_data = global_vars.df[column_id]
    unique_values = col_data.nunique()



    # Base color palette
    colorscale = [
        "#a6bddb", "#d0d1e6", "#bdbdbd", "#fdd0a2",
        "#c7e9c0", "#f2b6b6", "#d9d9d9", "#c6dbef"
    ]

    fig = None


    # Case 2: numeric column (e.g. age)
    if np.issubdtype(col_data.dtype, np.number):
        if unique_values <= 20:
            col_for_plot = f"{column_id}_str"
            global_vars.df[col_for_plot] = col_data.astype(str)
            unique_categories = sorted(global_vars.df[col_for_plot].dropna().unique())
            extended_colors = (colorscale * ((len(unique_categories) // len(colorscale)) + 1))[:len(unique_categories)]
            color_map = {category: color for category, color in zip(unique_categories, extended_colors)}

            fig = px.histogram(global_vars.df, x=col_for_plot, color=col_for_plot,
                               category_orders={col_for_plot: unique_categories},
                               color_discrete_map=color_map)
        else:
            # Manual binning and use bin label as both x and color
            bins = [0, 20, 30, 40, 50, 60, 70, 80]
            labels = ['<20', '20s', '30s', '40s', '50s', '60s', '70+']
            bin_col = f"{column_id}_bin"
            global_vars.df[bin_col] = pd.cut(col_data, bins=bins, labels=labels)

            unique_categories = labels
            extended_colors = (colorscale * ((len(labels) // len(colorscale)) + 1))[:len(labels)]
            color_map = {label: color for label, color in zip(labels, extended_colors)}

            fig = px.histogram(global_vars.df, x=bin_col, color=bin_col,
                               category_orders={bin_col: labels},
                               color_discrete_map=color_map)

    # Case 3: categorical column
    else:
        if unique_values > 100:
            return []
        col_for_plot = column_id
        unique_categories = sorted(col_data.dropna().unique())
        extended_colors = (colorscale * ((len(unique_categories) // len(colorscale)) + 1))[:len(unique_categories)]
        color_map = {category: color for category, color in zip(unique_categories, extended_colors)}

        fig = px.histogram(global_vars.df, x=column_id, color=column_id,
                           category_orders={column_id: unique_categories},
                           color_discrete_map=color_map)

    fig.update_layout(
        xaxis={"automargin": True, "tickmode": "auto"},
        yaxis={"automargin": True},
        height=250,
        margin={"t": 10, "l": 10, "r": 10},
        bargap=0.2,
        showlegend=False
    )

    return dcc.Graph(id=column_id, figure=fig)




@app.callback(
    [Output('label-selection', 'options'),
     Output('sensi-attr-selection', 'options')],
    [Input('dataset-selection', 'value')],
    prevent_initial_call=True
)
def update_columns(df_id):
    if df_id is None:
        return [], []

    # Get the columns of the selected DataFrame
    columns = [{'label': col, 'value': col} for col in global_vars.data_snapshots[int(df_id) - 1].columns]

    return columns, columns


@app.callback(
    Output('model-selection', 'options'),
    Input('task-selection', 'value'),
    prevent_initial_call=True
)
def update_model_dropdown(selected_task):
    if selected_task == 'Classification':
        return [{'label': 'SVM', 'value': 'SVM'}, {'label': 'Logistic', 'value': 'Logistic'},
                {'label': 'MLP', 'value': 'MLP'}]
    if selected_task == 'Regression':
        return [{'label': 'SVM', 'value': 'SVM'}, {'label': 'MLP', 'value': 'MLP'}]


@app.callback(
    Output('eval-info', 'children'),
    Output('eval-info', 'is_open'),
    Output('eval-res', 'children'),
    Output('fairness-scores', 'children'),
    Output('eval-explanation', 'children'),
    Output({'type': 'spinner-btn', 'index': 0}, 'children', allow_duplicate=True),
    Output("experiment-result-table", 'data', allow_duplicate=True),
    Output("experiment-result", 'data', allow_duplicate=True),
    Output("recommended-op", "children", allow_duplicate=True),
    Output("tooltip-expl", "children", allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 0}, 'children'),
    State('dataset-selection', 'value'),
    State('sensi-attr-selection', 'value'),
    State('label-selection', 'value'),
    State('task-selection', 'value'),
    State('model-selection', 'value'),
    State("experiment-result-table", 'data'),
    State("experiment-result", 'data'),
    prevent_initial_call=True
)
def evaluate_dataset(_, df_id, sens_attr, label, task, model, past_res_table, past_res):
    if global_vars.df is None or not global_vars.data_snapshots:
        return 'No dataset is loaded!', True, [], [], [], " Run", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if df_id is None or sens_attr is None or label is None or task is None or model is None:
        return 'The experimental setting is incomplete!', True, [], [], [], " Run", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    data = global_vars.data_snapshots[int(df_id) - 1]
    if label in sens_attr:
        return 'The label cannot be in the sensitive attributes!', True, [], [], [], " Run", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if data[label].dtype in ['float64', 'float32'] and task == 'Classification':
        return ('The target attribute is continuous (float) but the task is set to classification. Consider binning '
                'the target or setting the task to regression.'), True, [], [], [], " Run", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if data[label].dtype == 'object' or data[label].dtype.name == 'bool' or data[label].dtype.name == 'category':
        if task == 'Regression':
            return 'The target attribute is categorical and cannot be used for regression task.', True, [], [], [], " Run", dash.no_update, dash.no_update
    de = DatasetEval(data, label, ratio=0.2, task_type=task, sensitive_attribute=sens_attr, model_type=model)
    res, scores = de.train_and_test()
    tables = []
    for tid, frame in enumerate(scores):
        tables.append(dash_table.DataTable(
            id=f'table-{tid + 1}',
            columns=[
                {
                    'name': col, 'id': col, 'type': 'numeric',
                    'format': Format(precision=0, scheme=Scheme.fixed) if frame[col].dtype in ['int64',
                                                                                               'O'] else Format(
                        precision=4, scheme=Scheme.fixed)
                }
                for col in frame.columns
            ],
            data=frame.to_dict('records'),
            style_cell={'textAlign': 'center',
                        'fontFamily': 'Arial'},
            # style_header={'backgroundColor': '#614385',
            #               'color': 'white',
            #               'fontWeight': 'bold'
            #               },
            style_table={'overflowX': 'auto', 'marginTop': '20px', 'marginLeft': '0px'},  # Add margin here
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f2f2f2'
                },
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': 'white'
                },
                # Highlight the last row
                {
                    'if': {'row_index': len(frame) - 1},
                    'backgroundColor': '#ffeb3b',  # Yellow background color for highlighting
                    'fontWeight': 'bold'
                },
            ]
        ))
    if task == 'Classification':
        tooltip = html.Div([
            html.Div([
                html.H5("Results", style={'paddingLeft': 0}),
                html.Span(
                    html.I(className="fas fa-question-circle"),
                    id="tooltip-eval",
                    style={
                        "fontSize": "20px",
                        "color": "#aaa",
                        "cursor": "pointer",
                        "marginLeft": "5px",
                        "alignSelf": "center"
                    }
                )
            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "width": "100%"}),
            dbc.Tooltip(
                "The figures in the table represent the average predicted probability that the subgroup is classified "
                "into the corresponding category. The disparity score is calculated as the difference between "
                "the maximum and minimum values in each column. A larger score indicates a higher degree of potential bias.",
                target="tooltip-eval",
            ),
        ])
    else:
        tooltip = html.Div([
            html.Div([
                html.H5("Results", style={'paddingLeft': 0}),
                html.Span(
                    html.I(className="fas fa-question-circle"),
                    id="tooltip-eval",
                    style={
                        "fontSize": "20px",
                        "color": "#aaa",
                        "cursor": "pointer",
                        "marginLeft": "5px",
                        "alignSelf": "center"
                    }
                )
            ], style={"display": "flex", "alignItems": "center", "justifyContent": "spaceBetween", "width": "100%"}),
            dbc.Tooltip(
                "The figures in the table represent the predicted mean absolute error for each subgroup in the regression task. "
                "The disparity score is calculated as the difference between "
                "the maximum and minimum values in the column. A larger score indicates a higher degree of potential bias.",
                target="tooltip-eval",
            ),
        ])
    data_string = "\n".join(
        [f"Row {i + 1}: {row}" for i, row in enumerate(tables)]
    )
    query = f"Assess the bias level in the dataset using the following results: {data_string}. The model accuracy is {res}. These results were generated by executing the {task} task with the {model} model. The analysis centers on the sensitive attributes {sens_attr}, with {label} serving as the target attribute. The objective is to identify and minimize disparities among subgroups of the sensitive attributes without sacrificing accuracy."
    answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
    answer = format_reply_to_markdown(answer)
    res_explanation = [dcc.Markdown(answer, className="llm-text")]
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    str_sens_attr = ' '.join(sens_attr)
    settings = f"sensitive attributes: {str_sens_attr}, label:{label}, model:{model}, task:{task}"
    past_res_table.append({"Snapshot": df_id, "Timestamp": formatted_date_time, "Result": res,
                           "Setting": settings})
    past_res.append(tables)
    global_vars.agent.add_user_action_to_history(f"I have evaluated the dataset and got the result and disparity scores: {data_string}")
    return "", False, [html.Hr(), tooltip, res], tables, res_explanation, " Run", past_res_table, past_res, op, expl


@app.callback(
    Output("experiment-result-table", 'data', allow_duplicate=True),
    Output("experiment-result", 'data', allow_duplicate=True),
    Input("remove-all-result-btn", 'n_clicks'),
    prevent_initial_call=True
)
def remove_all_result(n_clicks):
    if n_clicks:
        return [],{}
    return dash.no_update, dash.no_update

@app.callback(
    Output('chosen-experiment-res', 'children'),
    Input('experiment-result-table', 'active_cell'),
    State("experiment-result","data"),
    prevent_initial_call=True
)
def show_past_experiment_result(active_cell, data):
    if active_cell is None:
        return []  # Return an empty figure if no cell is selected

    # Get the row id from the active cell
    row = active_cell['row']

    return data[row]

@app.callback(
    Output('comparison-res', 'children', allow_duplicate=True),
    Output('comparison-alert', 'children', allow_duplicate=True),
    Output('comparison-alert', 'is_open', allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 10}, 'children', allow_duplicate=True),
    Output("recommended-op", "children", allow_duplicate=True),
    Output("tooltip-expl", "children", allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 10}, 'children'),
    State('experiment-result-table', 'selected_rows'),
    State('experiment-result-table', 'data'),
    State("experiment-result","data"),
    prevent_initial_call=True

)
def compare_experiment_results(_, selected_rows, table_data, res_data):
    if selected_rows is None:
        return [], "Choose two experiment results to compare.", True, "Compare", dash.no_update, dash.no_update
    if len(selected_rows)!=2:
        return [], "You can only choose two experiment results to compare.", True, "Compare", dash.no_update, dash.no_update
    # Get the row id from the active cell
    acc1 = table_data[selected_rows[0]]["Result"]
    acc2 = table_data[selected_rows[1]]["Result"]
    res1 = res_data[selected_rows[0]]
    res2 = res_data[selected_rows[1]]

    res_string1 = "\n".join(
        [f"Row {i + 1}: {row}" for i, row in enumerate(res1)]
    )
    res_string2 = "\n".join(
        [f"Row {i + 1}: {row}" for i, row in enumerate(res2)]
    )
    query = f"Please compare the results of two comparison. The first chosen result has the overall {acc1} and the accuracy across different subgroups and categories is {res_string1}. The second chosen result has the overall {acc2} and the accuracy across different subgroups and categories is {res_string2}. You should consider both the accuracy and disparity score to demonstrate which result is better."
    answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
    answer = format_reply_to_markdown(answer)
    res_comparison = [dcc.Markdown(answer, className="llm-text")]
    return res_comparison, dash.no_update, dash.no_update, "compare", op, expl


@app.callback(
    Output("data-stat-modal", "is_open"),
    Output("data-stat-body", "children"),
    Input("data-stat-button", "n_clicks"),
    Input("data-stat-close", "n_clicks"),
    State("data-stat-modal", "is_open"),
    prevent_initial_call=True
)
def display_data_stat(n1, n2, is_open):
    if global_vars.df is not None:
        # Summarize the DataFrame and include column names as the first column
        summary = summarize_dataframe(global_vars.df)
        summary.reset_index(inplace=True)  # Turn column names into a column
        summary.rename(columns={"index": "Column Name"}, inplace=True)

        # Ensure serializable
        summary = summary.fillna("").astype(str)
        total_missing = global_vars.df.isnull().sum().sum()
        total_values = global_vars.df.size
        missing_rate = (total_missing / total_values) * 100
        desc = f"This dataset: {global_vars.file_name}, comprises {global_vars.df.shape[0]} rows and {global_vars.df.shape[1]} columns. with an overall missing rate {missing_rate:.2f}%. "
        # Define the DataTable
        table = dash_table.DataTable(
            columns=[
                {"name": col, "id": col} for col in summary.columns
            ],
            data=summary.to_dict("records"),  # Ensure serializable
            style_cell={"textAlign": "center", "fontFamily": "Arial"},
            # style_header={"backgroundColor": "#614385", "color": "white", "fontWeight": "bold"},
            style_table={"overflowX": "auto", "marginTop": "20px", "marginLeft": "0px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f2f2f2"},
                {"if": {"row_index": "even"}, "backgroundColor": "white"},
            ]
        )

        # Toggle modal and return table
        if n1 or n2:
            return not is_open, [desc,table]

    return is_open, []

@app.callback(
    Output("data-stat-summary", "children"),
    Output({'type': 'spinner-btn', 'index': 1}, "children",allow_duplicate=True),
    Output("recommended-op", "children", allow_duplicate=True),
    Output("tooltip-expl", "children", allow_duplicate=True),
    Input({'type': 'spinner-btn', 'index': 1}, "children"),
    State("data-stat-body", "children"),
    prevent_initial_call=True
)
def display_data_summary(_, data):
    if global_vars.df is not None:
        # Summarize the DataFrame and include column names as the first column
        data_string = "\n".join(
            [f"Row {i + 1}: {row}" for i, row in enumerate(data)]
        )
        query = f"""
                The dataset is with the following summary statistics {data_string}. Please First provide a summary of this 
                dataset and then: 
                1. Identify any notable trends, patterns, or insights based on the provided 
                statistics. 
                2. Highlight potential issues, such as missing values, outliers, or unusual 
                distributions.                 
                3. Identify any signs of bias in the dataset, such as imbalances in distributions across key features.              
                4. Suggest strategies to mitigate bias, such as rebalancing, feature engineering, or fairness-aware 
                approaches. 
                """

        answer, media, suggestions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id)
        answer = format_reply_to_markdown(answer)
        global_vars.agent.add_user_action_to_history(f"I have analyzed the dataset. ")
        return [dcc.Markdown(answer, className="llm-text")], "Analyze", op, expl

    return [], "Analyze", dash.no_update, dash.no_update


def summarize_dataframe(df):
    """
    Summarizes a pandas DataFrame by providing:
    - Column names and data types
    - Number of missing values
    - Number of unique values
    - Basic descriptive statistics for numerical and categorical columns
    """
    # Create a summary DataFrame with basic information
    summary = pd.DataFrame({
        "Data Type": df.dtypes.astype(str),  # Data types of each column
        "Missing Values": df.isnull().sum(),  # Count of missing values in each column
        "Unique Values": df.nunique(),  # Number of unique values in each column
    })

    # Add statistics for numerical columns
    numerical_summary = df.describe().T  # Transpose the descriptive statistics for readability
    numerical_summary = numerical_summary[["mean", "std", "min", "25%", "50%", "75%", "max"]]
    summary = summary.join(numerical_summary, how="left")  # Join numerical stats to the summary

    # Handle categorical columns separately
    categorical_columns = df.select_dtypes(include=["object", "category"])  # Select only categorical columns

    # Calculate the most frequent value (mode) for each categorical column
    top_values = categorical_columns.apply(
        lambda col: col.mode().iloc[0] if not col.mode().empty else None  # Handle empty mode
    )

    # Calculate the frequency of the most frequent value
    top_frequencies = categorical_columns.apply(
        lambda col: col.value_counts().iloc[0] if not col.value_counts().empty else None  # Handle empty value_counts
    )

    # Create a summary DataFrame for categorical columns
    categorical_summary = pd.DataFrame({
        "Top Value": top_values,  # Most frequent value for each column
        "Top Frequency": top_frequencies,  # Frequency of the most frequent value
    })

    # Merge the categorical summary with the overall summary
    summary = summary.join(categorical_summary, how="left")

    return summary

