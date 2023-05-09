import unittest

import numpy as np

from neuropack.utils import normalize_npy, osum


class UtilTests(unittest.TestCase):
    def test_osum_1(self):
        self.assertEqual(osum(np.array([1, 2, 3, 4])), 10)

    def test_osum_2(self):
        # arrange
        array = [np.array([1, 2, 3, 4]), 2]

        # action
        calc_sum = osum(array)

        # check
        self.assertListEqual(
            np.array([3, 4, 5, 6]).tolist(), calc_sum.tolist())

    def test_normalize_npy_1(self):
        # arrange
        array = np.array([1, 2, 3, 4])

        # action
        calc_normalized = normalize_npy(array)

        # check, we need to use almost equal because of floating point
        # precision
        self.assertAlmostEqual(np.linalg.norm(calc_normalized), 1)

    def test_normalize_npy_2(self):
        # arrange
        array = np.array([-1, 2, 0.5, 4])

        # action
        calc_normalized = normalize_npy(array)

        # check, we need to use almost equal because of floating point
        # precision
        self.assertAlmostEqual(np.linalg.norm(calc_normalized), 1)
