import time
import dash
from UI.app import app
from dash.dependencies import Input, Output, State
import base64
from agent import ConversationFormat, rag
import datetime
from dash import callback_context, MATCH, ALL, ctx
import io
from dash import dcc, html
from UI.functions import *
import dash_bootstrap_components as dbc
from flask_login import current_user
from UI.functions import query_llm
from agent.rag import RAG
from db_models.conversation import Conversation
from itertools import zip_longest
@app.callback(
    [Output("query-area", "children",allow_duplicate=True),
     Output("error-alert", "is_open", allow_duplicate=True),
    Output("error-alert", "children", allow_duplicate=True),
     Output("chat-update-trigger", "data"),
     Output("next-suggested-questions", "children"),
     Output("commands-input", "value"),
     Output('query-input', 'value'),
     Output("pipeline-alert", "is_open"),
     Output("pipeline-slider", "value"),
     Output("recommended-op", "children", allow_duplicate=True),
     Output("tooltip-expl", "children", allow_duplicate=True)],
    [Input('send-button', 'n_clicks'),
     Input('query-input', 'n_submit'),
     Input({"type": 'next-suggested-question', "index": ALL}, 'n_clicks')],
    [State('query-input', 'value'),
     State('query-area', 'children'),
     State('next-suggested-questions', 'children'),
     State('rag-switch', 'value'),],
    prevent_initial_input=True,
    prevent_initial_call=True
)
def update_messages(n_clicks, n_submit, question_clicked, input_text, query_records, suggested_questions, rag_status):
    if not input_text and not question_clicked:
        #no input information provided
        return query_records, True, "Please enter a query.",  dash.no_update, suggested_questions, "", "", dash.no_update, dash.no_update, dash.no_update,  dash.no_update
    if n_clicks is None and question_clicked is None:
        # no controls clicked
        return query_records, True, "Please enter a query.",  dash.no_update, suggested_questions, "", "", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if global_vars.df is None:
        # no dataset loaded
        return query_records, True, "Please upload a dataset first.", dash.no_update, suggested_questions, "", "", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    trigger = ctx.triggered_id

    if not isinstance(trigger, str) and 'next-suggested-question' in trigger.type:
        query = global_vars.suggested_questions[int(trigger.index[-1])]
    else:
        query = input_text
    new_user_message = html.Div(query + '\n', className="user-msg")
    global_vars.dialog.append("\nUSER: " + query + '\n')
    suggested_questions = []
    if not query_records:
        query_records = []
    context=''
    if global_vars.rag and rag_status:
        context = global_vars.rag.retrieve(query)
    answer, media, sensi_attrs, new_suggested_questions, stage, op, expl = query_llm(query, global_vars.current_stage, current_user.id, context)
    print(stage)
    change_stage = False
    stages = ["Identify","Measure","Surface","Adapt"]
    if stage is not None and stage in stages:
        if stage != global_vars.current_stage:
            global_vars.current_stage = stage
            change_stage = True
    if new_suggested_questions is not None:
        for i in range(len(new_suggested_questions)):
            if new_suggested_questions[i]:
                new_suggested_question = html.Div(dbc.CardBody([
                    html.P("Suggested Next Question", style={'fontWeight': 'bold', "marginBottom": "0px"}),
                    html.P(new_suggested_questions[i], style={"marginBottom": "0px"})],
                    style={"padding": 0}), className="next-suggested-question",
                    id={"type": "next-suggested-question", "index": f'next-question-{i}'}, n_clicks=0)
                suggested_questions.append(new_suggested_question)

    query_records.append(new_user_message)
    if contains_python_code_block(answer):
        text_blocks, code_blocks = extract_text_and_code_blocks(answer)
        for text, code in zip_longest(text_blocks, code_blocks):
            if text is not None:
                answer = format_reply_to_markdown(text)
                response = answer + '\n'
                global_vars.dialog.append("\n" + response)
                # Simulate a response from the system
                new_response_message = dcc.Markdown(response, className="llm-msg")
                query_records.append(new_response_message)
            if code is not None:
                answer = format_reply_to_markdown(code)
                response = answer + '\n'
                global_vars.dialog.append("\n" + response)
                query_records.append(create_python_editors(code))

    else:
        answer = format_reply_to_markdown(answer)
        response = answer + '\n'
        global_vars.dialog.append("\n" + response)
        # Simulate a response from the system
        new_response_message = dcc.Markdown(response, className="llm-msg")
        query_records.append(new_response_message)
    if media:
        query_records.append(media[-1])
    list_commands = global_vars.agent.list_commands
    return query_records, False, "", time.time(), suggested_questions, ('\n').join(list_commands) if len(
        list_commands) > 0 and not media else "", "", change_stage, stages.index(stage) if change_stage else dash.no_update, op, expl


@app.callback(
    Output("export-conversation", "data"),
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


# @app.callback(
#     Output('rag-switch-output', 'children'),
#     Output('rag-card', 'style'),
#     Output('RAG-button', 'style'),
#     Input('rag-switch', 'value')
# )
# def rag_switch(value):
#     if value:
#         global_vars.use_rag = True
#         return 'RAG: On', {'display': 'block'}, {'display': 'block'}
#     else:
#         global_vars.use_rag = False
#         return 'RAG: OFF', {'display': 'none'}, {'display': 'none'}

@app.callback(
    Output("rag-state", "data"),
    Input("rag-switch", "n_clicks"),
    prevent_initial_call=True
)
def toggle_rag_state(n):
    return n % 2 == 1

# Update UI based on state
@app.callback(
    Output("rag-switch", "className"),
    Input("rag-state", "data")
)
def update_rag_ui(active):
    if active:
        return "button-clicked"
    return "send-button"

@app.callback(
    Output('RAG-area', 'children'),
    Output("query-area", "children",allow_duplicate=True),
    Output('RAG-button', 'children',allow_duplicate=True),
    Input('upload-rag', 'contents'),
    State('upload-rag', 'filename'),
    Input('RAG-button', 'children'),
    Input('send-button', 'n_clicks'),
    State('RAG-area', 'children'),
    State('query-input', 'value'),
    State('rag-state', 'data'),
    State('query-area', 'children'),
    prevent_initial_call=True
)
def upload_rag_area(list_of_contents, list_of_names, clicks_rag, clicks_send, rag_output, query, rag_status, total_msg):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, html.Span(className="fas fa-file")

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    allowed_extensions = ('pdf', 'txt')

    if triggered_id == 'upload-rag':
        if list_of_contents is None:
            return dash.no_update, dash.no_update, html.Span(className="fas fa-file")

        filename = list_of_names[0]
        contents = list_of_contents[0]

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_type = filename.split('.')[-1].lower()

            if file_type in allowed_extensions:
                output = f"RAG files: {filename}\n"

                if global_vars.rag:
                    global_vars.rag.clean()

                global_vars.rag = RAG(io.BytesIO(decoded), file_type)
                total_msg.append(html.Div([html.I(className="bi bi-file-earmark-text",
                       style={"marginRight": "8px", "fontSize": "1.2rem"}),f"The file {filename} has been read." + '\n'], className="file-msg"))
                return [html.Div([output])], total_msg, html.Span(className="fas fa-file")
            else:
                error_msg = html.Div([
                    f"This file format ({file_type}) is not supported. Only {', '.join(allowed_extensions)} files are supported."
                ], className="file-msg")
                total_msg.append(error_msg)
                return error_msg, total_msg, html.Span(className="fas fa-file")

        except Exception as e:
            print(f"Error processing file upload: {e}")
            error_msg = html.Div(['There was an error processing the file.'],className="file-msg")
            total_msg.append(error_msg)
            return error_msg, total_msg, html.Span(className="fas fa-file")

    elif triggered_id == 'send-button':
        if not rag_status:
            return dash.no_update, dash.no_update, html.Span(className="fas fa-file")
        if not global_vars.rag or not rag_output:
            return dash.no_update, dash.no_update, html.Span(className="fas fa-file")

        try:
            docs = global_vars.rag.retrieve(query)
            rag_output=html.Div(["Retrieved relevant context: \n" + docs])

            return rag_output, dash.no_update, html.Span(className="fas fa-file")

        except Exception as e:
            print(f"Error processing file upload: {e}")
            error_msg = html.Div(['There was an error processing the file.'], className="file-msg")
            total_msg.append(error_msg)
            return error_msg, total_msg, html.Span(className="fas fa-file")

    return dash.no_update, dash.no_update, html.Span(className="fas fa-file")

@app.callback(
    Output('rag-switch-status', 'children'),
    Input('rag-switch', 'value'),
    prevent_initial_call=True
)
def rag_switch_status(value):
    if value:
        return f'RAG is ON.'
    else:
        return f'RAG is OFF.'

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
    Output({'type': 'llm-media-button', 'index': MATCH}, 'style', allow_duplicate=True),
    Input({'type': 'llm-media-button', 'index': MATCH}, 'children'),
    State({'type': 'llm-generated-chart', 'index': MATCH}, 'src'),
    prevent_initial_call=True
)
def explain_llm_figure(_, content):
    if content is not None:
        explanation = global_vars.agent.describe_image('', content)
        return dcc.Markdown(explanation.content,className="llm-text"), {"display": "block", "marginBottom": "20px", "marginTop": "20px"}, {"display":"none"}

@app.callback(
    Output("chat-history-content", "children"),
    Input("url", "pathname"),
    Input("chat-update-trigger", "data")
)
def update_chat_history(pathname, trigger):
    if (pathname == '/'):
        return dash.no_update
    user_id = str(current_user.id)
    conversations = Conversation.get_user_conversations(user_id)

    if not conversations:
        return [html.P("You don't have any chat history yet.")]

    history_blocks = []
    for idx, conv in enumerate(conversations):
        card_content = [
            dbc.CardHeader([
                html.H5(f"Dataset: {conv.dataset}", className="card-title card-header mb-0"),
                html.Small(f"Model: {conv.model}", className="text-muted"),
                html.Small(f"Last updated: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                           className="text-muted d-block")
            ], className="card-header"),
            dbc.CardBody([
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                [format_message(msg) for msg in conv.messages],
                                style={
                                    'maxHeight': '400px',  # Adjust this value as needed
                                    'overflowY': 'auto',
                                },
                                className="scrollable-conversation-body"
                            )
                        )
                    ),
                    id={"type": "collapse", "index": idx},
                    is_open=False,
                ),
                dbc.Button(
                    ["Show Messages ", html.I(
                        className="fas fa-chevron-down")],
                    id={"type": "collapse-button", "index": idx},
                    className="mt-3",
                    color="primary",
                    n_clicks=0,
                ),
            ])
        ]

        history_blocks.append(
            dbc.Card(card_content, className="mb-3 chat-history-card")
        )

    return history_blocks