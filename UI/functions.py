from UI.app_state import app_vars
import re
import docker
from pathlib import Path
import ast
import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_editor_components


#identify bias


# def parse_suggested_questions(response):
#     try:
#         pattern1 = r"1\.\s*([a-zA-Z0-9?\s]+)\?"
#         pattern2 = r"2\.\s*([a-zA-Z0-9?\s]+)\?"
#
#         match1 = re.search(pattern1, response)
#         match2 = re.search(pattern2, response)
#
#         if match1 or match2:
#             response1 = match1.group(1).strip() if match1 else ""
#             response2 = match2.group(1).strip() if match2 else ""
#             return [response1, response2]
#     except:
#         return []


def query_llm(query, stage, user_id, context=''):
    print(query, stage)
    response, media, sensi_attrs, suggestions, stage, op, explanation = app_vars.agent.run(query, stage)
    app_vars.agent.persist_history(user_id=str(user_id))
    app_vars.suggested_questions = suggestions
    return response, media, sensi_attrs, suggestions, stage, "Suggestion: "+op, explanation


def format_reply_to_markdown(reply):
    """
    Converts an LLM reply into proper Markdown format.

    Args:
        reply (str): The raw reply from the LLM.

    Returns:
        str: A Markdown-friendly formatted reply.
    """

    # Remove wrapping curly braces if present
    if reply.startswith("{") and reply.endswith("}"):
        reply = reply[1:-1]

    reply = reply.replace("\\n\\n", "  \n")

    reply = reply.replace("\\n", "  \n")

    reply = re.sub(r"(?<!\n)\n(?!\n)", "  \n", reply)

    # add more if necessary...

    return reply




def get_docker_client():
    context_sock = Path.home() / ".docker/run/docker.sock"
    legacy_mac_sock = Path.home() / "Library/Containers/com.docker.docker/Data/docker-cli.sock"
    default_linux_sock = Path("/var/run/docker.sock")

    for sock in [context_sock, legacy_mac_sock, default_linux_sock]:
        if sock.exists():
            print(f"[Docker] Using socket: {sock}")
            return docker.DockerClient(base_url=f'unix://{sock}')

    raise RuntimeError("No valid Docker socket found. Is Docker Desktop running?")


def format_message(msg):
    role_class = "user-message" if msg['role'] == 'user' else "assistant-message"
    content = msg.get("content")
    text = content  # default fallback

    try:
        parsed_content = ast.literal_eval(content)
        if isinstance(parsed_content, dict) and "answer" in parsed_content:
            text = parsed_content["answer"]
    except (ValueError, SyntaxError):
        pass  # keep default

    return html.Div([
        html.Div([
            html.Span(msg['role'].capitalize(), className="message-role"),
        ], className="message-header"),
        dcc.Markdown(text, className="message-content")
    ], className=f"chat-message {role_class}")


def contains_python_code_block(text):
    pattern = r"```python\s+.*?```"
    return bool(re.search(pattern, text, re.DOTALL))
def extract_text_and_code_blocks(text):
    pattern = r"```python\s*(.*?)\s*```"
    text_blocks = []
    code_blocks = []
    last_end = 0

    for match in re.finditer(pattern, text, re.DOTALL):
        start, end = match.span()


        if start > last_end:
            non_code = text[last_end:start].strip()
            if non_code:
                text_blocks.append(non_code)


        code = match.group(1).strip()
        if code:
            code_blocks.append(code)

        last_end = end


    if last_end < len(text):
        remaining = text[last_end:].strip()
        if remaining:
            text_blocks.append(remaining)

    return text_blocks, code_blocks

def create_python_editors(code):
    cid = app_vars.editor_id_counter
    app_vars.editor_id_counter += 1
    return html.Div([
        html.Div([
            dcc.Store(data="0",id={'type': "is-code-executed", 'index': cid}),
            html.Div([
                html.Div([
                    dash_editor_components.PythonEditor(
                        id={'type': 'commands-input', 'index': cid},
                        style={'overflow': "auto"},
                        value=code
                    )
                ], className='commands_editor'),
            ], id={'type': "python-code-editor", 'index': cid}, style={"marginTop": "20pt"}),
            dcc.Loading(
                id={'type': 'loading-', 'index': cid},
                children=[
                    dbc.Button(
                        "Run",
                        id={'type': 'execute-code-btn', 'index': cid},
                        n_clicks=0,
                        className='primary-button'
                    ),
                ],
                type="default",
            ),

        ]),

        html.Div([
            html.Div([
                html.H4("Result", className="secondary-title")
            ], className="query-header"),
            html.P(
                id={'type': 'console-area', 'index': cid},
                className='commands_result'
            ),
        ],
        id={'type': 'python-code-console', 'index': cid},
        style={"display": "none"})
    ],
    className="card", style={"paddingLeft": "20pt", "paddingRight": "20pt"})