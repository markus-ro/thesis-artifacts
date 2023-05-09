from typing import Callable, List, Tuple

import numpy as np
from numpy.typing import NDArray


def TPR(p_sims: NDArray, t: float) -> float:
    """Calculate the True Positive Rate for a given threshold and array of similarities. All similarities are assumed to be for
    positive samples. Note: True Positive Rate, True Acceptance Rate, and True Match Rate are the same.
    TPR = TP / (TP + FN) = TP / len(p_sims)

    :param p_sims: Similarity scores for positive samples.
    :type p_sims: NDArray
    :param t: Acceptance threshold.
    :type t: float
    :return: True Positive Rate.
    :rtype: float
    """
    TP = (p_sims >= t).sum()
    return TP / len(p_sims)


def FPR(n_sims: NDArray, t: float) -> float:
    """Calculate the False Positive Rate for a given threshold and array of similarities. All similarities are assumed to be for
    negative samples. Note: False Positive Rate, False Acceptance Rate, and False Match Rate are the same.
    FPR = FP / (FP + TN) = FP / len(n_sims)

    :param n_sims: Similarity scores for negative samples.
    :type n_sims: NDArray
    :param t: Acceptance threshold.
    :type t: float
    :return: False Positive Rate.
    :rtype: float
    """
    FP = (n_sims >= t).sum()
    return FP / len(n_sims)


def FNR(p_sims: NDArray, t: float) -> float:
    """Calculate the False Rejection Rate for a given threshold and array of similarities. All similarities are assumed to be for
    positive samples. False Negative Rate, False Rejection Rate, and False Non Match Rate are the same.
    FNR = FN / (FN + TP) = FN / len(p_sims)

    :param p_sims: Similarity scores for positive samples.
    :type p_sims: NDArray
    :param t: Acceptance threshold.
    :type t: float
    :return: False Negative Rate.
    :rtype: float
    """
    FN = (p_sims < t).sum()
    return FN / len(p_sims)


def TNR(n_sims: NDArray, t: float) -> float:
    """Calculate the True Negative Rate for a given threshold and array of similarities. All similarities are assumed to be for
    negative samples. True Negative Rate, True Rejection Rate, and True Non Match Rate are the same.
    TNR = TN / (TN + FP) = TN / len(n_sims)

    :param n_sims: Similarity scores for negative samples.
    :type n_sims: NDArray
    :param t: Acceptance threshold.
    :type t: float
    :return: True Negative Rate.
    :rtype: float
    """
    TN = (n_sims < t).sum()
    return TN / len(n_sims)


def confustion_matrix(p_sims: NDArray, n_sims: NDArray,
                      t: float) -> Tuple[int, int, int, int]:
    """Calculates the confusion matrix for a given acceptance threshold. All similarities are assumed to be for
    positive and negative samples. The confusion matrix is returned as a tuple: (TP, FP, FN, TN).

    :param p_sims: Similarity scores for positive samples.
    :type p_sims: NDArray
    :param n_sims: Similarity scores for negative samples.
    :type n_sims: NDArray
    :param t: Acceptance threshold.
    :type t: float
    :return: Confusion matrix as a tuple: (TP, FP, FN, TN).
    :rtype: Tuple[int, int, int, int]
    """
    TP = (p_sims >= t).sum()
    FP = (n_sims >= t).sum()
    FN = (p_sims < t).sum()
    TN = (n_sims < t).sum()
    return TP, FP, FN, TN


def roc(p: NDArray, n: NDArray,
        res: int = 100) -> Tuple[NDArray, NDArray, NDArray]:
    """Calculates the Receiver Operating Characteristic (ROC) curve for given sets of similarities scores for positive and negative samples.
    The TPR and FPR for every threshold are calculated and returned. The threshold resolution is determined by the res parameter.
    The res parameter is the number of values between 0 and 1 that will be used to calculate the TPR and FPR. The higher the resolution,
    the more accurate the curve will be. However, the higher the resolution, the longer it will take to calculate. The default resolution is 100.
    The resolution should be set to the highest possible value that will not cause the function to take too long to run.

    :param p: Similarity scores of positive samples
    :type p: NDArray
    :param n: Similarity scores of negative samples
    :type n: NDArray
    :param res: threshold resolution or number of values between 0 and 1, defaults to 100
    :type res: int, optional
    :return: False positive rate, true positive rate, and thresholds
    :rtype: Tuple[NDArray, NDArray, NDArray]
    """
    # Make sure to cover all thresholds found in provided dataset
    # max_sim = max(np.max(p), np.max(n)) + 1  # upper bound for threshold
    # min_sim = min(np.min(p), np.min(n))
    max_sim = 1
    min_sim = 0

    thresholds = np.linspace(min_sim, max_sim, res)
    _fpr = np.zeros(len(thresholds))
    _tpr = np.zeros(len(thresholds))
    for i in range(len(thresholds)):
        _fpr[i] = FPR(n, thresholds[i])
        _tpr[i] = TPR(p, thresholds[i])

    return _fpr, _tpr, thresholds


def calc_roc(template: NDArray, p: List[NDArray], n: List[NDArray], sim_func: Callable[[
             NDArray, NDArray], float], res: int = 100) -> Tuple[NDArray, NDArray, NDArray]:
    """Calculates the Receiver Operating Characteristic (ROC) curve for a given template, similarity function, and set of positive/negative samples.
    The positive and negative samples are first compared against the template using the similarity metric, and the resulting similarities are stored.
    Following this, the TPR and FPR for every threshold are calculated and returned.

    :param template: Template used to determine the similarity of both positive and negative samples
    :type template: NDArray
    :param p: List of positive samples in the form of numerical arrays
    :type p: List[NDArray]
    :param n: List of negative samples in the form of numerical arrays
    :type n: List[NDArray]
    :param sim_func: Similarity function used to determine similarity, must project between 0 = no similarity and 1 = equal
    :type sim_func: Callable[[NDArray, NDArray], float]
    :param res: Threshold resolution or number of values between 0 and 1, defaults to 100
    :type res: int, optional
    :return: false positive rate, true positive rate, and thresholds
    :rtype: Tuple[NDArray, NDArray, NDArray]
    """
    p_similarities = np.array([sim_func(template, i) for i in p])
    n_similarities = np.array([sim_func(template, i) for i in n])
    return roc(p_similarities, n_similarities, res=res)


def auc(fpr: NDArray, tpr: NDArray):
    """Approximate the Area Under Curve using the False Positive Rate and True Positive Rate
    produced using the Receiver Operating Characteristic Curve.
    The approximation is done using the trapeziodal rule.

    :param fpr: False positive rate calculated through ROC
    :type fpr: NDArray
    :param tpr: True positiv rate through ROC
    :type tpr: NDArray
    """
    # Make sure the arrays are sorted in ascending order
    correction = -1
    if np.all(np.diff(fpr) >= 0):
        correction = 1

    # Calculate the area under the curve
    return correction * np.trapz(tpr, fpr)


def calc_eer(p: NDArray, n: NDArray, res: int = 100) -> Tuple[float, float]:
    """Approximates the Equal Error Rate for a given set of positive and negative samples.
    First, calculates the ROC curve based on the given positive and negative samples. Following this,
    the similarities are used to approximate a threshold in which both the false positive rate
    and the false negative rate are equal.

    :param p: Similarity scores of positive samples
    :type p: NDArray
    :param n: Similarity scores of negative samples
    :type n: NDArray
    :param res: Threshold resolution or number of values between 0 and 1, defaults to 100
    :type res: int, optional
    :return: False negative rate, Threshold at which fnr and fpr are equal
    :rtype: Tuple[float, float]
    """
    _fpr, _tpr, _t = roc(p, n, res=res)
    _fnr = 1 - _tpr

    i = np.argmin(np.abs(_fpr - _fnr))
    return _fnr[i], _t[i]


def eer(fpr, tpr) -> float:
    """Calculates the equal error rate (EER) of the given FPR and TPR.
    The EER is the point on the ROC curve where the false positive rate
    and false negative rate are equal.

    :param fpr: False positive rate
    :type fpr: NDArray
    :param tpr: True positive rate
    :type tpr: NDArray
    :return: Equal error rate
    :rtype: float"""
    fnr = 1 - tpr
    eer = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
    return eer
