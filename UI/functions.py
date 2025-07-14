from UI.variable import global_vars
import re
import docker
import os
from pathlib import Path
import ast
from dash import dcc, html
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
    response, media, sensi_attrs, suggestions, stage, op, explanation = global_vars.agent.run(query, stage)
    global_vars.agent.persist_history(user_id=str(user_id))
    global_vars.suggested_questions = suggestions
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
