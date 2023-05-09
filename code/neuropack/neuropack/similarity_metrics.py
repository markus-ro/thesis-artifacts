import numpy as np
from numpy.typing import NDArray
from scipy.signal import correlate


def cosine_similarity(x: NDArray, y: NDArray) -> float:
    """Calculates the cosine similarity between two signals. The cosine similarity is defined as the dot product of the two signals divided by the product of their norms.

    :param x: First signal.
    :type x: NDArray
    :param y: Second signal.
    :type y: NDArray
    :return: Similarity between the two signals, in the range of [-1, 1].
    :rtype: float
    """
    if np.array_equal(x, y):
        return 1.0
    x_norm = np.linalg.norm(x)
    y_norm = np.linalg.norm(y)

    if x_norm == 0 or y_norm == 0:
        return 0

    return np.dot(x, y) / (x_norm * y_norm)


def bounded_cosine_similarity(x: NDArray, y: NDArray) -> float:
    """Bounded cosine similarity. The bounded cosine similarity is defined as the cosine similarity between the two signals plus 1, divided by 2. This is done to ensure that the similarity is in the range of [0, 1].

    :param x: First signal.
    :type x: NDArray
    :param y: Second signal.
    :type y: NDArray
    :return: Similarity between the two signals, in the range of [0, 1].
    :rtype: float
    """
    if np.array_equal(x, y):
        return 1.0
    x_norm = np.linalg.norm(x)
    y_norm = np.linalg.norm(y)

    if x_norm == 0 or y_norm == 0:
        return 0

    cos = np.dot(x, y) / (x_norm * y_norm)

    return (1 + cos) / 2


def euclidean_similarity(x: NDArray, y: NDArray) -> float:
    """Calculates the euclidean similarity between two signals. The euclidean similarity is defined as 1 / (1 + euclidean distance).

    :param x: First signal.
    :type x: NDArray
    :param y: Second signal.
    :type y: NDArray
    :return: Similarity between the two signals, in the range of [0, 1].
    :rtype: float"""
    distance = np.linalg.norm(x - y)
    return 1 / (1 + distance)
