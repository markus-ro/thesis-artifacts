import matplotlib.pyplot as plt
from typing import List

from .metrics import auc


def plot_roc(fpr: List[float], tpr: List[float], title="ROC Curve"):
    """Plot ROC curve for a given FPR and TPR.

    :param fpr: False Positive Rate
    :type fpr: List[float]
    :param tpr: True Positive Rate
    :type tpr: List[float]
    :param title: Title of the plot, defaults to "ROC Curve"
    :type title: str, optional
    """
    plt.figure()
    plt.grid()
    plt.title(title)
    plt.xlabel("False Positive Rate (FPR)")
    plt.ylabel("True Positiv Rate (TPR)")
    plt.plot(fpr, tpr, label="(AUC = {0:.2f})".format(auc(fpr, tpr)))
    plt.legend()
    plt.axline((0, 0), slope=1, linestyle='--', color='r')
    # Limit viewing area
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.show()
