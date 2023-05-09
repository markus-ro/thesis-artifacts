from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar

import numpy as np
from numpy.typing import NDArray
from statsmodels.regression import yule_walker

from .container import EventContainer
from .utils import normalize_npy


class FeatureExtractionModelBase(ABC):
    def __init__(self) -> None:
        """Base class for feature extraction models."""
        super().__init__()

    @abstractmethod
    def extract_features(self, ev: EventContainer) -> NDArray:
        """Extract features from an EventContainer.

        :param ev: EventContainer to extract features from.
        :type ev: EventContainer
        :return: Features as a numpy array.
        :rtype: NDArray"""
        pass


class AverageModel(FeatureExtractionModelBase):
    __slots__ = "channels"

    def __init__(self, *channels: Optional[TypeVar]) -> None:
        """Average model. Returns the average of all channels. If channels are specified, only those channels are averaged. If no channels are specified, all channels are averaged.

        :param channels: List of channels to average.
        :type channels: Optional[List[str]]
        """
        self.channels = channels if channels else []
        super().__init__()

    def extract_features(self, ev: EventContainer) -> NDArray:
        """Extract features from an EventContainer. Features are: Average of all channels. If channels are specified, only those channels are averaged. If no channels are specified, all channels are averaged.

        :param ev: EventContainer to extract features from.
        :type ev: EventContainer
        :return: Features as a numpy array.
        :rtype: NDArray
        """
        t = ev.average_ch(*self.channels)
        return t[0]

    def __str__(self) -> str:
        return f"AverageModel()"


class BandpowerModel(FeatureExtractionModelBase):
    def __init__(self) -> None:
        """Model that extracts features from an EventContainer. Features are: power spectrum in the form of mean values for alpha and beta powerbands.
        """
        super().__init__()

    def aggregate_ps(self, power: NDArray, freqs: NDArray) -> List[float]:
        """Returns median for alpha and beta powerbands
        alpha [10-13Hz]
        beta [13-30Hz]

        :param power: Data points for each frequency.
        :type power: NDArray
        :param freqs: Frequency labels.
        :type freqs: NDArray
        :return: List of length 2, with the mean value for each power bands.
        Ordered as [<alpha>, <beta>]
        :rtype: List[int]
        """
        alpha = np.mean(np.sort(power[(freqs > 10) & (freqs <= 13)]))
        beta = np.mean(np.sort(power[(freqs > 13) & (freqs <= 30)]))

        return [alpha, beta]

    def extract_features(self, ev: EventContainer) -> NDArray:
        """Extract features from an EventContainer. Features are: power spectrum.

        :param ev: EventContainer to extract features from.
        :type ev: EventContainer
        :return: Features as a numpy array.
        :rtype: NDArray
        """
        features = []
        power_spectrum = ev.power_spectrum()
        for ch_ps in power_spectrum[:-1]:
            features.append(self.aggregate_ps(ch_ps, power_spectrum[-1]))

        return np.concatenate(features)

    def __str__(self) -> str:
        return f"BandpowerModel()"


class PACModel(FeatureExtractionModelBase):
    def __init__(self) -> None:
        """Model that extracts features from an EventContainer. Features are: power spectrum and AR coefficients. The AR coefficients are calculated for each channel. The power spectrum is calculated for each channel and aggregated to a single value for each power band. This model takes huge inspiration from the model described in "Performance and Usability Evaluation of Brainwave Authentication Techniques with Consumer Devices" by Arias-Cabarcos et al released in 2023.
        """
        super().__init__()

    def aggregate_ps(self, power: NDArray, freqs: NDArray) -> List[int]:
        """Returns median for detla, theta, alpha, and beta powerbands
        low [0-10Hz]
        alpha [10-13Hz]
        beta [13-30Hz]
        gamma [30-50Hz]

        :param power: Data points for each frequency.
        :type power: NDArray
        :param freqs: Frequency labels.
        :type freqs: NDArray
        :return: List of length 4, with the mean value for each power bands.
        Ordered as [<alpha>, <beta>]
        :rtype: List[int]
        """
        low = np.average(power[(freqs >= 0) & (freqs <= 10)])
        alpha = np.average(power[(freqs > 10) & (freqs <= 13)])
        beta = np.average(power[(freqs > 13) & (freqs <= 30)])
        gamma = np.average(power[(freqs > 30) & (freqs <= 50)])

        return [low, alpha, beta, gamma]

    def extract_features(self, ev: EventContainer) -> NDArray:
        """Extract features from an EventContainer. Features are: power spectrum and AR coefficients. The AR coefficients are calculated for each channel. The power spectrum is calculated for each channel and aggregated to a single value for each power band.

        :param ev: EventContainer to extract features from.
        :type ev: EventContainer
        :return: Features as a numpy array.
        :rtype: NDArray
        """
        features = []
        power_spectrum = ev.power_spectrum()

        # Calculate features for each channel
        for i in range(len(ev.signals)):
            # Extract power spectrum for channel
            features.append(self.aggregate_ps(
                power_spectrum[i], power_spectrum[-1]))

            # Calculate AR coefficients
            rho, sigma = yule_walker(
                ev[i], order=10, method="mle")
            features.append(rho)

        # Concatenate features, and return normalized features
        return np.concatenate(features)

    def __str__(self) -> str:
        return f"PACModel()"


class AdaptedPACModel(FeatureExtractionModelBase):
    __slots__ = "num_coefficients"

    def __init__(self, num_coefficients: int = 10) -> None:
        """Model that extracts features from an EventContainer. Features are: power spectrum and AR coefficients. The AR coefficients are calculated for each channel. The power spectrum is calculated for each channel and aggregated to a single value for each power band. Further, it is normalized and contains frequencies in the ranges of [0-10Hz], [10-13Hz], [13-30Hz], and [30-50Hz]. Model is adaption from PACModel, which does not normalize the power spectrum, thereby introducing values which are too large for usefull similarity calculation using classic distance metrics.

        :param num_coefficients: _description_, defaults to 10
        :type num_coefficients: int, optional
        """
        self.num_coefficients = num_coefficients
        super().__init__()

    def aggregate_ps(self, power: NDArray, freqs: NDArray) -> List[int]:
        """Returns aggregated value for each power band.
        low [0-10Hz]
        alpha [10-13Hz]
        beta [13-30Hz]
        gamma [30-50Hz]

        :param power: Data points for each frequency.
        :type power: NDArray
        :param y: Frequency labels.
        :type y: NDArray
        :return: Normalized list of length 4, with aggregated value for each power bands.
        Ordered as [<delta>, <theta>, <alpha>, <beta>]
        :rtype: List[int]
        """
        low = np.average(power[(freqs >= 0) & (freqs <= 10)])
        alpha = np.average(power[(freqs > 10) & (freqs <= 13)])
        beta = np.average(power[(freqs > 13) & (freqs <= 30)])
        gamma = np.average(power[(freqs > 30) & (freqs <= 50)])

        concat = np.array([low, alpha, beta, gamma])

        return normalize_npy(concat)

    def extract_features(self, ev: EventContainer) -> NDArray:
        """Extract features from an EventContainer. Features are: AR coefficients, power spectrum.

        :param ev: EventContainer to extract features from.
        :type ev: EventContainer
        :return: Features as a numpy array.
        :rtype: NDArray
        """
        # Extract AR coefficients
        features = []
        for sig in ev.signals:
            rho, sigma = yule_walker(
                sig, order=self.num_coefficients, method="mle")
            features.append(rho)

        # Extract power spectrum
        power_spectrum = ev.power_spectrum()
        for ch_ps in power_spectrum[:-1]:
            features.append(self.aggregate_ps(ch_ps, power_spectrum[-1]))

        # Concatenate features
        return np.concatenate(features)

    def __str__(self) -> str:
        return f"AdaptedPACModel(num_coefficients={self.num_coefficients})"
