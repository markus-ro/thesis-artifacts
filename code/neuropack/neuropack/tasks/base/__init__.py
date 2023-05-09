from abc import ABC, abstractmethod
from ctypes import c_short
from dataclasses import dataclass
from multiprocessing import Pipe, Process, Value
from random import random, randrange
from time import sleep
from typing import List, Optional, Tuple, Union


@dataclass
class StimuliTime:
    timestamp: float
    is_target: bool

    def __str__(self) -> str:
        return f"StimuliTime(timestamp={self.timestamp}, is_target={self.is_target})"


class PersistentTaskBase(ABC):
    def __init__(self) -> None:
        self.target_only = True

    def start(self):
        self.create_task()
        self.task.start()

    def stop(self):
        if self.task:
            self.task.stop()
        self.task = None

    def fetch_data(self) -> StimuliTime:
        if self.task:
            return self.task.fetch_data()
        return None

    def has_data(self) -> bool:
        return self.task.has_data()

    def is_alive(self) -> bool:
        if self.task:
            return self.task.is_alive()
        return False

    def only_target_data(self, d: bool):
        """Set, if only target data should be recorded.

        :param d: Only target data?
        :type d: bool
        """
        self.target_only = d
        if self.task:
            self.task.only_target_data(d)

    @abstractmethod
    def create_task(self):
        pass

    @property
    def aborted(self):
        if self.task:
            return self.task.aborted
        return False


class TaskBase(ABC, Process):
    __slots__ = "receiver", "sender", "min_non_target", "max_non_target", "exposure_time", "inter_stim_time", "_manager", "_running", "_closed", "_num_since_target", "_record", "_aborted", "_target_only"

    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: Union[int, Tuple[int, int]],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200) -> None:
        """Base class for any acquisition task. Each acquisition task consists should
        expose individual to a number of stimuli. Acquisition is for as long as it is not stopped
        by external application.

        :param min_non_target: Minimum number of non_targets between two targets
        :type min_non_target: int
        :param max_non_target: Maximum number of non_targets impulses between two targets
        :type max_non_target: int
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param stimuli_record: Record of previous run for replay, defaults to None
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        """
        super().__init__()
        self.receiver, self.sender = Pipe()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.exposure_time = exposure_time
        self.inter_stim_time = inter_stim_time
        self._num_since_target = 0
        self._running = False,
        self._record = None
        self._aborted = Value(c_short, 0)
        self._target_only = Value(c_short, 1)

        if stimuli_record:
            self._record = stimuli_record.copy()

    def start(self) -> None:
        """Start acquisition task
        """
        self._running = True
        return super().start()

    def run(self) -> None:
        """Main logic of acquisition task.
        """
        # Setup before doing anything
        self.set_up()

        # Run task for as long as we capture data needed
        while self._aborted.value == 0:
            try:
                self.main()
            except BaseException:
                break
            sleep(.001)

    def stop(self):
        """Stop acquisition task. Needs to be called, else
        task never stops.
        """
        if self._running:
            self._running = False
            self.sender.close()
            self.receiver.close()

        # Fallback if terminate does not work for some reason
        try:
            self.terminate()
        finally:
            if self.is_alive():
                self.kill()

    def fetch_data(self) -> StimuliTime:
        """Fetch data from executed tasks.

        :return: None if no task is running, else last stimuli.
        :rtype: StimuliTime
        """
        if self.is_alive():
            return self.receiver.recv()
        return None

    def has_data(self) -> bool:
        """Check, if new data can be fetched.

        :return: Can new data be fetched?
        :rtype: bool
        """
        return self.receiver.poll(0.005)

    def only_target_data(self, d: bool):
        """Set, if only target data should be recorded.

        :param d: Only target data?
        :type d: bool
        """
        self._target_only.value = 1 if d else 0

    def _send_stimulus_info(self, s: StimuliTime):
        """Send stimulus info to receiver.

        :param s: Stimulus info
        :type s: StimuliTime
        """
        if self._target_only.value == 1:
            if not s.is_target:
                return
        self.sender.send(s)

    def _get_exposure_time(self) -> float:
        """Returns exposure time for current impulse.

        :return: If tuple, returns random value in range, else returns value.
        :rtype: float
        """
        if isinstance(self.exposure_time, tuple):
            return randrange(*self.exposure_time) / 1000
        return self.exposure_time / 1000

    def _get_inter_stim_time(self) -> float:
        """Returns time between to impulses.

        :return: If tuple, returns random value in range, else returns value.
        :rtype: float
        """
        if isinstance(self.inter_stim_time, tuple):
            return randrange(*self.inter_stim_time) / 1000
        return self.inter_stim_time / 1000

    def _scheduler(self) -> bool:
        """Algorithm to schedule next item. Should be used in every task.
        Also takes care of record keeping.

        :return: True if next item should be a target item, else false.
        :rtype: bool
        """
        # Check if a recording is used for task simulation
        if self._record:
            if len(self._record) == 0:
                self._num_since_target += 1
                self._record = None
                return False
            return self._record.pop(0)

        # We are below min distance, increment and return non_target
        if self._num_since_target < self.min_non_target:
            self._num_since_target += 1
            return False

        # We are at max distance, set count to 0 and return target
        if self._num_since_target == self.max_non_target:
            self._num_since_target = 0
            return True

        # We are in the random zone
        self._num_since_target += 1
        distance = self.max_non_target - self.min_non_target
        show_target = random() < 1 / (distance + 1)

        # Check result, write it to order record
        if show_target:
            self._num_since_target = 0

        return show_target

    @abstractmethod
    def set_up(self) -> None:
        """Preparation of task.
        """
        pass

    @abstractmethod
    def main(self) -> None:
        """None blocking main task.
        """
        pass

    @property
    def aborted(self) -> bool:
        """Checks, if task has been stopped early.

        :return: Task stopped early?
        :rtype: bool
        """
        return self._aborted.value == 1
