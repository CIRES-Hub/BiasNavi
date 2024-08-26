# Import libraries
import numpy as np
import pandas as pd
from metric import fairlens as fl
import matplotlib.pyplot as plt
from itertools import combinations, chain
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class DatasetEval(object):
    def __init__(self, df, label, ratio=0.8, fixed=True):
        if df is None:
            raise ValueError('The dataframe is None.')

    # def split_dataset(self, df, label, ratio=0.8, fixed=True):
    #     if fixed:
    #         X_train, X_test, y_train, y_test = train_test_split(
    #             df, y, test_size=0.33, random_state=42)
