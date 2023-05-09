import copy
import csv
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.fft import fft, fftfreq

from .devices.base import BCISignal
from .utils import osum


class AbstractContainer(ABC):
    __slots__ = "channel_names", "signals", "sample_rate", "timestamps"

    def __init__(
            self,
            channel_names: List[str],
            sample_rate: int,
            signals: Union[List[List[float]], List[NDArray]],
            timestamps: Union[List[float], NDArray]) -> None:
        """Base class for all containers.

        :param channel_names: List of channel names.
        :type channel_names: List[str]
        :param sample_rate: Sample rate of the data.
        :type sample_rate: int
        :param signals: List of signals. Each signal is a list of floats.
        :type signals: Union[List[List[float]], List[NDArray]]
        :param timestamps: List of timestamps. Each timestamp is a float.
        :type timestamps: Union[List[float], NDArray]
        """
        self.channel_names = channel_names
        self.sample_rate = sample_rate
        self.signals = signals
        self.timestamps = timestamps

    @abstractmethod
    def average_ch(self, *channel_selection: Optional[List[str]]):
        """Create Container with an averaged channel. Operation is not performed in place.

        :param channel_selection: Specify channels to average. If None, returns Container with a signal channel, which is the average of all channels. Defaults to None
        :type channel_selection: Optional[List[str]], optional
        """
        pass

    @abstractmethod
    def average_sub_ch(
            self, *channel_selection: Optional[List[Union[Tuple[str], str]]]):
        """Create Container containing several averaged channels. Channels in the new Container are
        made up of specified channels. Each tuple results in one new averaged channel.
        E.g., the input ("TP9", "TP10"), ("AF9", "AF10") results in Container with two new channels. The first
        channel is the average of "TP9" and "TP10". If no channels are selected, averages all channels into one.

        :param channel_selection: Specify channels to average.
        :type channel_selection: Optional[List[Union[Tuple[str], str]]], optional.
        """
        pass

    def power_spectrum(self) -> List[NDArray]:
        """Calculates the power spectrum over all channels using
        Fast Fourier Transformation.

        :return: List containing real parts of frequency domain for each signal. The last entry in the returned list is a list containing the frequencies.
        :rtype: List[NDArray]
        """
        fin = []
        N = len(self)
        xf = fftfreq(N, 1 / self.sample_rate)[:N // 2]
        for ch in self.channel_names:
            yf = fft(self[ch])
            fin.append(2.0 / N * np.abs(yf[0:N // 2]))
        fin.append(xf)
        return fin

    def plot_ch(self, *channel_names: List[str]):
        """Plot stored channel data using matplotlib.

        :param channel_names: List of channel names to plot. If None, plots all channels. Defaults to None.
        :type channel_names: List[str]
        """
        max_val = 0
        if channel_names:
            for ch in channel_names:
                if ch not in self.channel_names:
                    raise Exception("Unknown channel can not be plotted.")
        else:
            channel_names = self.channel_names

        for ch in channel_names:
            plt.plot(self.timestamps, self[ch], label=ch)
            max_val = max(max_val, np.max(np.abs(self[ch])))
        plt.grid()
        plt.xlim([self.timestamps[0], self.timestamps[-1]])
        plt.ylim([-(max_val + 1), max_val + 1])
        plt.legend()
        plt.show()
        plt.close()

    def save_plot_ch(
            self,
            title: str,
            filename: str,
            *channel_names: List[str]):
        """Plot stored channel data using matplotlib and save to file.

        :param title: Title of the plot.
        :type title: str
        :param filename: Filename of the plot.
        :type filename: str
        :param channel_names: List of channel names to plot. If None, plots all channels. Defaults to None.
        :type channel_names: List[str], optional
        """
        max_val = 0
        if channel_names:
            for ch in channel_names:
                if ch not in self.channel_names:
                    raise Exception("Unknown channel can not be plotted.")
        else:
            channel_names = self.channel_names

        for ch in channel_names:
            plt.plot(self.timestamps, self[ch], label=ch)
            max_val = max(max_val, np.max(np.abs(self[ch])))
        plt.grid()
        plt.xlim([self.timestamps[0], self.timestamps[-1]])
        plt.ylim([-(max_val + 1), max_val + 1])
        plt.legend()
        plt.title(title)
        plt.savefig(filename, dpi=300)
        plt.close()

    def plot_ps(self):
        """Plot power spectrum using matplotlib.
        """
        ps = self.power_spectrum()
        for i in range(len(self.channel_names)):
            plt.plot(ps[-1], ps[i], label=self.channel_names[i])
        plt.title("Power Spectrum")
        plt.grid()
        plt.legend()
        plt.show()
        plt.close()

    def __getitem__(self, key):
        if type(key) not in [str, int]:
            raise Exception("Unsupported index type")

        if isinstance(key, int):
            if key >= len(self.channel_names) or key < 0:
                raise Exception("Index out of bound")
            key = self.channel_names[key]

        if key not in self.channel_names:
            raise Exception("No channel with that name")

        i = self.channel_names.index(key)
        return self.signals[i]

    def __setitem__(self, key, value):
        if type(key) not in [str, int]:
            raise Exception("Unsupported index type")

        if isinstance(key, int):
            if key >= len(self.channel_names) or key < 0:
                raise Exception("Index out of bound")
            key = self.channel_names[key]

        if key not in self.channel_names:
            raise Exception("No channel with that name")

        i = self.channel_names.index(key)
        self.signals[i] = value

    def __len__(self):
        if self.signals and len(self.signals) > 0:
            return len(self.signals[0])
        return 0


class EventContainer(AbstractContainer):
    def __init__(
            self,
            channel_names: List[str],
            sample_rate: int,
            signals: Union[List[List[float]], List[NDArray]],
            timestamps: Union[List[float], NDArray]) -> None:
        """Container for event data.

        :param channel_names: List of channel names.
        :type channel_names: List[str]
        :param sample_rate: Sample rate of the data.
        :type sample_rate: int
        :param signals: List of signals. Each signal is a list of floats.
        :type signals: Union[List[List[float]], List[NDArray]]
        :param timestamps: List of timestamps. Each timestamp is a float.
        :type timestamps: Union[List[float], NDArray]
        """
        if isinstance(signals[0], list):
            signals = [np.array(x) for x in signals]
        if isinstance(timestamps, list):
            timestamps = np.array(timestamps)
        super().__init__(channel_names, sample_rate, signals, timestamps)

    def average_ch(self, *channel_selection: Optional[List[str]]):
        """Create EventContainer with an averaged channel.

        :param channel_selection: Specify channels to average. If None, returns EventContainer with a signal channel, which is the average of all channels. Defaults to None
        :type channel_selection: Optional[List[str]], optional
        """
        if not channel_selection:
            new_channel_name = ["".join(self.channel_names)]
            new_signal = [osum(self.signals) / len(self.signals)]
        else:
            new_channel_name = ["".join(channel_selection)]
            selected_signals = [self[ch] for ch in channel_selection]
            new_signal = [osum(selected_signals) / len(selected_signals)]

        return EventContainer(
            new_channel_name,
            self.sample_rate,
            new_signal,
            np.copy(
                self.timestamps))

    def average_sub_ch(
            self, *channel_selection: Optional[List[Union[Tuple[str], str]]]):
        """Create EventContainer containing several averaged channels. Channels in the new EventContainer are
        made up of specified channels. Each tuple results in one new averaged channel.
        E.g., the input ("TP9", "TP10"), ("AF9", "AF10") results in EventContainer with two new channels. The first
        channel is the average of "TP9" and "TP10". If no channels are selected, averages all channels into one.

        :param channel_selection: Specify channels to average.
        :type channel_selection: Optional[List[Union[Tuple[str], str]]], optional.
        """
        if not len(channel_selection):
            return self.average_ch()

        new_channel_names = []
        new_signals = []

        for t in channel_selection:
            selection = t
            if not isinstance(t, tuple):
                selection = [t]
            selected_signals = [self[ch] for ch in selection]

            new_channel_names.append("".join(selection))
            new_signals.append(osum(selected_signals) / len(selected_signals))

        return EventContainer(
            new_channel_names,
            self.sample_rate,
            new_signals,
            np.copy(
                self.timestamps))

    def contains_blink(self, *channel_names) -> bool:
        """Checks if EventContainer contains a blink. This is done by
        checking if a threshold of 100 is reached. If True, signals
        in EventContainer include a blink.

        :param channel_names: Name of the channel for which the snr should be calculated.
        :type channel_names: *list, optional
        :return: True if blink is contained, False otherwise.
        :rtype: bool
        """
        if not channel_names:
            channel_names = self.channel_names

        for ch in self.channel_names:
            if np.abs(self[ch]).max() > 100:
                return True
        return False

    def snr(self, signal_range: Tuple[int, int] = (
            250, 400), use_absolutes: bool = False) -> dict:
        """Estimates the signal-to-noise ratio for a given channel by dividing the peak amplitude in the signal range by the standard deviation
        of the full eeg epoch. If the amplitude is expected to be negative, e.g., for a negative ERP amplitude, use_absolutes should be true.
        Returns the ratio.

        :param signal_range: Time range in which signal should appear. E.g. for for P300 250-400ms -> (250, 400)
        :type signal_range: Tuple[int, int]
        :param use_absolutes: If true, the absolute value of the signal is used to calculate the peak amplitude, defaults to False
        :type use_absolutes: bool, optional
        :return: Dictionary with channel names as keys and snr as values.
        :rtype: dict
        """
        def find_nearest(array, value):
            return int((np.abs(array - value)).argmin())

        def peak_amplitude(signal, start, stop):
            return np.max(np.abs(signal[start:stop])
                          if use_absolutes else signal[start:stop])

        start = find_nearest(self.timestamps, signal_range[0] / 1000)
        stop = find_nearest(self.timestamps, signal_range[1] / 1000)
        return {
            ch: peak_amplitude(
                self[ch],
                start,
                stop) /
            np.std(
                self[ch]) for ch in self.channel_names}

    def avg_snr(self, channel_names: list = None, signal_range: Tuple[int, int] = (
            250, 400), use_absolutes: bool = False) -> float:
        """Calculates the average snr over all channels in EventContainer. Returns the average snr.

        :param channel_names: List of channel names for which the snr should be calculated. If None, all channels are used.
        :type channel_names: list, defaults to None
        :param signal_range: Time range in which signal should appear. E.g. for P300 250-400ms -> (250, 400)
        :type signal_range: Tuple[int, int]
        :param use_absolutes: If true, the absolute value of the signal is used to calculate the peak amplitude, defaults to False, defaults to False
        :type use_absolutes: bool, optional
        :return: Average snr over all channels.
        :rtype: float
        """
        snr = self.snr(signal_range, use_absolutes)
        if not channel_names:
            channel_names = self.channel_names

        return np.mean([snr[ch] for ch in channel_names])

    def __add__(self, other):
        assert set(self.channel_names) == set(other.channel_names)
        assert len(self.signals[0]) == len(other.signals[0])
        assert self.sample_rate == other.sample_rate

        new_signals = [self[c] + other[c] for c in self.channel_names]

        return EventContainer(
            self.channel_names,
            self.sample_rate,
            new_signals,
            self.timestamps)

    def __truediv__(self, scalar: float):
        if scalar == 0:
            raise Exception("Can't divide by zero.")

        new_signals = [self[c] / scalar for c in self.channel_names]
        return EventContainer(
            self.channel_names,
            self.sample_rate,
            new_signals,
            self.timestamps)

    def __floordiv__(self, scalar: float):
        if scalar == 0:
            raise Exception("Can't divide by zero.")

        new_signals = [self[c] // scalar for c in self.channel_names]
        return EventContainer(
            self.channel_names,
            self.sample_rate,
            new_signals,
            self.timestamps)

    def __eq__(self, other):
        if self.channel_names != other.channel_names:
            return False

        if self.sample_rate != other.sample_rate:
            return False

        if not np.array_equal(self.timestamps, other.timestamps):
            return False

        if len(self.signals) != len(other.signals):
            return False

        for i in range(len(self.signals)):
            if not np.array_equal(self.signals[i], other.signals[i]):
                return False

        return True


class EEGContainer(AbstractContainer):
    __slots__ = "events"

    @classmethod
    def from_file(
            cls,
            channel_names: List[str],
            sample_rate: int,
            file: str,
            event_marker: str = "1"):
        """Create EEGContainer from data. Data is expected to be in the following format: <timestamp>, <channels>*n, <target marker?>

        :param channel_names: List of channel names.
        :type channel_names: List[str]
        :param sample_rate: Sample rate in Hz.
        :type sample_rate: int
        :param file: File containing data.
        :type file: str
        :param event_marker: Marker indicating the start of a new event. Defaults to "1".
        :type event_marker: str, optional
        """
        t = cls(channel_names, sample_rate)
        t.load_signals(file, event_marker=event_marker)
        return t

    def __init__(self, channel_names: List[str], sample_rate: int) -> None:
        """Create EEGContainer containing several channels. Channels are expected to be in the same order as signals added to the container.

        :param channel_names: List of channel names.
        :type channel_names: List[str]
        :param sample_rate: Sample rate in Hz.
        :type sample_rate: int
        """
        super().__init__(
            channel_names, sample_rate, [
                list() for _ in range(
                    len(channel_names))], [])
        self.events = []

    def add_data(self, rec: BCISignal):
        """Add new measured data point to the container. Data points consist of combinations of
        a time stamp and measured signals, and signals are expected to be in the same order as channels
        initially configured for the container.

        :param rec: Data point to add to the container.
        :type rec: BCISignal
        """
        if len(rec.signals) != len(self.channel_names):
            raise Exception(
                "Number of signals does not match number of channels provided")

        self.timestamps.append(rec.timestamp)
        for i in range(len(rec.signals)):
            self.signals[i].append(rec.signals[i])

    def add_event(
            self,
            event_time: int,
            before: int = 50,
            after: int = 100) -> EventContainer:
        """Adds an event to the recording. Returns EventContainer containing all data for added event.

        :param event_time: Time of event data in the container will be centered around.
        :type event_time: int
        :param before: Duration in milliseconds before the event to include in EventContainer, defaults to 50
        :type before: int
        :param after: Duration in milliseconds after the event to include in EventContainer, defaults to 100
        :type after: int
        :return: EventContainer containing all channels centered around event_time.
        :rtype: EventContainer
        """
        event = self.__find_closest_timestamp(event_time)
        event_time = self.timestamps[event]
        if event_time not in self.events:
            self.events.append(event_time)

        # Calculate number of samples before and after event
        before_samples = (before * self.sample_rate) // 1000
        before_samples = max(event - before_samples, 0)
        after_samples = (after * self.sample_rate) // 1000 + 1
        after_samples = min(event + after_samples, len(self.timestamps))

        # Create new timestamps and signals
        new_timestamps = np.array(
            self.timestamps[before_samples: after_samples])
        new_timestamps -= event_time
        new_signals = [np.array(x[before_samples: after_samples])
                       for x in self.signals]

        # Create new EventContainer
        return EventContainer(
            self.channel_names,
            self.sample_rate,
            new_signals,
            new_timestamps)

    def average_ch(self, *channel_selection: Optional[List[str]]):
        """Create EEGContainer with an averaged channel.

        :param channel_selection: Specify channels to average. If None, returns EEGContainer with a signal channel, which is the average of all channels. Defaults to None
        :type channel_selection: Optional[List[str]], optional
        """
        def s_osum(x):
            if len(x) == 0:
                return None
            if len(x) == 1:
                if isinstance(x[0], list):
                    return np.array(x[0])
                return x
            s = copy.deepcopy(x[0])
            for o in x[1:]:
                s = np.add(s, o)
            return s

        # If no channels are specified, average all channels
        if not channel_selection:
            # Average all channels
            new_channel_name = ["".join(self.channel_names)]
            new_signal = [s_osum(self.signals) / len(self.signals)]
        else:
            # Average specified channels
            new_channel_name = ["".join(channel_selection)]
            selected_signals = [self[ch] for ch in channel_selection]
            # Average signals
            new_signal = [s_osum(selected_signals) / len(selected_signals)]

        # Convert to list
        new_signal = [x.tolist() for x in new_signal]

        # Create new EEGContainer
        _t = EEGContainer(new_channel_name, self.sample_rate)
        _t.timestamps = copy.deepcopy(self.timestamps)
        _t.signals = new_signal

        return _t

    def average_sub_ch(
            self, *channel_selection: Optional[List[Union[Tuple[str], str]]]):
        """Create EEGContainer containing several averaged channels. Channels in the new EEGContainer are
        made up of specified channels. Each tuple results in one new averaged channel.
        E.g., the input ("TP9", "TP10"), ("AF9", "AF10") results in EEGContainer with two new channels. The first
        channel is the average of "TP9" and "TP10". If no channels are selected, averages all channels into one.

        :param channel_selection: Specify channels to average.
        :type channel_selection: Optional[List[Union[Tuple[str], str]]], optional.
        """
        def s_osum(x):
            if len(x) == 0:
                return None
            if len(x) == 1:
                if isinstance(x[0], list):
                    return np.array(x[0])
                return x
            s = copy.deepcopy(x[0])
            for o in x[1:]:
                s = np.add(s, o)
            return s

        if not len(channel_selection):
            return self.average_ch()

        new_channel_names = []
        new_signals = []

        for t in channel_selection:
            selection = t
            if not isinstance(t, tuple):
                selection = [t]
            selected_signals = [self[ch] for ch in selection]

            new_channel_names.append("".join(selection))
            new_signals.append(
                s_osum(selected_signals) /
                len(selected_signals))

        # Convert to list
        new_signals = [x.tolist() for x in new_signals]

        # Create new EEGContainer
        _t = EEGContainer(new_channel_names, self.sample_rate)
        _t.timestamps = copy.deepcopy(self.timestamps)
        _t.signals = new_signals

        return _t

    def get_all_events(self, before: int, after: int) -> List[EventContainer]:
        """Get EventContainer representation for all events stored in the container.

        :param before: Before duration.
        :type before: int
        :param after: After duration.
        :type after: int
        :return: List containing EventContainers for all stored events.
        :rtype: List[EventContainer]
        """
        return [self.add_event(x, before, after) for x in self.events]

    def load_signals(self, file_name: str, event_marker: str = "1"):
        """Load data from a csv file.
        The first col has to be the column with timestamps. Following this,
        the different channels must follow. The last column must contain either a 0, no
        target, or a 1, target.

        Channels are read in the same order as configured for the container. The additional channels are ignored if more channels
        are present than in the container.
        <timestamp>, <channels>*n, <target marker?>

        :param file_name: File name to read from.
        :type file_name: str
        """

        # Reset object before loading new signals
        self.timestamps = []
        self.signals = [list() for _ in range(len(self.channel_names))]

        with open(file_name) as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for line in reader:
                timestamp = float(line[0])
                signals = [float(x)
                           for x in line[1: len(self.channel_names) + 1]]

                if line[-1] == event_marker:
                    self.events.append(timestamp)
                self.add_data(BCISignal(timestamp, signals))

    def save_signals(self, file_name: str, event_marker: str = "1"):
        """Store data in csv format.

        :param file_name: File name to write to.
        :type file_name: str
        :param event_marker: Character to signify an event in saved data. Non-events always get marked with a 0.
        :type file_name: str
        """
        assert event_marker != "0"

        with open(file_name, "w", newline='') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["timestamps"] + self.channel_names + ["Marker"])

            for i in range(len(self.timestamps)):
                timestamp = self.timestamps[i]
                marker = 1 if timestamp in self.events else 0
                writer.writerow([timestamp] + [ch[i]
                                for ch in self.signals] + [marker])

    def shift_timestamps(self):
        """Shifts all timestamps to start at 0. This is useful if the EEGContainer is created
        from a file with a start time stamp != 0. Can also be used to anonymize data,i.e., by removing
        any information about the time of the recording. All events are shifted accordingly.
        """
        if len(self.timestamps) == 0:
            return

        first_timestamp = self.timestamps[0]
        self.timestamps = [x - first_timestamp for x in self.timestamps]
        self.events = [x - first_timestamp for x in self.events]

    def __find_closest_timestamp(self, timestamp: float) -> float:
        """Finds the index of the closest stored timestamp to provided time stamp.
        Ensures the event is always centered at 0.

        :param timestamp: External time stamp to search for in milliseconds.
        :type timestamp: float
        :return: Index of closest stored time stamp.
        :rtype: float
        """
        timestamp_arr = np.array(self.timestamps)
        return (np.abs(timestamp_arr - timestamp)).argmin()

    def __eq__(self, other):
        if self.channel_names != other.channel_names:
            return False

        if self.sample_rate != other.sample_rate:
            return False

        if self.timestamps != other.timestamps:
            return False

        if self.events != other.events:
            return False

        if len(self.signals) != len(other.signals):
            return False

        for i in range(len(self.signals)):
            if self.signals[i] != other.signals[i]:
                return False

        return True
