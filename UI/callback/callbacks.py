from UI.app import app
from dash.dependencies import Input, Output, State
import plotly.express as px
import base64
from agent import ConversationFormat, DatasetAgent
import datetime
from dash import callback_context
import io
from RAG import RAG
from dash import dcc, html, dash_table
import pandas as pd
from UI.variable import global_vars


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
    history, extension = global_vars.agent.get_history(c_format=ConversationFormat(format))
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
    [Output('left-column', 'style'),
     Output('menu-hide-chatbox', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-chatbox', 'n_clicks')],
    [State('menu-hide-chatbox', 'children')],
    prevent_initial_call=True
)
def hide_chatbox(n_clicks, label):
    if label == 'Show ChatBox':
        return {'display': 'block'}, "Hide ChatBox", 3, 6, 3
    else:
        return {'display': 'none'}, "Show ChatBox", 0, 9, 3


@app.callback(
    [Output('middle-column', 'style'),
     Output('menu-hide-dataview', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-dataview', 'n_clicks')],
    [State('menu-hide-dataview', 'children')],
    prevent_initial_call=True
)
def hide_dataviews(n_clicks, label):
    if label == 'Show Data View':
        return {'display': 'block'}, "Hide Data View", 3, 6, 3
    else:
        return {'display': 'none'}, "Show Data View", 6, 0, 6


@app.callback(
    [Output('right-column', 'style'),
     Output('menu-hide-chartview', 'children'),
     Output('left-column', 'width', allow_duplicate=True),
     Output('middle-column', 'width', allow_duplicate=True),
     Output('right-column', 'width', allow_duplicate=True),
     ],
    [Input('menu-hide-chartview', 'n_clicks')],
    [State('menu-hide-chartview', 'children')],
    prevent_initial_call=True
)
def hide_chartview(n_clicks, label):
    if label == 'Show Chart View':
        return {'display': 'block'}, "Hide Chart View", 3, 6, 3
    else:
        return {'display': 'none'}, "Show Chart View", 3, 9, 0


@app.callback(
    [Output('menu-model-gpt3dot5', 'children', allow_duplicate=True),
     Output('menu-model-gpt4', 'children', allow_duplicate=True),
     Output('menu-model-gpt4o', 'children', allow_duplicate=True)],
    Input('menu-model-gpt3dot5', 'n_clicks'),
    prevent_initial_call=True
)
def change_llm_model_gpt3dot5(n_clicks):
    global_vars.agent.set_llm_model('gpt3dot5')
    return "GPT-3.5 ✔", "GPT-4", "GPT-4o"


@app.callback(
    [Output('menu-model-gpt3dot5', 'children', allow_duplicate=True),
     Output('menu-model-gpt4', 'children', allow_duplicate=True),
     Output('menu-model-gpt4o', 'children', allow_duplicate=True)],
    Input('menu-model-gpt4', 'n_clicks'),
    prevent_initial_call=True
)
def change_llm_model_gpt3dot5(n_clicks):
    global_vars.agent.set_llm_model('gpt4')
    return "GPT-3.5", "GPT-4 ✔", "GPT-4o"


@app.callback(
    [Output('menu-model-gpt3dot5', 'children', allow_duplicate=True),
     Output('menu-model-gpt4', 'children', allow_duplicate=True),
     Output('menu-model-gpt4o', 'children', allow_duplicate=True)],
    Input('menu-model-gpt4o', 'n_clicks'),
    prevent_initial_call=True
)
def change_llm_model_gpt3dot5(n_clicks):
    global_vars.agent.set_llm_model('gpt4o')
    return "GPT-3.5", "GPT-4", "GPT-4o ✔"


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
    Output('table-overview', 'data'),
    Output('column-names-dropdown', 'options'),
    Output('error-file-format', 'is_open'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    Input('show-rows-button', 'n_clicks'),
    State('input-start-row', 'value'),
    State('input-end-row', 'value'),
    prevent_initial_call=True
)
def import_data_and_update_table(list_of_contents, list_of_names, click, start_row, end_row):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'upload-data':

        if list_of_contents is not None:
            # Assuming that only the first file is processed
            contents = list_of_contents[0]
            filename = list_of_names[0]
            global_vars.file_name = filename
            global_vars.dialog.append("DATASET: " + filename + '\n')
            global_vars.dialog.append("=" * 100 + '\n')
            # Decode the contents of the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'csv' in filename:
                # Assume that the user uploaded a CSV
                global_vars.df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name)
            else:
                return (), [], True
            # Return the data in a format that Dash DataTable can use

            return global_vars.df.head(15).to_dict('records'), [col for col in global_vars.df.columns], False

        else:
            return (), [], False  # If no file was uploaded

    else:
        start_row = int(start_row) - 1 if start_row else 0
        end_row = int(end_row) if end_row else len(global_vars.df)

        # Check that start_row and end_row are within bounds and in the correct order
        if start_row < 0 or end_row > len(global_vars.df) or start_row >= end_row:
            return [], (), False
        # Slicing the DataFrame
        xdf = global_vars.df.iloc[start_row:end_row]
        return xdf.to_dict('records'), [col for col in global_vars.df.columns], False


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


# @app.callback(
#     Output('query-area', 'value'),
#     Input('send-button', 'n_clicks'),
#     State('query-input', 'value'),
#     State('query-area', 'value'),
#     prevent_initial_call=True
# )
# def update_output(n_clicks,input_text, existing_text, ):
#     if n_clicks is None:
#         return ""  # If the button hasn't been clicked, do nothing
#     if df is None:
#         return "Please load a dataset first."
#     if input_text is None or input_text == '':
#         return "Please enter a valid query."
#     response = 'LLM: '+query_llm(input_text)
#     new_text = (existing_text if existing_text else '') + "\n"+"Me: "+input_text+"\n"+response
#     return new_text

# Update the llm chatbox
@app.callback(
    Output('query-area', 'children'),
    Output('error-query', 'is_open'),
    Input('send-button', 'n_clicks'),
    Input('query-input', 'n_submit'),
    [State('query-input', 'value'),
     State('query-area', 'children'),
     ],
    prevent_initial_call=True
)
def update_messages(n_clicks, n_submit, input_text, query_records):
    if n_clicks is None or input_text is None or global_vars.df is None:
        return query_records, True
    new_user_message = html.Div(input_text + '\n', className="user-msg")
    global_vars.dialog.append("\nUSER: " + input_text + '\n')
    if not query_records:
        query_records = []
    if global_vars.rag and global_vars.use_rag:
        input_text = global_vars.rag.invoke(input_text)
        global_vars.rag_prompt = input_text
    response = 'LLM: ' + query_llm(input_text) + '\n'
    global_vars.dialog.append("\n" + response)
    # Simulate a response from the system
    new_response_message = html.Div(response, className="llm-msg")
    query_records.append(new_user_message)
    query_records.append(new_response_message)
    return query_records, False


def query_llm(query):
    # prompt = """
    #                 Answer this question step by step and generate a output with details and inference:
    #         """ + query
    print(query)
    response = global_vars.agent.run(query)
    global_vars.agent.persist_history()
    return response

# @app.callback(
#     Output('query-output', 'children'),
#     [Input('send-query', 'n_clicks')],
#     [State('query-input', 'value'), State('stored-data', 'children')]
# )
# def update_output(n_clicks, query, stored_data):
#     # Process query and update output here
#     # ...
#     pass
