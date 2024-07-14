import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ks_2samp
from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from statsmodels.stats.outliers_influence import variance_inflation_factor


class BiasMetrics:
    @staticmethod
    def correlation_analysis(df, target):
        df_copy = df.copy()
        if df_copy[target].dtype == 'object':
            df_copy[target] = LabelEncoder().fit_transform(df_copy[target])
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        correlations = df_copy[numeric_cols].corrwith(df_copy[target])
        return correlations

    @staticmethod
    def feature_importance(df, target):
        df_copy = df.copy()
        X = df_copy.drop(columns=[target])
        y = df_copy[target]

        if y.dtype == 'object':
            y = LabelEncoder().fit_transform(y)

        X_encoded = X.apply(lambda col: LabelEncoder().fit_transform(col) if col.dtype == 'object' else col)

        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X_encoded)

        model = RandomForestClassifier()
        model.fit(X_imputed, y)
        importances = pd.Series(model.feature_importances_, index=X_encoded.columns)
        return importances

    @staticmethod
    def mutual_information(df, target):
        df_copy = df.copy()
        X = df_copy.drop(columns=[target])
        y = df_copy[target]

        if y.dtype == 'object':
            y = LabelEncoder().fit_transform(y)

        X_encoded = X.apply(lambda col: LabelEncoder().fit_transform(col) if col.dtype == 'object' else col)

        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X_encoded)

        mi = mutual_info_classif(X_imputed, y, discrete_features='auto')
        mi_series = pd.Series(mi, index=X_encoded.columns)
        return mi_series

    @staticmethod
    def chi_square_test(df, target):
        df_copy = df.copy()
        chi2_results = {}
        for col in df_copy.columns:
            if col != target and df_copy[col].dtype == 'object':
                contingency_table = pd.crosstab(df_copy[col], df_copy[target])
                chi2, p, _, _ = chi2_contingency(contingency_table)
                chi2_results[col] = p
        return chi2_results

    @staticmethod
    def ks_test(df, target):
        df_copy = df.copy()
        ks_results = {}
        for col in df_copy.columns:
            if col != target and df_copy[col].dtype != 'object':
                if df_copy[target].dtype == 'object':
                    y_encoded = LabelEncoder().fit_transform(df_copy[target])
                else:
                    y_encoded = df_copy[target]

                stat, p_value = ks_2samp(df_copy[col][y_encoded == 1], df_copy[col][y_encoded == 0])
                ks_results[col] = p_value
        return ks_results

    @staticmethod
    def vif_analysis(df):
        df_copy = df.copy()
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        X = df_copy[numeric_cols].assign(intercept=1)
        vif_data = pd.DataFrame()
        vif_data['feature'] = X.columns
        vif_data['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        return vif_data.drop(index=X.columns.get_loc('intercept'))

# Example Usage:
# Assuming 'data' is your DataFrame and 'target' is your target variable
# metrics = BiasMetrics()
# correlations = metrics.correlation_analysis(data, 'target')
# importances = metrics.feature_importance(data, 'target')
# mutual_info = metrics.mutual_information(data, 'target')
# chi_square = metrics.chi_square_test(data, 'target')
# ks_test_results = metrics.ks_test(data, 'target')
# vif = metrics.vif_analysis(data)

# print("Correlations:\n", correlations)
# print("Feature Importances:\n", importances)
# print("Mutual Information:\n", mutual_info)
# print("Chi-Square Test p-values:\n", chi_square)
# print("KS Test p-values:\n", ks_test_results)
# print("VIF Analysis:\n", vif)
