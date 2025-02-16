from bias import fairlens as fl


def calculate_demographic_report(data, target, attrs):
    fscorer = fl.FairnessScorer(data, target, attrs)
    return fscorer.distribution_score(method="dist_to_rest", max_comb=2)
