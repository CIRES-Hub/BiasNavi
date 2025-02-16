from imblearn.over_sampling import SMOTENC
from sklearn.utils import resample
import pandas as pd
from sklearn.impute import SimpleImputer
import numpy as np
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
        Perform SMOTE-NC to balance the classes in a dataset with mixed data types,
        and fallback to random oversampling for categorical-only datasets.

        Parameters:
        - random_state (int): Random state for reproducibility.

        Returns:
        - pd.DataFrame: A new DataFrame with balanced classes.
        """
        # Split data into features and target
        X = self.df.drop(columns=[self.target_col])
        y = self.df[self.target_col]

        # Identify columns with all NaN values
        all_nan_columns = X.columns[X.isna().all()].tolist()

        # Remove columns with all NaN values for SMOTE
        X_non_nan = X.drop(columns=all_nan_columns)

        # Handle NaN values: Impute missing data for non-NaN columns
        imputer = SimpleImputer(strategy='most_frequent')  # Use 'mean' for numerical columns
        X_imputed = pd.DataFrame(imputer.fit_transform(X_non_nan), columns=X_non_nan.columns)

        # Get categorical column indices
        categorical_indices = self._get_categorical_indices(X_imputed)

        # Check if the dataset has numerical features
        num_numerical_features = len(X_imputed.select_dtypes(include=['float64', 'int64']).columns)

        if num_numerical_features == 0:
            # Fallback to random oversampling if no numerical features exist
            print("No numerical features found. Falling back to random oversampling.")
            max_class_size = y.value_counts().max()

            # Oversample each class
            balanced_dfs = []
            for class_label in y.unique():
                class_data = self.df[self.df[self.target_col] == class_label]
                oversampled_data = resample(
                    class_data,
                    replace=True,
                    n_samples=max_class_size,
                    random_state=random_state
                )
                balanced_dfs.append(oversampled_data)

            balanced_df = pd.concat(balanced_dfs).reset_index(drop=True)
            return balanced_df

        # Determine the smallest class size
        class_counts = y.value_counts()
        min_class_size = class_counts.min()

        # Ensure k_neighbors is valid
        k_neighbors = max(1, min(5, min_class_size - 1))

        # Apply SMOTE-NC for mixed data
        smote_nc = SMOTENC(
            categorical_features=categorical_indices,
            k_neighbors=k_neighbors,
            random_state=random_state
        )
        X_resampled, y_resampled = smote_nc.fit_resample(X_imputed, y)

        # Combine resampled features and target into a DataFrame
        resampled_df = pd.concat(
            [pd.DataFrame(X_resampled, columns=X_imputed.columns),
             pd.DataFrame(y_resampled, columns=[self.target_col])],
            axis=1
        )

        # Add back all-NaN columns to the end
        for col in all_nan_columns:
            resampled_df[col] = np.nan

        # Reorder columns to place all-NaN columns at the end
        reordered_columns = [col for col in resampled_df.columns if col != self.target_col] + [self.target_col]
        resampled_df = resampled_df[reordered_columns]

        return resampled_df.reset_index(drop=True)

# import pandas as pd
# import numpy as np
#
# # Create a larger, more complex dataset with mixed types and missing values
# np.random.seed(42)
#
# data = pd.DataFrame({
#     'feature_int': np.random.randint(1, 100, size=100),                       # Integer feature
#     'feature_float': np.random.uniform(0, 1, size=100),                      # Float feature
#     'feature_cat1': np.random.choice(['A', 'B', 'C', None], size=100),       # Categorical with NaNs
#     'feature_cat2': np.random.choice(['X', 'Y', None], size=100),            # Categorical with NaNs
#     'label': np.random.choice([0, 1, 2, 3], size=100, p=[0.6, 0.2, 0.15, 0.05])  # Imbalanced labels
# })
#
# # Introduce additional missing values
# data.loc[np.random.choice(data.index, size=10, replace=False), 'feature_int'] = np.nan
# data.loc[np.random.choice(data.index, size=15, replace=False), 'feature_float'] = np.nan
#
# print("Original Dataset (First 10 Rows):")
# print(data.head(10))
#
# print("Label Distribution:")
# print(data['label'].value_counts())
# # Instantiate and balance using MixedSampler
# sampler = Sampler(data, target_col='label')
#
# # Apply SMOTE-NC or random oversampling
# resampled_data = sampler.smote()
#
# print("\nResampled Dataset (First 10 Rows):")
# print(resampled_data.head(10))
#
# print("\nResampled Label Distribution:")
# print(resampled_data['label'].value_counts())
