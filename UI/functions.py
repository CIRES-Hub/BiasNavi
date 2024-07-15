from metric import fairlens as fl


#identify bias
def identify_sensitive_attributes(data, target):
    fscorer = fl.FairnessScorer(data, target)
    return fscorer
