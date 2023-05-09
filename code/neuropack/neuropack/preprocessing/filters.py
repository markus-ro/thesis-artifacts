from abc import ABC, abstractclassmethod
from typing import Union

import numpy as np
from scipy.signal import butter, detrend, filtfilt, iirnotch, sosfiltfilt

from ..container import AbstractContainer, EventContainer


class FilterBase(ABC):
    @abstractclassmethod
    def apply(self, data: EventContainer) -> None:
        pass


class DetrendFilter(FilterBase):
    def __init__(self) -> None:
        """Detrend filter. Removes linear trend from data. Uses scipy.signal.detrend. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.detrend.html for more information."""
        super().__init__()

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        for c in data.channel_names:
            t = detrend(data[c])
            if isinstance(data[c], list):
                data[c] = t.tolist()
            else:
                data[c] = t

    def __str__(self) -> str:
        return f"DetrendFilter()"


class HighpassFilter(FilterBase):
    def __init__(self, cutoff: float, sample_rate: int) -> None:
        """Highpass filter. Removes low frequency components from data. Uses scipy.signal.butter. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html for more information.

        :param cutoff: Frequency cutoff. Frequencies below this value are removed.
        :type cutoff: float
        :param sample_rate: Sample rate of the data.
        :type sample_rate: int
        """
        super().__init__()
        self._cutoff = cutoff
        self.sos = butter(
            5,
            cutoff,
            "high",
            fs=sample_rate,
            analog=False,
            output="sos")

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        for c in data.channel_names:
            t = sosfiltfilt(self.sos, data[c])
            if isinstance(data[c], list):
                data[c] = t.tolist()
            else:
                data[c] = t

    def __str__(self) -> str:
        return f"HighpassFilter(cutoff={self._cutoff})"


class LowpassFilter(FilterBase):
    def __init__(self, cutoff: float, sample_rate: int) -> None:
        """Lowpass filter. Removes high frequency components from data. Uses scipy.signal.butter. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html for more information.

        :param cutoff: Frequency cutoff. Frequencies above this value are removed.
        :type cutoff: float
        :param sample_rate: Sample rate of the data.
        :type sample_rate: int
        """
        super().__init__()
        self._cutoff = cutoff
        self.sos = butter(
            5,
            cutoff,
            "low",
            fs=sample_rate,
            analog=False,
            output="sos")

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        for c in data.channel_names:
            t = sosfiltfilt(self.sos, data[c])
            if isinstance(data[c], list):
                data[c] = t.tolist()
            else:
                data[c] = t

    def __str__(self) -> str:
        return f"LowpassFilter(cutoff={self._cutoff})"


class BandpassFilter(FilterBase):
    def __init__(self, low=0.1, high=30, sample_rate=256) -> None:
        """Bandpass filter. Removes low and high frequency components from data. Uses LowpassFilter and HighpassFilter.

        :param low: Low cutoff frequency. Frequencies below this value are removed. Defaults to 0.1.
        :type low: float, optional
        :param high: High cutoff frequency. Frequencies above this value are removed. Defaults to 30.
        :type high: int, optional
        :param sample_rate: Sample rate of the data. Defaults to 256.
        :type sample_rate: int, optional
        """
        super().__init__()
        self.low_pass = LowpassFilter(high, sample_rate)
        self.high_pass = HighpassFilter(low, sample_rate)

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        self.low_pass.apply(data)
        self.high_pass.apply(data)

    def __str__(self) -> str:
        return f"BandpassFilter({str(self.low_pass)}, {str(self.high_pass)})"


class NotchFilter(FilterBase):
    def __init__(self, notch=50, sample_rate=256, quality_factor=30) -> None:
        super().__init__()
        self._notch = notch
        self._quality_factor = quality_factor
        self.b, self.a = iirnotch(notch, quality_factor, sample_rate)

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        for c in data.channel_names:
            t = filtfilt(self.b, self.a, data[c])
            if isinstance(data[c], list):
                data[c] = t.tolist()
            else:
                data[c] = t

    def __str__(self) -> str:
        return f"NotchFilter(notch={self._notch}, quality_factor={self._quality_factor})"


class BaselineCorrectionFilter(FilterBase):
    def apply(self, data: EventContainer) -> None:
        """Apply the filter to an EventContainer. The filter is applied to all channels in the EventContainer. The filter is applied in-place. The baseline is calculated as the average of the data before the stimulus.

        :param data: Container to apply the filter to.
        :type data: EventContainer
        """
        stim_i = np.where(data.timestamps == 0)[0][0]
        for channel in data.channel_names:
            avg = sum(data[channel][0:stim_i]) / stim_i
            data[channel] -= avg

    def __str__(self) -> str:
        return f"BaselineCorrectionFilter()"


class ReductionFilter(FilterBase):
    def __init__(self, *channel_selection) -> None:
        """Reduce channels found in event. Can be used to either combine several signals or to leave signals out.
        E.g., the input ("TP9", "TP10"), ("AF9", "AF10") results in two new channels. The first
        channel is the average of "TP9" and "TP10". If no channels are selected, averages all channels into one.

        :param channel_selection: Specify channels to average.
        :type channel_selection: Optional[List[Union[Tuple[str], str]]], optional.
        """
        super().__init__()
        self.channel_selection = list(channel_selection)

    def apply(self, data: AbstractContainer) -> None:
        """Apply the filter to an AbstractContainer. The filter is applied to all channels in the AbstractContainer. The filter is applied in-place.

        :param data: Container to apply the filter to.
        :type data: AbstractContainer
        """
        new = data.average_sub_ch(*self.channel_selection)
        data.channel_names = new.channel_names
        data.signals = new.signals

    def __str__(self) -> str:
        str_selection = str(self.channel_selection)
        return f"ChannelReduction(selection={str_selection})"
