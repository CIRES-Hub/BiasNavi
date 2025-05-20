
from utils.dataset_eval import DatasetEval
from langchain_core.tools import tool
from typing import Annotated, List

@tool
def evaluate_dataset(sens_attr:Annotated[list[str], "sensitive attributes"],
                     label:Annotated[str, "the target attribute or label"],
                     task:Annotated[str, "the experiment task: classification or regression"]="classification",
                     model:Annotated[str, "model used for the experiment: SVM, MLP, or Logistic"]="SVM") \
        -> str:
    """Evaluate dataset with experiments given the sensitive attribute and target attribute."""
    from UI.variable import global_vars
    if task not in ["Classification","classification"] and task not in ["regression","Regression"]:
        return "Task can only be classification or regression."
    if global_vars.df is None or not global_vars.data_snapshots:
        return 'No dataset is loaded!'
    if sens_attr is None or label is None or task is None or model is None:
        return 'The experimental setting is incomplete!'
    data = global_vars.df
    if label in sens_attr:
        return 'The label cannot be in the sensitive attributes!'
    if data[label].dtype in ['float64', 'float32'] and task == 'classification':
        return ('The target attribute is continuous (float) but the default task is classification. Do you want to do regression?')
    if data[label].dtype == 'object' or data[label].dtype.name == 'bool' or data[label].dtype.name == 'category':
        if task == 'regression':
            return 'The target attribute is categorical and cannot be used for regression task. Do you want to do classification?'
    de = DatasetEval(data, label, ratio=0.2, task_type=task, sensitive_attribute=sens_attr, model_type=model)
    res, scores = de.train_and_test()
    report = []
    for score in scores:
        report.append(score.to_string())
    report = '\n'.join(report)
    return f"The accuracy of the model is {res} and the experiment result report is {report}. Please explain the result in detail."

