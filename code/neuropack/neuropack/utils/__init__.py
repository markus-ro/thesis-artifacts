from copy import deepcopy
from typing import Any, List, Tuple, Union

import numpy as np
from numpy.typing import NDArray


def osum(collection: Union[List[Any], Tuple[Any]]) -> Any:
    """Allows sum operation over any collection.
    In contrast to build-in sum works with things
    other than numbers. For example, it can sum up lists.

    :param collection: Collection to sum up.
    :type collection: Union[List[Any], Tuple[Any]]
    """
    if len(collection) == 0:
        return None
    s = deepcopy(collection[0])
    for o in collection[1:]:
        s += o
    return s


def oavg(collection: Union[List[Any], Tuple[Any]]) -> Any:
    """Allows average operation over any collection.

    :param collection: Collection to average.
    :type collection: Union[List[Any], Tuple[Any]]
    """
    if len(collection) == 0:
        return None
    return osum(collection) / len(collection)


def normalize_npy(array: NDArray) -> NDArray:
    """Returns normalized representation of 1D numpy array. Normalization is done by dividing each element by the length of the array. The length is calculated as a square root of the sum of squares of all elements. The result is a vector with the same direction, but with length equal to 1. This is useful for calculating angles between vectors.

    :param array: Numpy array to normalize.
    :type array: NDArray
    :return: Normalized array.
    :rtype: NDArray
    """
    length = (array**2).sum()**0.5
    return array / length
