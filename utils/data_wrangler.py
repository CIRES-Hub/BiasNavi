import pandas as pd
import numpy as np
import random


class DataWrangler:
    @staticmethod
    def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        for column in df.columns:
            # if pd.api.types.is_numeric_dtype(df[column]):
            #     # Fill numeric columns with the mean
            #     mean_value = df[column].mean()
            #     df[column] = df[column].fillna(mean_value)
            # else:
            # Fill non-numeric columns with a random value from the same column
            non_na_values = df[column].dropna().unique()
            if len(non_na_values) > 0:
                random_value = random.choice(non_na_values)
                df[column] = df[column].fillna(random_value)
            else:
                # If the column has no non-missing values to choose from
                df[column] = df[column].fillna('Unknown')
        return df

    @staticmethod
    def drop_rows_with_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna()