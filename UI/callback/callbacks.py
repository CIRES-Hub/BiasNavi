import time
import dash
from UI.app import app
from models.users import User
from models.databases import db
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import ConversationFormat, DatasetAgent
import datetime
from dash import callback_context, MATCH, ALL,ctx
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


@app.callback(
    Output("export", "data"),
    Output("error-export", "is_open"),
    Input("download-button", "n_clicks"),
    Input("export-format-dropdown", "value"),
    prevent_initial_call=True,
)
def func(n_clicks, format):
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
    [Output('table-overview', 'data'),
     Output('table-overview', 'columns'),
     Output('column-names-dropdown', 'options'),
     Output('error-file-format', 'is_open'),
     Output('bias-report', 'children'),
     Output('table-overview', 'style_data_conditional'),
     Output('multi_dist_plot', 'src'),
     Output('bias-overview', 'data'),
     Output('dataset-name', 'children')],
    [Input('upload-data', 'contents'),
     Input('show-rows-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('input-start-row', 'value'),
     State('input-end-row', 'value')],
    prevent_initial_call=True
)
def import_data_and_update_table(list_of_contents, n_clicks, list_of_names, start_row, end_row):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'upload-data':
        if not list_of_contents or not list_of_names:
            return [], [], [], False, [], [], "", [], ""

        # Process the first file only
        contents = list_of_contents[0]
        filename = list_of_names[0]

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if 'csv' not in filename:
            return [], [], True, [], [], "", [], ""

        raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        global_vars.file_name = filename
        global_vars.dialog.append("DATASET: " + filename + '\n')
        global_vars.dialog.append("=" * 100 + '\n')
        global_vars.df = DataWrangler.fill_missing_values(raw_data)
        global_vars.df = raw_data  #DataWrangler.fill_missing_values(raw_data)
        global_vars.agent = DatasetAgent(global_vars.df, file_name=filename)
        if  all([current_user.professional_role, current_user.industry_sector, current_user.expertise_level]):
            query_llm('. \n '.join([f'my professional role is {current_user.professional_role}' if current_user.professional_role else '',
                        f'I am working in {current_user.industry_sector} industry' if current_user.industry_sector else '',
                        f'my level of expertise in data analysis is {current_user.expertise_level}' if current_user.expertise_level else ''
                    ]))

        sensitive_attrs = identify_sensitive_attributes(global_vars.df, "decile_score")
        styles = [{'if': {'column_id': attr}, 'backgroundColor': 'tomato', 'color': 'white'} for attr in
                  sensitive_attrs]
        bias_identification = " ".join(sensitive_attrs)

        draw_multi_dist_plot(global_vars.df, "decile_score", sensitive_attrs)
        bias_stats = calculate_demographic_report(global_vars.df, "decile_score", ["sex", "race"])

        bias_report_content = html.Div([
            html.H5("Identified sensitive attributes"),
            html.P([
                html.B(f"{bias_identification}. ", style={'color': 'tomato'}),
                "When making decisions, it should be cautious to use these attributes."
            ])
        ])
        return (
            global_vars.df.head(15).to_dict('records'),
            [{"name": col, "id": col,'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            bias_report_content,
            styles,
            f"../assets/{filename}_mult_dist_plot.png",
            bias_stats.to_dict('records'),
            f"Dataset: {filename} (maximum row number:{len(global_vars.df)})"
        )

    elif triggered_id == 'show-rows-button':
        if global_vars.df is None:
            return [], [], [], False, [], [], "", [], ""

        start_row = int(start_row) - 1 if start_row else 0
        end_row = int(end_row) if end_row else len(global_vars.df)

        if start_row < 0 or end_row > len(global_vars.df) or start_row >= end_row:
            return (
                [],
                [{"name": col, "id": col,'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                [{'label': col, 'value': col} for col in global_vars.df.columns],
                False,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update
            )

        xdf = global_vars.df.iloc[start_row:end_row]
        return (
            xdf.to_dict('records'),
            [{"name": col, "id": col,'deletable': True, 'renamable': True} for col in global_vars.df.columns],
            [{'label': col, 'value': col} for col in global_vars.df.columns],
            False,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )

    return [], [], [], False, [], [], "", [], ""

@app.callback(
    Output('download-data-csv', 'data'),
    [Input('save-data-button', 'n_clicks')],
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
    Output('bar-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('column-names-dropdown', 'value'),
    prevent_initial_call=True
)
def update_graph(selected_column):
    value_counts = global_vars.df[selected_column].value_counts()
    bar = px.bar(
        x=value_counts.index,
        y=value_counts.values,
        labels={'x': selected_column, 'y': 'Count'},
        title=f'Bar Chart - Distribution of {selected_column}'
    )

    value_counts = global_vars.df[selected_column].value_counts().reset_index()
    value_counts.columns = [selected_column, 'count']

    pie = px.pie(
        value_counts,
        names=selected_column,
        values='count',
        title=f'Pie Chart - Distribution of {selected_column}'
    )
    return bar, pie


# Update the llm chatbox
@app.callback(
    [Output("query-area", "children"),
     Output("error-query", "is_open"),
     Output('llm-media-area', 'children'),
     Output("chat-update-trigger", "data"),
     Output("next-suggested-questions", "children"),
     Output("query-input", "value"),],
    [Input('send-button', 'n_clicks'),
     Input('query-input', 'n_submit'),
     Input({"type": 'next-suggested-question', "index": ALL}, 'n_clicks'),],
    [State('query-input', 'value'),
     State('query-area', 'children'),
     State('next-suggested-questions', 'children')],
    prevent_initial_input=True,
    prevent_initial_call=True
)
def update_messages(n_clicks, n_submit, input_3, input_text, query_records, suggested_questions):
    if ((n_clicks is None or input_text is None) and input_3 is None) or global_vars.df is None:
        return query_records, True, None, dash.no_update, suggested_questions
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
        for i  in range(len(new_suggested_questions)):
            if new_suggested_questions[i]:
                new_suggested_question = html.Div(dbc.CardBody([
                    html.P(" Suggestion", style={'font-weight': 'bold', "margin-bottom": "0px"}),
                    html.P(new_suggested_questions[i], style={"margin-bottom": "0px"})],
                    style={"padding": 0}), className="next-suggested-question", id={"type": "next-suggested-question", "index": f'next-question-{i}'}, n_clicks=0)
                suggested_questions.append(new_suggested_question)

    response = 'Assistant: ' + output_text + '\n'
    global_vars.dialog.append("\n" + response)
    # Simulate a response from the system
    new_response_message = dcc.Markdown(response, className="llm-msg")
    query_records.append(new_user_message)
    query_records.append(new_response_message)
    print(suggested_questions)
    return query_records, False, media, time.time(), suggested_questions


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
    response, media = global_vars.agent.run(query)
    response_suggested_questions, _ = global_vars.agent.run("Generate 2 relevant follow-up questions in format 1.question 1, 2. question 2")
    suggested_questions = parse_suggested_questions(response_suggested_questions)
    global_vars.agent.persist_history(user_id=str(current_user.id))
    global_vars.suggested_questions = suggested_questions
    return response, media, suggested_questions

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
