"""
Visualize distributions of data.
"""
import itertools
from typing import Any, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import seaborn as sns
import os
from .. import utils
import plotly.graph_objects as go
from math import ceil
import plotly.express as px

def distr_plot(
        df: pd.DataFrame,
        target_attr: str,
        attr: str,
        groups: Sequence[Union[Mapping[str, List[Any]], pd.Series]],
        labels: Optional[list] = None,
):

    preds = utils.get_predicates_mult(df, groups)
    column = utils.infer_dtype(df[target_attr])
    colors = px.colors.qualitative.Pastel
    combined_data = zip(preds, labels)
    sorted_data = sorted(
        combined_data,
        key=lambda x: len(column[x[0]]),
        reverse=True
    )
    # Unpack sorted data
    sorted_preds, sorted_labels = zip(*sorted_data)


    # Plot the sorted data
    fig = go.Figure()
    for i, pred in enumerate(sorted_preds):
        fig.add_trace(go.Histogram(
            x=column[pred],
            bingroup=1,
            name=sorted_labels[i],
            marker=dict(color=colors[i]),
            showlegend=True,
        ))

    fig.update_layout(
        barmode="overlay",
        bargap=0.2,
        xaxis_title=f"<b>{target_attr}</b>",
        title = {
            'text': f"<b>Subgroup distribution of column {attr} w.r.t. {target_attr}</b>",
            'y': 0.95,  # Adjust the y position of the title (1.0 is the top, 0.0 is the bottom)
            'x': 0.5,  # Center the title (0.5 is the center)
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin = dict(t=55)  # Reduce the top margin to bring the plot closer to the title
    )
    return fig


def attr_distr_plot(
        df: pd.DataFrame,
        target_attr: str,
        attr: str,
        attr_distr_type: Optional[str] = None,
        max_quantiles: int = 8,
        #ax: Optional[Axes] = None,
):
    if target_attr == attr:
        raise ValueError("'target_attr' and 'attr' cannot be the same.")

    df_ = df[[attr, target_attr]].copy()

    col_ = utils.infer_dtype(df_[attr])

    if attr_distr_type is None:
        attr_distr_type = utils.infer_distr_type(col_).value

    # Bin data
    if attr_distr_type == "continuous" or attr_distr_type == "datetime":
        df_.loc[:, attr] = utils._bin_as_string(col_, attr_distr_type, max_bins=max_quantiles)

    # Values ordered by counts in order for overlay to work well.
    unique_values = df_[attr].dropna().value_counts().keys()

    labels = ["All"] + [str(val) for val in unique_values]
    groups = [pd.Series([True] * len(df_))] + [(df_[attr] == val) for val in unique_values]

    fig = distr_plot(
        df_,
        target_attr,
        attr,
        groups,
        labels=labels
    )

    return fig

def mult_distr_plot(
        df: pd.DataFrame,
        target_attr: str,
        attrs: Sequence[str],
        attr_distr_types: Optional[Mapping[str, str]] = None,
        max_quantiles: int = 8,
):
    attr_distr_types = attr_distr_types or {}
    figures = []
    for i, attr in enumerate(attrs):
        #ax_ = fig.add_subplot(r, c, i + 1)
        attr_distr_type = attr_distr_types[attr] if attr in attr_distr_types else None
        fig = attr_distr_plot(
            df,
            target_attr,
            attr,
            attr_distr_type=attr_distr_type,
            max_quantiles=max_quantiles,
        )
        figures.append(fig)
    return figures

