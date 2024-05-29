import pandas as pd
import json

class Dataset:
    def __init__(self, filepath=None, metadata_path=None):
        self.filepath = filepath
        self.metadata_path = metadata_path
        self.dataframe = None
        self.metadata = {}
        self.sensitive_attributes = []

    def load(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        if self.filepath is None:
            raise ValueError("Filepath must be provided for loading the dataset.")
        self.dataframe = pd.read_csv(self.filepath)

    def save(self, filepath=None):
        if self.dataframe is None:
            raise ValueError("There is no dataset to save.")
        if filepath is not None:
            self.filepath = filepath
        if self.filepath is None:
            raise ValueError("Filepath must be provided for saving the dataset.")
        self.dataframe.to_csv(self.filepath, index=False)

    def load_metadata(self, metadata_path=None):
        """
        Load metadata from a JSON file.

        :param metadata_path: str, optional
            Path to the JSON file to load metadata. If not specified, tries to use the metadata_path provided during initialization.
        """
        if metadata_path is not None:
            self.metadata_path = metadata_path
        if self.metadata_path is None:
            raise ValueError("Metadata path must be provided for loading metadata.")
        with open(self.metadata_path, 'r') as file:
            self.metadata = json.load(file)

    def get_metadata(self):
        """
        Returns the metadata.

        :return: dict
            The loaded metadata.
        """
        return self.metadata

    def set_sensitive_attributes(self, attributes):
        """
        Set the list of sensitive attributes.

        :param attributes: list
            A list of strings representing the sensitive attributes in the dataset.
        """
        if not isinstance(attributes, list):
            raise ValueError("Sensitive attributes must be provided as a list.")
        self.sensitive_attributes = attributes

    def get_dataframe(self):
        return self.dataframe
