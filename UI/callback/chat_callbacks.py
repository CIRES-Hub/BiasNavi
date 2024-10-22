import time
import dash
from UI.app import app
from dash.dependencies import Input, Output, State
import base64
from agent import ConversationFormat
import datetime
from dash import callback_context, MATCH, ALL, ctx
import io
from RAG import RAG
from dash import dcc, html
from UI.functions import *
import dash_bootstrap_components as dbc
from flask_login import current_user
from UI.functions import query_llm


@app.callback(
    [Output("query-area", "children"),
     Output("error-export", "is_open", allow_duplicate=True),
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
def update_messages(n_clicks, n_submit, question_clicked, input_text, query_records, suggested_questions):
    if not input_text and not question_clicked:
        #no input information provided
        return query_records, True, None, dash.no_update, suggested_questions, "", ""
    if n_clicks is None and question_clicked is None:
        # no controls clicked
        return query_records, True, None, dash.no_update, suggested_questions, "", ""
    if global_vars.df is None:
        # no dataset loaded
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
    output_text, media, new_suggested_questions = query_llm(query, current_user.id)

    if new_suggested_questions is not None:
        for i in range(len(new_suggested_questions)):
            if new_suggested_questions[i]:
                new_suggested_question = html.Div(dbc.CardBody([
                    html.P("Suggested Next Question", style={'fontWeight': 'bold', "marginBottom": "0px"}),
                    html.P(new_suggested_questions[i], style={"marginBottom": "0px"})],
                    style={"padding": 0}), className="next-suggested-question",
                    id={"type": "next-suggested-question", "index": f'next-question-{i}'}, n_clicks=0)
                suggested_questions.append(new_suggested_question)

    response = output_text + '\n'
    global_vars.dialog.append("\n" + response)
    # Simulate a response from the system
    new_response_message = dcc.Markdown(response, className="llm-msg")
    query_records.append(new_user_message)
    query_records.append(new_response_message)
    list_commands = global_vars.agent.list_commands
    if not media:
        return query_records, False, dash.no_update, time.time(), suggested_questions, ('\n').join(list_commands) if len(
            list_commands) > 0 else "", ""
    return query_records, False, media, time.time(), suggested_questions, ('\n').join(list_commands) if len(
        list_commands) > 0 else "", ""


@app.callback(
    Output("export", "data"),
    Input("download-button", "n_clicks"),
    Input("export-format-dropdown", "value"),
    prevent_initial_call=True,
)
def export_conversation(n_clicks, format):
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if (triggered_id != 'download-button'):
        return None
    # return dict(content="".join(global_vars.dialog), filename=f"query-history-{formatted_date_time}.txt")
    if (global_vars.agent is None):
        return None
    history, extension = global_vars.agent.get_history(
        c_format=ConversationFormat(format))
    return dict(content=history, filename=f"query-history-{formatted_date_time}" + extension)


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
    Output({'type': 'llm-media-modal', 'index': MATCH}, 'is_open'),
    Input({'type': 'llm-media-figure', 'index': MATCH}, 'n_clicks'),
    State({'type': 'llm-media-figure', 'index': MATCH}, 'id'),
)
def show_figure_modal(n_clicks, id):
    if (n_clicks is not None and n_clicks > 0):
        return True
    else:
        return False

@app.callback(
    Output({'type': 'llm-media-explanation', 'index': MATCH}, 'children'),
    Output({'type': 'llm-media-explanation', 'index': MATCH}, 'style'),
    Input({'type': 'llm-media-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'llm-generated-chart', 'index': MATCH}, 'src'),
    prevent_initial_call=True
)
def show_figure_modal(n_clicks, content):
    if n_clicks and n_clicks > 0 and content is not None:
        explanation = global_vars.agent.describe_image('', content)
        return dcc.Markdown(explanation.content,className="chart-explanation"), {"display": "block"}

