from utils.dataset_eval import DatasetEval
from langchain_core.tools import tool
from typing import Annotated, List, Union
import pandas as pd
from UI.app_state import app_vars

@tool
def evaluate_dataset(
    sens_attr: Annotated[Union[str, List[str]], "sensitive attributes (string or list)"]
    ) -> str:

    """Evaluate dataset with experiments given the sensitive attribute."""
    try:
        # Check dataset availability
        if app_vars.df is None or not getattr(app_vars, "data_snapshots", None):
            return "No dataset is loaded!"
        if not hasattr(app_vars, "target_attr") or app_vars.target_attr is None:
            return "No target attribute is set (app_vars.target_attr is None)."

        data: pd.DataFrame = app_vars.df
        label: str = app_vars.target_attr

        if label not in data.columns:
            return f"Target attribute `{label}` not found in dataset."

        # Normalize sens_attr into list[str]
        if sens_attr is None:
            sens_list: List[str] = []
        elif isinstance(sens_attr, (list, tuple, set)):
            sens_list = [str(x) for x in sens_attr]
        else:
            sens_list = [str(sens_attr)]

        # Check if sensitive attributes contain the target label
        if label in sens_list:
            return "Error: Sensitive attribute(s) cannot be the same as the target attribute."

        # Keep only existing sensitive attributes
        missing_sens = [c for c in sens_list if c not in data.columns]
        sens_list = [c for c in sens_list if c in data.columns]

        # Helper: determine if a column is categorical
        def is_categorical_series(s: pd.Series) -> bool:
            if pd.api.types.is_bool_dtype(s) or pd.api.types.is_categorical_dtype(s) or pd.api.types.is_object_dtype(s):
                return True
            if pd.api.types.is_numeric_dtype(s):
                _nunq = s.dropna().nunique()
                return _nunq <= max(20, int(len(s) * 0.02))
            return False

        # Decide task type and model
        y = data[label]
        if pd.api.types.is_numeric_dtype(y) and not is_categorical_series(y):
            task_type = "regression"
            model_type = "MLP"
        else:
            task_type = "classification"
            model_type = "SVM"

        # Run evaluation
        de = DatasetEval(
            data, label, ratio=0.2,
            task_type=task_type,
            sensitive_attribute=sens_list,
            model_type=model_type
        )
        res, scores = de.train_and_test()

        # Format report
        parts = []
        for s in scores:
            try:
                parts.append(s.to_string())
            except Exception:
                parts.append(str(s))
        report = "\n".join(parts)

        # Metadata
        meta = [
            f"label: {label}",
            f"task: {task_type}",
            f"model: {model_type}",
            f"sensitive attributes used: {sens_list or '[]'}",
        ]
        if missing_sens:
            meta.append(f"ignored (not found): {missing_sens}")

        return (
                f"[Run config] " + " | ".join(meta) + "\n"
                                                      f"The primary score is {res}.\n"
                                                      f"Experiment report:\n{report}\n"
                                                      f"Please use a table to display the result and explain the result in detail."
        )

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
