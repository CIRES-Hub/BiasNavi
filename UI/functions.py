from UI.variable import global_vars
import re


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
    response, media, suggestions, stage, op, explanation = global_vars.agent.run(query, stage)
    global_vars.agent.persist_history(user_id=str(user_id))
    global_vars.suggested_questions = suggestions
    return response, media, suggestions, stage, "Recommended Operation: "+op, explanation


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
