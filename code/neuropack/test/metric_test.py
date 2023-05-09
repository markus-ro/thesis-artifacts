import unittest

import numpy as np

from neuropack.benchmarking import FNR, FPR, TNR, TPR


class MetricTests(unittest.TestCase):
    def test_FPR_1(self):
        self.assertEqual(FPR(np.array([0.8, 0.9, 0.7, 0.6]), 0.75), 0.5)

    def test_FPR_2(self):
        self.assertEqual(FPR(np.array([0.6, 0.6, 0.6, 0.6]), 0.75), 0)

    def test_FPR_3(self):
        self.assertEqual(FPR(np.array([0.8, 0.9, 0.7, 0.6]), 0.5), 1)

    def test_FNR_1(self):
        self.assertEqual(FNR(np.array([0.8, 0.9, 0.7, 0.6]), 0.75), 0.5)

    def test_FNR_2(self):
        self.assertEqual(FNR(np.array([0.6, 0.6, 0.6, 0.6]), 0.75), 1)

    def test_FNR_3(self):
        self.assertEqual(FNR(np.array([0.8, 0.9, 0.7, 0.6]), 0.5), 0)

    def test_TPR_1(self):
        self.assertEqual(TPR(np.array([0.8, 0.9, 0.7, 0.6]), 0.75), 0.5)

    def test_TPR_2(self):
        self.assertEqual(TPR(np.array([0.6, 0.6, 0.6, 0.6]), 0.75), 0)

    def test_TPR_3(self):
        self.assertEqual(TPR(np.array([0.8, 0.9, 0.7, 0.6]), 0.5), 1)

    def test_TNR_1(self):
        self.assertEqual(TNR(np.array([0.8, 0.9, 0.7, 0.6]), 0.75), 0.5)

    def test_TNR_2(self):
        self.assertEqual(TNR(np.array([0.6, 0.6, 0.6, 0.6]), 0.75), 1)
