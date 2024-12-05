# import time
# import dash
# from UI.app import app
# from dash.dependencies import Input, Output, State
# import base64
# from agent import ConversationFormat
# import datetime
# from dash import callback_context, MATCH, ALL, ctx
# import io
# from RAG import RAG
# from dash import dcc, html
# from UI.functions import *
# import dash_bootstrap_components as dbc
# from flask_login import current_user
# from UI.functions import query_llm
# import pandas as pd
# from agent import DatasetAgent
# from flask_login import logout_user, current_user
# from dash.exceptions import PreventUpdate
# import random
#
# @app.callback(
#     [Output("chat-area-chat", "children"),
#      Output("error-toast-chat", "is_open"),
#      Output("next-suggested-questions-chat", "children"),
#      Output('query-input-chat', 'value')],
#     [Input('send-button-chat', 'n_clicks'),
#      Input('query-input-chat', 'n_submit'),
#      Input({"type": 'next-suggested-question', "index": ALL}, 'n_clicks')],
#     [State('query-input-chat', 'value'),
#      State('chat-area-chat', 'children'),
#      State('next-suggested-questions-chat', 'children')],
#     prevent_initial_input=True,
#     prevent_initial_call=True
# )
# def update_messages(n_clicks, n_submit, question_clicked, input_text, query_records, suggested_questions):
#     if not input_text and not question_clicked:
#         #no input information provided
#         return query_records, True, suggested_questions, ""
#     if n_clicks is None and question_clicked is None:
#         # no controls clicked
#         return query_records, True, suggested_questions, ""
#     if global_vars.df is None:
#         # no dataset loaded
#         return query_records, True, suggested_questions, ""
#     trigger = ctx.triggered_id
#     query = ''
#     if not isinstance(trigger, str) and 'next-suggested-question' in trigger.type:
#         query = global_vars.suggested_questions[int(trigger.index[-1])]
#     else:
#         query = input_text
#     new_user_message = html.Div(query + '\n', className="user-msg")
#     suggested_questions = []
#     if not query_records:
#         query_records = []
#     if global_vars.rag and global_vars.use_rag:
#         input_text = global_vars.rag.invoke(query)
#         global_vars.rag_prompt = query
#     output_text, media, new_suggested_questions = query_llm(query, current_user.id)
#
#     if new_suggested_questions is not None:
#         for i in range(len(new_suggested_questions)):
#             if new_suggested_questions[i]:
#                 new_suggested_question = html.Div(dbc.CardBody([
#                     html.P("Suggested Next Question", style={'fontWeight': 'bold', "marginBottom": "0px"}),
#                     html.P(new_suggested_questions[i], style={"marginBottom": "0px"})],
#                     style={"padding": 0}), className="next-suggested-question",
#                     id={"type": "next-suggested-question", "index": f'next-question-{i}'}, n_clicks=0)
#                 suggested_questions.append(new_suggested_question)
#
#     response = 'Assistant: ' + output_text + '\n'
#     global_vars.dialog.append("\n" + response)
#     # Simulate a response from the system
#     new_response_message = dcc.Markdown(response, className="llm-msg")
#     query_records.append(new_user_message)
#     query_records.append(new_response_message)
#     return query_records, False, suggested_questions, ""
#
#
# @app.callback(
#     Output("upload-data-modal-chat", "style", allow_duplicate=True),
#     Output("chat-area-chat", "children", allow_duplicate=True),
#     Output("upload-modal-chat", "is_open", allow_duplicate=True),
#     Input('upload-data-modal-chat', 'contents'),
#     State('upload-data-modal-chat', 'filename'),
#     State("upload-data-modal-chat", "style",),
#     State("chat-area-chat", "children"),
#     prevent_initial_call=True,
# )
# def import_data_and_update_table(list_of_contents_modal, list_of_names_modal, style, query_records):
#     triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
#     if triggered_id == 'upload-data-modal-chat':
#         if not list_of_contents_modal or not list_of_names_modal:
#             return style, "", False
#
#         # Process the first file only
#         contents = list_of_contents_modal[0]
#         filename = list_of_names_modal[0]
#
#         content_type, content_string = contents.split(',')
#         decoded = base64.b64decode(content_string)
#
#         if 'csv' not in filename:
#             return style, "", False
#
#         raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#         global_vars.file_name = filename
#         global_vars.df = raw_data  # DataWrangler.fill_missing_values(raw_data)
#         global_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
#         global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name, conversation_session=global_vars.conversation_session)
#         if not query_records:
#             query_records = []
#         query_records.append(
#             dcc.Markdown("The dataset has been successfully uploaded! Let's start chatting!", className="llm-msg"))
#         return style, query_records, False
#     return style, "", False
#
# @app.callback(
#     Output('url', 'pathname', allow_duplicate=True),
#     [Input('logout-button-chat', 'n_clicks')],
#     prevent_initial_call=True
# )
# def logout_and_redirect(n_clicks):
#     if n_clicks:
#         logout_user()
#         return "/"
#     raise PreventUpdate