# Import libraries
import numpy as np
import pandas as pd
from metric import fairlens as fl
import matplotlib.pyplot as plt
from itertools import combinations, chain
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


class DatasetEval:
    def __init__(self, data, label, ratio=0.2, fixed=True):
        self.y_test = None
        self.y_train = None
        self.X_test = None
        self.X_train = None
        if data is None:
            raise ValueError('The dataframe is None.')
        else:
            self.split_dataset(data, label, ratio, fixed)

    def preprocess(self, data):
        d_copy = data.copy()


    def split_dataset(self, data, label, ratio=0.2, fixed=True):
        if label not in data.columns:
            raise ValueError('The label is not in the dataset.')
        if fixed:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                data.drop(label,axis=1), data[label], test_size=ratio, random_state=42)
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                data.drop(label,axis=1), data[label], test_size=ratio)


# import pandas as pd
# testdata = {
#     'c1': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]*1000,
#     'c2': [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]*1000,
# }
#
# df = pd.DataFrame(testdata)
#
# de = DatasetEval(df, 'c2')
# print(de.X_train)