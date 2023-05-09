import math
import sys
import tempfile
import unittest
from os import path
from random import randint

import numpy as np

from neuropack.container import EEGContainer
from neuropack.devices.base import BCISignal

sys.path.append("../")


class EEGContainerTests(unittest.TestCase):
    def test_add_values(self):
        """Check, that new EEG signals are correctly added to EEGContainer.
        """
        container = EEGContainer(["Ch1", "Ch2"], 256)
        container.add_data(BCISignal(0, [0.1, 0.2]))

        self.assertEqual(container["Ch1"][0], 0.1,
                         "Value was not added as expected")
        self.assertEqual(container["Ch2"][0], 0.2,
                         "Value was not added as expected")

        container.add_data(BCISignal(0, [0.2, 0.1]))

        self.assertEqual(container["Ch1"][1], 0.2,
                         "Value was not added as expected")
        self.assertEqual(container["Ch2"][1], 0.1,
                         "Value was not added as expected")

    def test_wrong_channels(self):
        # arrange
        container = EEGContainer(["Ch1", "Ch2"], 256)
        exception_raised = False

        # action
        try:
            container.add_data(BCISignal(0, [0.1, 0.2, 0.3]))
        except BaseException:
            exception_raised = True

        # check
        self.assertTrue(exception_raised,
                        "No exception was raised despite wrong data.")

    def test_event_data(self):
        """Check, that creating events works as intended.
        """
        # arrange
        container = EEGContainer(["Ch1"], 250)
        signal = [math.sin(x) for x in range(250)]
        timestamps = [x * 4 for x in range(250)]
        event_time_stamp = 500
        signal[125] = 100
        for i in range(250):
            container.add_data(BCISignal(timestamps[i], [signal[i]]))

        # action
        event = container.add_event(event_time_stamp, 250, 250)

        # check
        self.assertEqual(
            len(event.signals[0]), 125, "Expected exactly 125 signal data points.")
        self.assertEqual(len(event.timestamps), 125,
                         "Expected exactly 125 signal time stamps.")
        i = np.where(event.timestamps == 0)
        self.assertEqual(event.signals[0][i], 100,
                         "Did not find event value at 0 time stamp.")

    def test_save_signals_csv(self):
        """Check, that signals can be saved and loaded in csv format.
        """
        # arrange
        file_name = path.join(tempfile.gettempdir(), "test.csv")
        container = EEGContainer(["Ch1", "Ch2"], 250)
        signal = [math.sin(x) for x in range(250)]
        timestamps = [x * 4 for x in range(250)]
        event_time_stamp = 500
        signal[125] = 100
        for i in range(250):
            container.add_data(BCISignal(timestamps[i], [signal[i], 5]))
        container.add_event(event_time_stamp, 250, 250)

        # action
        container.save_signals(file_name)
        container2 = EEGContainer(["Ch1", "Ch2"], 250)
        container2.load_signals(file_name)

        # check
        self.assertEqual(container, container2,
                         "Loaded signals differ from stored ones.")

    def test_numerical_index_access_test(self):
        """Check, that numerical index can be used to access signals.
        """
        # arrange
        container = EEGContainer(["Ch1", "Ch2"], 256)
        for i in range(200):
            container.add_data(
                BCISignal(i, [randint(0, 100), randint(0, 100)]))

        # action and check
        self.assertEqual(
            container["Ch1"],
            container[0],
            "Signal with index 0 differed from first signal in named list.")
        self.assertEqual(
            container["Ch2"],
            container[1],
            "Signal with index 1 differed from second signal in named list.")

    def test_numerical_index_out_of_bound_test(self):
        # arrange
        container = EEGContainer(["Ch1", "Ch2"], 256)
        exception_raised = False

        for i in range(200):
            container.add_data(
                BCISignal(i, [randint(0, 100), randint(0, 100)]))

        # action
        try:
            print(container[-1])
        except BaseException:
            exception_raised = True

        # check
        self.assertTrue(
            exception_raised,
            "No exception was raised despite numerical index out of bound.")

    def test_average_channels(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]

        # action
        recording = EEGContainer(
            channel_names,
            sample_rate)
        recording.signals = signal_data
        recording.timestamps = timestamps
        avg_recording = recording.average_ch()

        # check
        self.assertEqual(len(avg_recording.signals), 1,
                         "Found more than one signal. Expected exactly 1.")
        self.assertEqual(len(avg_recording.channel_names), 1,
                         "Found more than one channel name. Expected exactly 1.")
        self.assertEqual(
            avg_recording.channel_names[0],
            "".join(channel_names),
            "Name of new channel is not as expected.")
        self.assertEqual(
            len(
                avg_recording.signals[0]),
            length,
            "Number of recorded data points is not equal to original.")

        self.assertListEqual(
            avg_recording.signals[0],
            [2.0] * length,
            "Average signal is not as expected.")

    def test_average_channels_identity(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1"]
        signal_data = [[1] * length]
        timestamps = [x for x in range(length)]

        # action
        recording = EEGContainer(
            channel_names,
            sample_rate)
        recording.signals = signal_data
        recording.timestamps = timestamps
        avg_recording = recording.average_ch()

        # check
        self.assertEqual(
            recording,
            avg_recording,
            "Average of one channel is not the same as the original.")

    def test_average_channels_selection(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]
        selected_channels = ["C1", "C2"]

        # action
        recording = EEGContainer(
            channel_names,
            sample_rate)
        recording.signals = signal_data
        recording.timestamps = timestamps
        avg_recording = recording.average_ch(*selected_channels)

        # check
        self.assertEqual(len(avg_recording.signals), 1,
                         "Found more than one signal. Expected exactly 1.")
        self.assertEqual(len(avg_recording.channel_names), 1,
                         "Found more than one channel name. Expected exactly 1.")
        self.assertEqual(
            avg_recording.channel_names[0],
            "".join(selected_channels),
            "Name of new channel is not as expected.")
        self.assertEqual(
            len(
                avg_recording.signals[0]),
            length,
            "Number of recorded data points is not equal to original.")
        self.assertListEqual(
            avg_recording.signals[0],
            [3.0] * length,
            "Average signal is not as expected.")

        self.assertListEqual(avg_recording["".join(selected_channels)], [
                             3.0] * length, "New channel could not be accessed.")

    def test_average_sub_channel(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]
        selected_channels = [("C1", "C2"), ("C1"), ("C2"), ("C1", "C2", "C3")]

        # action
        recording = EEGContainer(
            channel_names,
            sample_rate)
        recording.signals = signal_data
        recording.timestamps = timestamps
        avg_recording = recording.average_sub_ch(*selected_channels)

        # check
        self.assertEqual(len(avg_recording.signals), 4,
                         "Did not find exactly four signals.")

        self.assertEqual(len(avg_recording.channel_names), 4,
                         "Did not find exactly four channel names")

        self.assertEqual(
            len(
                avg_recording.signals[0]),
            length,
            "Number of recorded data points is not equal to original.")

        self.assertEqual(
            "C1C2",
            avg_recording.channel_names[0],
            "First channel was not named \"C1C2\".")
        self.assertEqual(
            "C1",
            avg_recording.channel_names[1],
            "Second channel was not named \"C1\".")
        self.assertEqual(
            "C2",
            avg_recording.channel_names[2],
            "Third channel was not named \"C2\".")
        self.assertEqual(
            "C1C2C3",
            avg_recording.channel_names[3],
            "Fourth channel was not named \"C1C2C3\".")

        self.assertListEqual(
            avg_recording["C1C2"],
            [3.] * length,
            "Channel \"C1C2\" was not as expected.")

        self.assertListEqual(
            avg_recording["C1"],
            [1.] * length,
            "Channel \"C1\" was not as expected.")

        self.assertListEqual(
            avg_recording["C2"],
            [5.] * length,
            "Channel \"C5\" was not as expected.")

        self.assertListEqual(
            avg_recording["C1C2C3"],
            [2.] * length,
            "Channel \"C1C2C3\" was not as expected.")

    def test_average_sub_channel_identity(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1"]
        signal_data = [[1] * length]
        timestamps = [x for x in range(length)]
        selected_channels = [("C1")]

        # action
        recording = EEGContainer(
            channel_names,
            sample_rate)
        recording.signals = signal_data
        recording.timestamps = timestamps
        avg_recording = recording.average_sub_ch(*selected_channels)

        # check
        self.assertEqual(
            recording,
            avg_recording,
            "Average of one channel is not the same as the original.")
