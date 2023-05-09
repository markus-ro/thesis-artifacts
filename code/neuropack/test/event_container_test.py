import unittest

import numpy as np

from neuropack.container import EventContainer
from neuropack.utils import osum


class EventContainerTests(unittest.TestCase):
    def test_average_channels(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]

        # action
        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        avg_event = event.average_ch()

        # check
        self.assertEqual(len(avg_event.signals), 1,
                         "Found more than one signal. Expected exactly 1.")
        self.assertEqual(len(avg_event.channel_names), 1,
                         "Found more than one channel name. Expected exactly 1.")
        self.assertEqual(
            avg_event.channel_names[0],
            "".join(channel_names),
            "Name of new channel is not as expected.")
        self.assertEqual(len(
            avg_event.signals[0]), length, "Number of recorded data points is not equal to original.")
        self.assertTrue(
            np.array_equal(
                avg_event.signals[0],
                np.array(
                    [2.0] * length)),
            "Average signal is not as expected.")

    def test_average_channels_selection(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]
        selected_channels = ["C1", "C2"]

        # action
        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        avg_event = event.average_ch(*selected_channels)

        # check
        self.assertEqual(len(avg_event.signals), 1,
                         "Found more than one signal. Expected exactly 1.")
        self.assertEqual(len(avg_event.channel_names), 1,
                         "Found more than one channel name. Expected exactly 1.")
        self.assertEqual(
            avg_event.channel_names[0],
            "".join(selected_channels),
            "Name of new channel is not as expected.")
        self.assertEqual(len(
            avg_event.signals[0]), length, "Number of recorded data points is not equal to original.")
        self.assertTrue(
            np.array_equal(
                avg_event.signals[0],
                np.array(
                    [3.0] * length)),
            "Average signal is not as expected.")
        self.assertTrue(np.array_equal(avg_event["".join(selected_channels)], np.array(
            [3.0] * length)), "New channel could not be accessed.")

    def test_average_channels_identity(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1"]
        signal_data = [[1] * length]
        timestamps = [x for x in range(length)]

        # action
        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        avg_event = event.average_ch()

        # check
        self.assertEqual(
            event,
            avg_event,
            "Average of one channel is not the same as the original.")

    def test_average_sub_channel(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2", "C3"]
        signal_data = [[1] * length, [5] * length, [0] * length]
        timestamps = [x for x in range(length)]
        selected_channels = [("C1", "C2"), ("C1"), ("C2"), ("C1", "C2", "C3")]

        # action
        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        avg_event = event.average_sub_ch(*selected_channels)

        # check
        self.assertEqual(len(avg_event.signals), 4,
                         "Did not find exactly four signals.")

        self.assertEqual(len(avg_event.channel_names), 4,
                         "Did not find exactly four channel names")

        self.assertEqual(len(
            avg_event.signals[0]), length, "Number of recorded data points is not equal to original.")

        self.assertEqual(
            "C1C2",
            avg_event.channel_names[0],
            "First channel was not named \"C1C2\".")
        self.assertEqual(
            "C1",
            avg_event.channel_names[1],
            "Second channel was not named \"C1\".")
        self.assertEqual(
            "C2",
            avg_event.channel_names[2],
            "Third channel was not named \"C2\".")
        self.assertEqual(
            "C1C2C3",
            avg_event.channel_names[3],
            "Fourth channel was not named \"C1C2C3\".")

        self.assertTrue(np.array_equal(
            avg_event["C1C2"],
            np.array([3.] * length)
        ), "Channel \"C1C2\" was not as expected.")

        self.assertTrue(np.array_equal(
            avg_event["C1"],
            np.array([1.] * length)
        ), "Channel \"C1\" was not as expected.")

        self.assertTrue(np.array_equal(
            avg_event["C2"],
            np.array([5.] * length)
        ), "Channel \"C5\" was not as expected.")

        self.assertTrue(np.array_equal(
            avg_event["C1C2C3"],
            np.array([2.] * length)
        ), "Channel \"C1C2C3\" was not as expected.")

    def test_average_sub_channel_identity(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1"]
        signal_data = [[1] * length]
        timestamps = [x for x in range(length)]
        selected_channels = [("C1")]

        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        avg_event = event.average_sub_ch(*selected_channels)

        # check
        self.assertEqual(
            event,
            avg_event,
            "Average of one channel is not the same as the original.")

    def test_add(self):
        """Check that EventContainer addition behaves as expected.
        """
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2"]
        signal_data = [[1] * length, [5] * length]
        timestamps = [x for x in range(length)]

        # action
        ev1 = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        ev2 = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)

        ev3 = ev1 + ev2

        # check
        self.assertListEqual(
            ev3.channel_names,
            channel_names,
            "Resulting container has different channel names.")
        self.assertTrue(np.array_equal(
            ev3["C1"],
            np.array([2] * length),
        ), "Result of addition for \"C1\" is different from expected value.")
        self.assertTrue(np.array_equal(
            ev3["C2"],
            np.array([10] * length),
        ), "Result of addition for \"C2\" is different from expected value.")
        self.assertTrue(np.array_equal(
            ev1["C1"],
            np.array([1] * length),
        ), "ev1 changed.")
        self.assertTrue(np.array_equal(
            ev1["C2"],
            np.array([5] * length),
        ), "ev1 changed.")
        self.assertTrue(np.array_equal(
            ev2["C1"],
            np.array([1] * length),
        ), "ev2 changed.")
        self.assertTrue(np.array_equal(
            ev2["C2"],
            np.array([5] * length),
        ), "ev2 changed.")

    def test_add_osum(self):
        """Check that EventContainer addition behaves as expected.
        """
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2"]
        signal_data = [[1] * length, [5] * length]
        timestamps = [x for x in range(length)]

        # action
        ev1 = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        ev2 = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)

        ev3 = osum([ev1, ev2])

        # check
        self.assertListEqual(
            ev3.channel_names,
            channel_names,
            "Resulting container has different channel names.")
        self.assertTrue(np.array_equal(
            ev3["C1"],
            np.array([2] * length),
        ), "Result of addition for \"C1\" is different from expected value.")
        self.assertTrue(np.array_equal(
            ev3["C2"],
            np.array([10] * length),
        ), "Result of addition for \"C2\" is different from expected value.")
        self.assertTrue(np.array_equal(
            ev1["C1"],
            np.array([1] * length),
        ), "ev1 changed.")
        self.assertTrue(np.array_equal(
            ev1["C2"],
            np.array([5] * length),
        ), "ev1 changed.")
        self.assertTrue(np.array_equal(
            ev2["C1"],
            np.array([1] * length),
        ), "ev2 changed.")
        self.assertTrue(np.array_equal(
            ev2["C2"],
            np.array([5] * length),
        ), "ev2 changed.")

    def test_numerical_index_access_test(self):
        """Check, that numerical index can be used to access signals.
        """
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2"]
        signal_data = [[1] * length, [5] * length]
        timestamps = [x for x in range(length)]

        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)

        self.assertListEqual(
            event["C1"].tolist(),
            event[0].tolist(),
            "Signal with index 0 differed from first signal in named list.")
        self.assertListEqual(
            event["C2"].tolist(),
            event[1].tolist(),
            "Signal with index 1 differed from second signal in named list.")

    def test_numerical_index_out_of_bound_test(self):
        # arrange
        sample_rate = 256
        length = 20
        channel_names = ["C1", "C2"]
        signal_data = [[1] * length, [5] * length]
        timestamps = [x for x in range(length)]

        event = EventContainer(
            channel_names,
            sample_rate,
            signal_data,
            timestamps)
        exception_raised = False

        # action
        try:
            print(event[-1])
        except BaseException:
            exception_raised = True

        # check
        self.assertTrue(
            exception_raised,
            "No exception was raised despite numerical index out of bound.")
