from metric import fairlens as fl
import os
from UI.variable import global_vars
import re


#identify bias
def identify_sensitive_attributes(data, target):
    fscorer = fl.FairnessScorer(data, target)
    return fscorer.sensitive_attrs


def draw_multi_dist_plot(data, target, attrs):
    figures = fl.plot.mult_distr_plot(data, target, attrs)
    return figures


def calculate_demographic_report(data, target, attrs):
    fscorer = fl.FairnessScorer(data, target, attrs)
    return fscorer.distribution_score(method="dist_to_rest", max_comb=2)


def parse_suggested_questions(response):
    try:
        pattern1 = r"1\.\s*([a-zA-Z0-9?\s]+)\?"
        pattern2 = r"2\.\s*([a-zA-Z0-9?\s]+)\?"

        match1 = re.search(pattern1, response)
        match2 = re.search(pattern2, response)

        if match1 or match2:
            response1 = match1.group(1).strip() if match1 else ""
            response2 = match2.group(1).strip() if match2 else ""
            return [response1, response2]
    except:
        return []


def query_llm(query, user_id):
    print(query)
    response, media, suggestions = global_vars.agent.run(query)
    global_vars.agent.persist_history(user_id=str(user_id))
    global_vars.suggested_questions = suggestions
    return response, media, suggestions
