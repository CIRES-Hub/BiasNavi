from dataset import Dataset  # Assuming your previous class is saved as dataset.py
from pkg_resources import resource_filename

# Global variable for the path to the COMPAS dataset CSV file
COMPAS_PATH = resource_filename(__name__,'compas-scores-two-years.csv')

class COMPASDataset(Dataset):
    def __init__(self):
        # Use the global COMPAS_PATH for initializing the superclass
        super().__init__(filepath=COMPAS_PATH)
        self.load()  # Automatically load the dataset
        self.set_sensitive_attributes(['race', 'sex'])
        # Optionally, load metadata if applicable
