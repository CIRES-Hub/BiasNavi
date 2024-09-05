import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.svm import SVR
def detect_text_columns(df, text_length_threshold=50):
    text_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':  # Check if the column is of type 'object'
            # Check if the maximum length of text in the column exceeds the threshold
            if df[col].apply(lambda x: len(str(x)) if pd.notnull(x) else 0).mean() > text_length_threshold:
                text_columns.append(col)
    return text_columns


class DatasetEval:
    def __init__(self, data, label, ratio=0.5, task_type='classification', fixed=True, text_length_threshold=50,
                 sensitive_attribute=None):
        self.y_test = None
        self.y_train = None
        self.X_test = None
        self.X_train = None
        self.task_type = task_type  # Store task_type as an instance variable
        self.sensitive_attribute = sensitive_attribute  # Sensitive attribute for bias analysis

        if data is None:
            raise ValueError('The dataframe is None.')

        if label not in data.columns:
            raise ValueError('The label is not in the dataset.')

        if data[label].dtype in ['float64', 'float32'] and task_type == 'classification':
            raise ValueError('The target attribute is continuous (float) but the task is set to classification. '
                             'Consider binning the target or setting the task to regression.')

        if data[label].dtype == 'object' or data[label].dtype.name == 'bool' or data[label].dtype.name == 'category':
            if task_type == 'regression':
                raise TypeError('The target attribute is categorical and cannot be used for regression task.')

        if task_type == 'classification':
            label_encoder = LabelEncoder()
            self.label = label_encoder.fit_transform(data[label])
        else:
            self.label = data[label]

        # Detect and drop columns with long text
        long_text_columns = detect_text_columns(data, text_length_threshold)
        self.samples = data.drop(columns=long_text_columns + [label])

        model = self.preprocess(self.samples)
        self.split_dataset(data, label, ratio, fixed)
        self.train_and_test(model)

    def preprocess(self, data):
        d_copy = data.copy()
        numeric_features = d_copy.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = d_copy.select_dtypes(include=['object']).columns
        datetime_features = d_copy.select_dtypes(include=['datetime64']).columns
        for col in datetime_features:
            d_copy[col + '_year'] = d_copy[col].dt.year
            d_copy[col + '_month'] = d_copy[col].dt.month
            d_copy[col + '_day'] = d_copy[col].dt.day
            d_copy[col + '_hour'] = d_copy[col].dt.hour
            d_copy[col + '_weekday'] = d_copy[col].dt.weekday
            d_copy = d_copy.drop(columns=[col])  # Drop the original datetime column after extraction

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features),
            ],
            remainder='drop'  # This will drop any columns not specified in transformers (like datetime columns)
        )

        if self.task_type == 'classification':
            model = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('classifier', LogisticRegression())])
        else:
            model = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('regressor', SVR())])
        return model

    def split_dataset(self, data, label, ratio, fixed):
        if fixed:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                data.drop(label, axis=1), self.label, test_size=ratio, random_state=42)
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                data.drop(label, axis=1), self.label, test_size=ratio)

    def train_and_test(self, model):
        # Train the model
        model.fit(self.X_train, self.y_train)

        if self.task_type == 'classification':
            # Standard accuracy evaluation
            y_pred = model.predict(self.X_test)
            accuracy = accuracy_score(self.y_test, y_pred)
            print(f"Model Accuracy: {accuracy:.4f}")

            # If a sensitive attribute is defined, calculate disparity
            if self.sensitive_attribute:
                disparity_df = self.calculate_disparity(y_pred)
                print("\nDisparity Results:")
                print(disparity_df)

        else:
            # For regression
            y_pred = model.predict(self.X_test)
            mse = mean_squared_error(self.y_test, y_pred)
            print(f"Model Mean Squared Error: {mse:.4f}")

    def calculate_disparity(self, y_pred):
        """Calculate disparity (fairness) for multi-class classification results."""
        if self.sensitive_attribute not in self.X_test.columns:
            raise ValueError(f"Sensitive attribute '{self.sensitive_attribute}' is not in the dataset.")

        # Add the predicted class to the test set
        result_df = self.X_test.copy()
        result_df['predicted_class'] = y_pred

        # Get unique classes from the predicted labels
        unique_classes = result_df['predicted_class'].unique()

        # Calculate the rate of predictions for each class within each group
        parity_results = []
        disparity_scores = {}
        for cls in unique_classes:
            # Calculate the prediction rate for each group
            cls_df = result_df[result_df['predicted_class'] == cls]
            parity_df = cls_df.groupby(self.sensitive_attribute).size() / result_df.groupby(
                self.sensitive_attribute).size()
            parity_df = parity_df.rename(f'Class_{cls}')
            parity_results.append(parity_df)

            # Calculate disparity score (max - min prediction rate) for each class
            max_rate = parity_df.max()
            min_rate = parity_df.min()
            disparity_score = max_rate - min_rate
            disparity_scores[f'Class_{cls}'] = disparity_score

        # Combine results for each class into one DataFrame
        result_df = pd.concat(parity_results, axis=1).reset_index()

        # Display disparity scores
        for cls, score in disparity_scores.items():
            print(f"{cls}: Disparity Score = {score:.4f}")

        return result_df

    # def analyze_bias(self):
    #     # Check if the sensitive attribute exists in the dataset
    #     if self.sensitive_attribute not in self.X_test.columns:
    #         raise ValueError(f"Sensitive attribute '{self.sensitive_attribute}' is not in the dataset.")
    #
    #     # Ensure all categories are included in the analysis using the training set
    #     sensitive_categories = self.X_train[self.sensitive_attribute].unique()
    #
    #     # Group by the sensitive attribute and calculate the mean predicted probability
    #     grouped = self.X_test.groupby(self.sensitive_attribute)['predicted_prob'].mean()
    #
    #     print("\nAverage predicted probability by sensitive attribute:")
    #     for category in sensitive_categories:
    #         if category in grouped.index:
    #             print(f"{category}: {grouped[category]:.4f}")
    #         else:
    #             print(f"{category}: No data in test set")
    #
    #     # Collect predicted probabilities and actual values in a DataFrame for each group
    #     result_df = pd.DataFrame()
    #     for category in sensitive_categories:
    #         if category in self.X_test[self.sensitive_attribute].values:
    #             temp_df = self.X_test[self.X_test[self.sensitive_attribute] == category][
    #                 ['predicted_prob', 'actual']].copy()
    #             temp_df[self.sensitive_attribute] = category
    #             result_df = pd.concat([result_df, temp_df], axis=0)
    #         else:
    #             print(f"No data for {self.sensitive_attribute} '{category}' in the test set.")
    #
    #     return result_df

    # @staticmethod
    # def demographic_parity(results, protected_attr, predicted_label):
    #     # Get unique classes from the predicted labels
    #     classes = results[predicted_label].unique()
    #
    #     # Calculate the rate of predictions for each class within each group
    #     parity_results = []
    #     for cls in classes:
    #         cls_df = results[results[predicted_label] == cls]
    #         parity_df = cls_df.groupby(protected_attr).size() / results.groupby(protected_attr).size()
    #         parity_results.append(parity_df.rename(f'Class_{cls}_Prediction_Rate'))
    #
    #     # Combine the results into one DataFrame
    #     result_df = pd.concat(parity_results, axis=1).reset_index()
    #
    #     return result_df

    # Calculate Demographic Parity for multi-class classification




    # @staticmethod
    # def plot_density_curve(result_df, sensitive_attribute):
    #     """
    #     Plot the density curve of predicted probabilities by sensitive attribute using Plotly Figure Factory.
    #
    #     Parameters:
    #     - result_df: DataFrame returned by analyze_bias, containing predicted probabilities and sensitive attribute data.
    #     - sensitive_attribute: The name of the sensitive attribute used in the model.
    #     """
    #     if result_df.empty:
    #         raise ValueError("Resulting DataFrame is empty. Cannot plot density curve.")
    #
    #     # Separate the data by the sensitive attribute
    #     categories = result_df[sensitive_attribute].unique()
    #
    #     # Prepare data for each category
    #     hist_data = [result_df[result_df[sensitive_attribute] == category]['predicted_prob'].tolist() for category in
    #                  categories]
    #
    #     # Create the group labels for the legend
    #     group_labels = [f'{sensitive_attribute}: {category}' for category in categories]
    #
    #     # Create distplot with the histogram and KDE
    #     fig = ff.create_distplot(hist_data, group_labels, bin_size=0.01, show_hist=False, curve_type="kde", show_rug=False)
    #
    #     # Update layout
    #     fig.update_layout(
    #         title=f'Density of Predicted Probabilities by {sensitive_attribute.capitalize()}',
    #         xaxis_title='Predicted Probability',
    #         yaxis_title='Density',
    #         xaxis=dict(range=[0, 1]),  # Truncate the x-axis to [0, 1]
    #     )
    #
    #     # Display the plot
    #     fig.show()

    # Example usage:
    # result_df = de.analyze_bias()
    # plot_density_curve_plotly(result_df, de.sensitive_attribute)


# Test with a sample dataset
# testdata = {
#     'age': [25, 45, 35, 50, 34, 23, 23, 40, 30, 22, 48, 34, 35, 38, 45],
#     'income': [50000, 100000, 10000, 75000, 50000, 120000, 45000, 80000, 60000, 55000, 110000, 65000, 50000, 45000,
#                65665],
#     'gender': ['female', 'male', 'male', 'male', 'female', 'male', 'female', 'male', 'female', 'female', 'male',
#                'female', 'female', 'female', 'male'],
#     'purchased': [0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1]  # Target variable
# }
# df = pd.DataFrame(testdata)
df = pd.read_csv('../dataset/compas/compas-scores-two-years.csv')

# Instantiate DatasetEval with 'gender' as the sensitive attribute
de = DatasetEval(df, 'score_text', task_type='classification', sensitive_attribute='race')

# Example usage with plotting

