from metric import fairlens as fl
import os
from UI.variable import global_vars
import re

#identify bias
def identify_sensitive_attributes(data, target):
    fscorer = fl.FairnessScorer(data, target)
    return fscorer.sensitive_attrs

def draw_multi_dist_plot(data, target, attrs):
    attrs_to_plot = []
    for attr in attrs:
        if data[attr].unique().size < 100:
            attrs_to_plot.append(attr)
    fig = fl.plot.mult_distr_plot(data, target, attrs_to_plot)
    fig.savefig(f"./UI/assets/{global_vars.file_name}_mult_dist_plot.png")

def calculate_demographic_report(data, target, attrs):
    fscorer = fl.FairnessScorer(data, target,attrs)
    return fscorer.distribution_score(method="dist_to_rest")

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