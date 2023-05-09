import sys
import unittest

import numpy as np

from neuropack import similarity_metrics

sys.path.append("../")


class SimilarityMetricsTests(unittest.TestCase):
    def test_euclidean_similarity(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        expected = 1 / (1 + np.sqrt(27))

        # action
        result = similarity_metrics.euclidean_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_euclidean_similarity_with_zero(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([0, 0, 0])
        expected = 1 / (1 + np.sqrt(14))

        # action
        result = similarity_metrics.euclidean_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_eucledian_similarity_with_equal(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        expected = 1

        # action
        result = similarity_metrics.euclidean_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_euclidean_similarity_with_almost_equal(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([1.1, 2.1, 3.1])
        expected = 1 / (1 + np.sqrt(0.03))

        # action
        result = similarity_metrics.euclidean_similarity(a, b)

        # check, we use assertAlmostEqual because of floating point errors
        self.assertAlmostEqual(result, expected, delta=0.05)

    def test_cosine_similarity(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        expected = 32 / (np.sqrt(14) * np.sqrt(77))

        # action
        result = similarity_metrics.cosine_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_cosine_similarity_with_zero(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([0, 0, 0])
        expected = 0

        # action
        result = similarity_metrics.cosine_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_cosine_similarity_with_equal(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        expected = 1

        # action
        result = similarity_metrics.cosine_similarity(a, b)

        # check
        self.assertEqual(result, expected)

    def test_cosine_similarity_with_almost_equal(self):
        # arrange
        a = np.array([1, 2, 3])
        b = np.array([1.1, 2.1, 3.1])
        expected = 32 / (np.sqrt(14) * np.sqrt(77))

        # action
        result = similarity_metrics.cosine_similarity(a, b)

        # check, we need to use assertAlmostEqual because of floating point
        # errors
        self.assertAlmostEqual(result, expected, delta=0.05)
