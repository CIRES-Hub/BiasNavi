import time
import dash
import docker.errors
from UI.app import app
from db_models.users import User
from db_models.databases import db
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import ConversationFormat, DatasetAgent
import datetime
from dash import callback_context, MATCH, ALL, ctx
import io
from RAG import RAG
from dash import dcc, html, dash_table
import pandas as pd
from UI.variable import global_vars
from flask_login import current_user
from UI.functions import *
from utils.data_wrangler import DataWrangler
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash.exceptions import PreventUpdate
import docker
import ast
import os
import os
import shutil


@app.callback(
    Output("export", "data"),
    Output("error-export", "is_open"),
    Input("download-button", "n_clicks"),
    Input("export-format-dropdown", "value"),
    prevent_initial_call=True,
)
def export_conversation(n_clicks, format):
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if (triggered_id != 'download-button'):
        return None, False
    # return dict(content="".join(global_vars.dialog), filename=f"query-history-{formatted_date_time}.txt")
    if (global_vars.agent is None):
        return None, True
    history, extension = global_vars.agent.get_history(
        c_format=ConversationFormat(format))
    return dict(content=history, filename=f"query-history-{formatted_date_time}" + extension), False


@app.callback(
    Output('rag-switch-output', 'children'),
    Output('rag-card', 'style'),
    Output('RAG-button', 'style'),
    Input('rag-switch', 'value')
)
def rag_switch(value):
    if value:
        global_vars.use_rag = True
        return 'RAG: On', {'display': 'block'}, {'display': 'block'}
    else:
        global_vars.use_rag = False
        return 'RAG: OFF', {'display': 'none'}, {'display': 'none'}


@app.callback(
    Output('RAG-area', 'children'),
    Input('upload-rag', 'contents'),
    State('upload-rag', 'filename'),
    Input('RAG-button', 'n_clicks'),
    Input('send-button', 'n_clicks'),
    [State('RAG-area', 'children')],
    State('query-input', 'value'),
    prevent_initial_call=True
)
def upload_rag_area(list_of_contents, list_of_names, clicks_rag, clicks_send, rag_output, query):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'upload-rag':
        if list_of_contents is not None:
            filename = ''
            output = 'RAG files: '
            # Assuming that only the first file is processed
            contents = list_of_contents[0]
            filename = list_of_names[0]

            # Decode the contents of the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                # Assume the file is plain text
                if 'pdf' in filename:
                    # Assume that the user uploaded a CSV
                    output += filename + '\n'
                    if global_vars.rag:
                        global_vars.rag.clean()

                    global_vars.rag = RAG(io.BytesIO(decoded))

                    return [html.Div([
                        # placeholder
                        output
                    ])]
                else:
                    return html.Div([
                        "This file format is not supported. Only PDF files are supported."
                    ])

            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])

    elif triggered_id == 'send-button':
        if not global_vars.rag or not global_vars.use_rag:
            return rag_output
        if not rag_output:
            return html.Div([""])
        if global_vars.rag and global_vars.use_rag:
            global_vars.rag_prompt = global_vars.rag.invoke(query)
        rag_output.append(html.Div(["RAG enhanced prompt: " + global_vars.rag_prompt]))
        global_vars.rag_prompt = None
        return rag_output

    else:
        return rag_output


@app.callback(
    [Output('table-overview', 'data', allow_duplicate=True, ),
     Output('table-overview', 'columns'),
     Output('column-names-dropdown', 'options'),
     Output('error-file-format', 'is_open'),
     Output('dataset-name', 'children'),
     Output('snapshot-table', 'data'),
     Output('dataset-selection', 'options')],
    [Input('upload-data', 'contents'),
     Input('show-rows-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('input-start-row', 'value'),
     State('input-end-row', 'value'),
     State('snapshot-table', 'data')],
    prevent_initial_call=True,
)
def import_data_and_update_table(list_of_contents, n_clicks, list_of_names, start_row, end_row, snapshot_data):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'upload-data':
        if not list_of_contents or not list_of_names:
            return [], [], [], False, "", []

        # Process the first file only
        contents = list_of_contents[0]
        filename = list_of_names[0]

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if 'csv' not in filename:
            return [], [], [], False, "", [], []

        raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        global_vars.file_name = filename
        global_vars.dialog.append("DATASET: " + filename + '\n')
        global_vars.dialog.append("=" * 100 + '\n')
        curtime = datetime.datetime.now()
        formatted_date_time = curtime.strftime("%Y-%m-%d %H:%M:%S")
        global_vars.data_snapshots.append(raw_data)
        #global_vars.df = DataWrangler.fill_missing_values(raw_data)
        global_vars.df = raw_data  #DataWrangler.fill_missing_values(raw_data)
        global_vars.agent = DatasetAgent(global_vars.df, file_name=filename)
        if all([current_user.professional_role, current_user.industry_sector, current_user.expertise_level]):
            query_llm('. \n '.join(
                [f'my professional role is {current_user.professional_role}' if current_user.professional_role else '',
                 f'I am working in {current_user.industry_sector} industry' if current_user.industry_sector else '',
                 f'my level of expertise in data analysis is {current_user.expertise_level}' if current_user.expertise_level else ''
                 ]))

        return (
            global_vars.df.to_dict('records'),
            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            f"Dataset: {filename} (maximum row number:{len(global_vars.df)})",
            [{'ver': '1', 'desc': 'Original', 'time': formatted_date_time}],
            ['1']
        )

    elif triggered_id == 'show-rows-button':
        if global_vars.df is None:
            return [], [], [], False, "", [], []

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
        )

    return [], [], [], False, "", [], []


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


# @app.callback(
#     Output('bar-chart', 'figure'),
#     Output('pie-chart', 'figure'),
#     Input('column-names-dropdown', 'value'),
#     prevent_initial_call=True
# )
# def update_graph(selected_column):
#     value_counts = global_vars.df[selected_column].value_counts()
#     bar = px.bar(
#         x=value_counts.index,
#         y=value_counts.values,
#         labels={'x': selected_column, 'y': 'Count'},
#         title=f'Bar Chart - Distribution of {selected_column}'
#     )
#
#     value_counts = global_vars.df[selected_column].value_counts().reset_index()
#     value_counts.columns = [selected_column, 'count']
#
#     pie = px.pie(
#         value_counts,
#         names=selected_column,
#         values='count',
#         title=f'Pie Chart - Distribution of {selected_column}'
#     )
#     return bar, pie


# Update the llm chatbox
@app.callback(
    [Output("query-area", "children"),
     Output("error-query", "is_open"),
     Output('llm-media-area', 'children'),
     Output("chat-update-trigger", "data"),
     Output("next-suggested-questions", "children"),
     Output("commands-input", "value"),
     Output('query-input', 'value')],
    [Input('send-button', 'n_clicks'),
     Input('query-input', 'n_submit'),
     Input({"type": 'next-suggested-question', "index": ALL}, 'n_clicks')],
    [State('query-input', 'value'),
     State('query-area', 'children'),
     State('next-suggested-questions', 'children')],
    prevent_initial_input=True,
    prevent_initial_call=True
)
def update_messages(n_clicks, n_submit, input_3, input_text, query_records, suggested_questions):
    if ((n_clicks is None or input_text is None) and input_3 is None) or global_vars.df is None:
        return query_records, True, None, dash.no_update, suggested_questions, "", ""
    trigger = ctx.triggered_id
    query = ''
    if not isinstance(trigger, str) and 'next-suggested-question' in trigger.type:
        query = global_vars.suggested_questions[int(trigger.index[-1])]
    else:
        query = input_text
    new_user_message = html.Div(query + '\n', className="user-msg")
    global_vars.dialog.append("\nUSER: " + query + '\n')
    suggested_questions = []
    if not query_records:
        query_records = []
    if global_vars.rag and global_vars.use_rag:
        input_text = global_vars.rag.invoke(query)
        global_vars.rag_prompt = query
    output_text, media, new_suggested_questions = query_llm(query)

    if new_suggested_questions is not None:
        for i in range(len(new_suggested_questions)):
            if new_suggested_questions[i]:
                new_suggested_question = html.Div(dbc.CardBody([
                    html.P("Suggested Next Question", style={'font-weight': 'bold', "margin-bottom": "0px"}),
                    html.P(new_suggested_questions[i], style={"margin-bottom": "0px"})],
                    style={"padding": 0}), className="next-suggested-question",
                    id={"type": "next-suggested-question", "index": f'next-question-{i}'}, n_clicks=0)
                suggested_questions.append(new_suggested_question)

    response = 'Assistant: ' + output_text + '\n'
    global_vars.dialog.append("\n" + response)
    # Simulate a response from the system
    new_response_message = dcc.Markdown(response, className="llm-msg")
    query_records.append(new_user_message)
    query_records.append(new_response_message)
    list_commands = global_vars.agent.list_commands
    return query_records, False, media, time.time(), suggested_questions, ('\n').join(list_commands) if len(
        list_commands) > 0 else "", ""


@app.callback(
    Output({'type': 'llm-media-modal', 'index': MATCH}, 'is_open'),
    Input({'type': 'llm-media-figure', 'index': MATCH}, 'n_clicks'),
    State({'type': 'llm-media-figure', 'index': MATCH}, 'id'),
)
def show_figure_modal(n_clicks, id):
    if (n_clicks is not None and n_clicks > 0):
        return True
    else:
        return False


def query_llm(query):
    print(query)
    response, media, suggestions = global_vars.agent.run(query)
    global_vars.agent.persist_history(user_id=str(current_user.id))
    global_vars.suggested_questions = suggestions
    return response, media, suggestions


# @app.callback(
#     Output('query-output', 'children'),
#     [Input('send-query', 'n_clicks')],
#     [State('query-input', 'value'), State('stored-data', 'children')]
# )
# def update_output(n_clicks, query, stored_data):
#     # Process query and update output here
#     # ...
#     pass


# Update Username
@app.callback(
    Output("edit-username-modal", "is_open"),
    Output("new-username-input", "value"),
    Input("edit-username-icon", "n_clicks"),
    Input("cancel-username-edit", "n_clicks"),
    Input("save-username-button", "n_clicks"),
    State("edit-username-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_username_modal(edit_clicks, cancel_clicks, save_clicks, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "edit-username-icon":
            return True, current_user.username or ""
        elif button_id in ["cancel-username-edit", "save-username-button"]:
            return False, ""
    return is_open, ""


@app.callback(
    Output("username-edit-success", "data"),
    Input("save-username-button", "n_clicks"),
    State("new-username-input", "value"),
    prevent_initial_call=True
)
def save_new_username(n_clicks, new_username):
    if n_clicks > 0 and new_username:
        user = User.query.get(current_user.id)
        user.username = new_username
        db.session.commit()
        return True
    return False


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


@app.callback(
    [Output("console-area", "children"),
     Output("commands-input", "disabled", allow_duplicate=True),
     Output("run-commands", "disabled", allow_duplicate=True)],
    Input("run-commands", "n_clicks"),
    State("commands-input", "value"),
    prevent_initial_call=True
)
def execute_commands(n_click, commands):
    if global_vars.df is None and n_click > 0:
        return ["Have you imported a dataset and entered a query?", False, False]
    if n_click > 0 and commands is not None:
        try:
            print("Running sandbox...")
            user_id = str(current_user.id)
            current_path = os.path.dirname(os.path.realpath(__file__))
            parent_path = os.path.dirname(current_path)
            user_data_dir = os.path.join(os.path.dirname(parent_path), 'tmp', user_id)

            if not os.path.exists(user_data_dir):
                print("Creating user's directory...")
                os.makedirs(user_data_dir, exist_ok=True)
                shutil.copyfile(os.path.join(parent_path, 'assets', 'sandbox_main.py'),
                                os.path.join(user_data_dir, 'sandbox_main.py'))
                print("Create user's directory successfully")
            else:
                if not os.path.exists(os.path.join(user_data_dir, 'sandbox_main.py')):
                    shutil.copyfile(os.path.join(parent_path, 'assets', 'sandbox_main.py'),
                                    os.path.join(user_data_dir, 'sandbox_main.py'))

            user_output_file = os.path.join(user_data_dir, f"_output_{user_id}.out")
            user_error_file = os.path.join(user_data_dir, f"_error_{user_id}.err")
            container_name = 'biasnavi-' + user_id

            with open(os.path.join(user_data_dir, 'sandbox_commands.py'), "w") as f:
                f.write(commands)

            global_vars.df.to_csv(os.path.join(user_data_dir, "df.csv"))
            if os.path.exists(user_output_file):
                os.remove(user_output_file)
            if os.path.exists(user_error_file):
                os.remove(user_error_file)

            client = docker.from_env()
            print("Running commands inside container")
            user_container = client.containers.get(container_name)
            user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)
            print("Run commands inside container successfully")

            output = []
            if os.path.isfile(user_output_file):
                with open(user_output_file, "r") as f:
                    output.append(html.P(f.read(), style={"color": "black"}))

            if os.path.isfile(user_error_file):
                with open(user_error_file, "r") as f:
                    output.append(html.P(f.read(), style={"color": "red"}))
            return [output, False, False]

        except Exception as e:
            if (isinstance(e, docker.errors.NotFound)):
                try:
                    print("Recreate container")
                    client = docker.from_env()
                    container_name = 'biasnavi-' + user_id
                    client.containers.run('daisyy512/hello-docker',
                                          name=container_name,
                                          volumes=[user_data_dir + ':/home/sandbox/' + user_id],
                                          detach=True,
                                          tty=True)
                    print("Create container successfully")
                    user_container = client.containers.get(container_name)
                    user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)
                    output = []
                    if os.path.isfile(user_output_file):
                        with open(user_output_file, "r") as f:
                            output.append(html.P(f.read(), style={"color": "white"}))

                    if os.path.isfile(user_error_file):
                        with open(user_error_file, "r") as f:
                            output.append(html.P(f.read(), style={"color": "red"}))
                    return [output, False, False]

                except Exception as e:
                    print("Create container failed: ", e)
                    return ["Sandbox is not available", False, False]
            elif (isinstance(e, docker.errors.APIError)):
                if e.status_code is not None and e.status_code == 409:
                    user_container = client.containers.get(container_name)
                    print("Restart container")
                    user_container.start()
                    user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)

                    output = []
                    if os.path.isfile(user_output_file):
                        with open(user_output_file, "r") as f:
                            output.append(html.P(f.read(), style={"color": "white"}))

                    if os.path.isfile(user_error_file):
                        with open(user_error_file, "r") as f:
                            output.append(html.P(f.read(), style={"color": "red"}))
                    return [output, False, False]

                return [str(e), False, False]
            else:
                print(type(e))
                return [str(e), False, False]
    return [dash.no_update, False, False]


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
    [Input('dataset-selection', 'value')]
)
def update_columns(df_id):
    if df_id is None:
        return [], []

    # Get the columns of the selected DataFrame
    columns = [{'label': col, 'value': col} for col in global_vars.data_snapshots[int(df_id)-1].columns]

    return columns, columns
