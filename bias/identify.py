from bias import fairlens as fl


def identify_sensitive_attributes(data, target):
    # This function identifies sensitive attributes based on column names and content.
    fscorer = fl.FairnessScorer(data, target)
    return fscorer.sensitive_attrs


