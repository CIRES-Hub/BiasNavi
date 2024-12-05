from imblearn.over_sampling import SMOTENC
from sklearn.utils import resample
import pandas as pd

class Sampler:
    def __init__(self, df, target_col):
        """
        Initialize the Sampler class.

        Parameters:
        - df (pd.DataFrame): The input dataframe.
        - target_col (str): The name of the target column.
        """
        self.df = df
        self.target_col = target_col

    def _get_categorical_indices(self, X):
        """
        Identify indices of categorical features.

        Parameters:
        - X (pd.DataFrame): Feature DataFrame.

        Returns:
        - List[int]: Indices of categorical columns.
        """
        return [i for i, dtype in enumerate(X.dtypes) if dtype == 'object']

    def undersample(self, random_state=42):
        """
        Perform random undersampling to balance the classes.

        Parameters:
        - random_state (int): Random state for reproducibility.

        Returns:
        - pd.DataFrame: A new DataFrame with balanced classes.
        """
        min_class_size = self.df[self.target_col].value_counts().min()

        # Downsample each class
        balanced_dfs = []
        for class_label in self.df[self.target_col].unique():
            class_data = self.df[self.df[self.target_col] == class_label]
            downsampled_data = resample(
                class_data,
                replace=False,
                n_samples=min_class_size,
                random_state=random_state
            )
            balanced_dfs.append(downsampled_data)

        balanced_df = pd.concat(balanced_dfs)
        return balanced_df

    def oversample(self, random_state=42):
        """
        Perform random oversampling to balance the classes.

        Parameters:
        - random_state (int): Random state for reproducibility.

        Returns:
        - pd.DataFrame: A new DataFrame with balanced classes.
        """
        max_class_size = self.df[self.target_col].value_counts().max()

        # Oversample each class
        balanced_dfs = []
        for class_label in self.df[self.target_col].unique():
            class_data = self.df[self.df[self.target_col] == class_label]
            oversampled_data = resample(
                class_data,
                replace=True,
                n_samples=max_class_size,
                random_state=random_state
            )
            balanced_dfs.append(oversampled_data)

        balanced_df = pd.concat(balanced_dfs)
        return balanced_df

    def smote(self, random_state=42):
        """
        Perform SMOTE-NC to balance the classes in a dataset with mixed data types.

        Parameters:
        - random_state (int): Random state for reproducibility.

        Returns:
        - pd.DataFrame: A new DataFrame with balanced classes.
        """
        # Split data into features and target
        X = self.df.drop(columns=[self.target_col])
        y = self.df[self.target_col]

        # Get categorical column indices
        categorical_indices = self._get_categorical_indices(X)

        # Determine the smallest class size
        class_counts = y.value_counts()
        min_class_size = class_counts.min()

        # If any class has fewer than 2 samples, handle manually
        if min_class_size < 2:
            print("Warning: Classes with fewer than 2 samples detected. Handling manually.")
            # Manually duplicate samples for small classes
            balanced_dfs = []
            for class_label in class_counts.index:
                class_data = self.df[self.df[self.target_col] == class_label]
                if len(class_data) < 2:
                    # Duplicate rows to create at least 2 samples
                    class_data = class_data.sample(n=2, replace=True, random_state=random_state)
                balanced_dfs.append(class_data)
            self.df = pd.concat(balanced_dfs).reset_index(drop=True)

            # Re-split data after manual duplication
            X = self.df.drop(columns=[self.target_col])
            y = self.df[self.target_col]

        # Ensure k_neighbors is valid
        k_neighbors = max(1, min(5, min_class_size - 1))

        # Apply SMOTE-NC for mixed data
        smote_nc = SMOTENC(
            categorical_features=categorical_indices,
            k_neighbors=k_neighbors,
            random_state=random_state
        )
        X_resampled, y_resampled = smote_nc.fit_resample(X, y)

        # Combine resampled features and target into a DataFrame
        resampled_df = pd.concat(
            [pd.DataFrame(X_resampled, columns=X.columns),
             pd.DataFrame(y_resampled, columns=[self.target_col])],
            axis=1
        ).reset_index(drop=True)
        return resampled_df


# import pandas as pd
#
# # Example dataset with very small class sizes
# data = pd.DataFrame({
#     'feature_int': [1, 2, 3, 4, 5, 6, 7],
#     'feature_float': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7],
#     'feature_cat': ['A', 'B', 'A', 'B', 'A', 'B', 'A'],  # Categorical (object)
#     'label': [0, 0, 1, 1, 2, 2, 3]  # Class 3 has only 1 sample
# })
#
# sampler = MixedSampler(data, target_col='label')
#
# # Apply SMOTE-NC
# smote_data = sampler.smote()
# print("SMOTE-NC Data:")
# print(smote_data)
