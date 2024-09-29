import dash
from UI.app import app
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import  DatasetAgent
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


@app.callback(
    [Output('table-overview', 'data', allow_duplicate=True),
     Output('table-overview', 'columns'),
     Output('column-names-dropdown', 'options'),
     Output('error-file-format', 'is_open'),
     Output('dataset-name', 'children'),
     Output('snapshot-table', 'data'),
     Output('dataset-selection', 'options'),
     Output('console-area', 'children', allow_duplicate=True),
     Output("commands-input", "disabled", allow_duplicate=True),
     Output("run-commands", "disabled", allow_duplicate=True), ],
    [Input('upload-data', 'contents'),
     Input('show-rows-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('input-start-row', 'value'),
     State('input-end-row', 'value'),
     State('snapshot-table', 'data'), ],
    prevent_initial_call=True,
)
def import_data_and_update_table(list_of_contents, n_clicks, list_of_names, start_row, end_row, snapshot_data):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'upload-data':
        if not list_of_contents or not list_of_names:
            return [], [], [], False, "", [], dash.no_update, dash.no_update, dash.no_update

            # Process the first file only
        contents = list_of_contents[0]
        filename = list_of_names[0]

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if 'csv' not in filename:
            return [], [], [], False, "", [], [], dash.no_update, dash.no_update, dash.no_update

        raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        global_vars.file_name = filename
        global_vars.dialog.append("DATASET: " + filename + '\n')
        global_vars.dialog.append("=" * 100 + '\n')
        curtime = datetime.datetime.now()
        formatted_date_time = curtime.strftime("%Y-%m-%d %H:%M:%S")
        global_vars.data_snapshots = [raw_data]
        # global_vars.df = DataWrangler.fill_missing_values(raw_data)
        global_vars.df = raw_data  # DataWrangler.fill_missing_values(raw_data)
        global_vars.agent = DatasetAgent(global_vars.df, file_name=filename)
        if all([current_user.professional_role, current_user.industry_sector, current_user.expertise_level,
                current_user.technical_level, current_user.bias_awareness]):
            persona_query = current_user.persona_prompt.replace("{{professional_role}}", current_user.professional_role)
            persona_query = persona_query.replace("{{industry_sector}}", current_user.industry_sector)
            persona_query = persona_query.replace("{{expertise_level}}", current_user.expertise_level)
            persona_query = persona_query.replace("{{technical_level}}", current_user.technical_level)
            persona_query = persona_query.replace("{{bias_awareness}}", current_user.bias_awareness)

            query_llm(persona_query, current_user.id)

        return (
            global_vars.df.to_dict('records'),
            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            f"Dataset: {filename} (maximum row number:{len(global_vars.df)})",
            [{'ver': '1', 'desc': 'Original', 'time': formatted_date_time}],
            ['1'],
            "",
            False,
            False
        )

    elif triggered_id == 'show-rows-button':
        if global_vars.df is None:
            return [], [], [], False, "", [], [], dash.no_update, dash.no_update, dash.no_update

        start_row = int(start_row) - 1 if start_row else 0
        end_row = int(end_row) if end_row else len(global_vars.df)

        if start_row < 0 or end_row > len(global_vars.df) or start_row >= end_row:
            return (
                [],
                [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                [{'label': col, 'value': col} for col in global_vars.df.columns],
                False,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update
            )

        xdf = global_vars.df.iloc[start_row:end_row]
        return (
            xdf.to_dict('records'),
            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            "",
            False,
            False
        )

    return [], [], [], False, "", [], [], "", dash.no_update, dash.no_update


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
                chosen_snapshot.columns], chosen_snapshot.to_dict('records')
    return dash.no_update, dash.no_update



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
        return []  # Return an empty figure if no cell is selected

    # Get the column id from the active cell
    column_id = active_cell['column_id']

    # Create a histogram for the selected column
    fig = px.histogram(global_vars.df, x=column_id)

    # Update the layout properly
    fig.update_layout(
        xaxis={"automargin": True, "tickmode": "auto", },
        yaxis={"automargin": True},
        height=250,
        margin={"t": 10, "l": 10, "r": 10},
        bargap=0.2,
    )

    # Return the Graph component
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
    Output('eval-res', 'children'),
    Output('fairness-scores', 'children'),
    Input('eval-button','n_clicks'),
    State('dataset-selection', 'value'),
    State('sensi-attr-selection', 'value'),
    State('label-selection', 'value'),
    State('task-selection', 'value'),
    State('model-selection', 'value'),
    prevent_initial_call=True
)
def evaluate_dataset(n_clicks, df_id, sens_attr, label, task, model):
    data = global_vars.data_snapshots[int(df_id) - 1]
    if label in sens_attr:
        return html.P('The label cannot be in the sensitive attributes!', style={"color": "red"}), [], [],
    if data[label].dtype in ['float64', 'float32'] and task == 'Classification':
        return html.P('The target attribute is continuous (float) but the task is set to classification. '
                      'Consider binning the target or setting the task to regression.',style={"color": "red"}), [], [], []
    if data[label].dtype == 'object' or data[label].dtype.name == 'bool' or data[label].dtype.name == 'category':
        if task == 'Regression':
            return html.P('The target attribute is categorical and cannot be used for regression task.',style={"color": "red"}), [], [], []
    de = DatasetEval(data,label,ratio=0.2,task_type=task,sensitive_attribute=sens_attr,model_type=model)
    res, scores = de.train_and_test()
    tables = []
    for tid,frame in enumerate(scores):
        tables.append(dash_table.DataTable(
            id=f'table-{tid + 1}',
            columns=[
                {
                    'name': col, 'id': col, 'type': 'numeric',
                    'format': Format(precision=0, scheme=Scheme.fixed) if frame[col].dtype in ['int64','O'] else Format(precision=4, scheme=Scheme.fixed)
                }
                for col in frame.columns
            ],
            data=frame.to_dict('records'),
            style_cell={'textAlign': 'center',
                        'fontFamily': 'Arial'},
            style_header={'backgroundColor': 'darkslateblue',
                          'color': 'white',
                          'fontWeight': 'bold'
                          },
            style_table={'overflowX': 'auto', 'marginTop': '20px', 'marginLeft':'0px'},  # Add margin here
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
                    ], style={"display": "flex", "alignItems": "center","justifyContent": "space-between","width": "100%"}),
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
    return [], [html.Hr(), tooltip, res], tables
