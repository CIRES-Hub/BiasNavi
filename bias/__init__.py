from sklearn.metrics import confusion_matrix
import numpy as np

class FairnessMetric:
    def __init__(self, sensitive_attr):
        """
        Initialize the FairnessMetric class with a sensitive attribute.

        :param sensitive_attr: array-like
            List or array of the sensitive attribute values (e.g., race or gender).
        """
        self.sensitive_attr = np.array(sensitive_attr)

    def demographic_parity_difference(self, y_true, y_pred):
        """
        Calculate the Demographic Parity Difference.

        :param y_true: array-like
            True labels.
        :param y_pred: array-like
            Predicted labels.
        :return: float
            The difference in probabilities of positive predictions between the groups.
        """
        y_pred = np.array(y_pred)
        group_1_mask = self.sensitive_attr == 1
        group_0_mask = self.sensitive_attr == 0

        prob_pos_group_1 = np.mean(y_pred[group_1_mask] == 1)
        prob_pos_group_0 = np.mean(y_pred[group_0_mask] == 1)

        return prob_pos_group_1 - prob_pos_group_0

    def equal_opportunity_difference(self, y_true, y_pred):
        """
        Calculate the Equal Opportunity Difference.

        :param y_true: array-like
            True labels.
        :param y_pred: array-like
            Predicted labels.
        :return: float
            The difference in true positive rates between the groups.
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        group_1_mask = (self.sensitive_attr == 1) & (y_true == 1)
        group_0_mask = (self.sensitive_attr == 0) & (y_true == 1)

        tpr_group_1 = np.mean(y_pred[group_1_mask] == 1)
        tpr_group_0 = np.mean(y_pred[group_0_mask] == 1)

        return tpr_group_1 - tpr_group_0
