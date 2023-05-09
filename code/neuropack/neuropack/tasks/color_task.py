import tkinter as tk
from random import random
from time import sleep, time
from typing import Callable, List, Optional, Tuple, Union

from .base import PersistentTaskBase, StimuliTime
from .base.graphic_task_base import GraphicTaskBase


class ColorTask(GraphicTaskBase):
    __slots__ = "color", "target_color", "instructions"

    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 color: str,
                 target_color: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Color task. Displays one of two colors.

        :param min_non_target: Minimum number of non_target impulses between two target impulses.
        :type min_non_target: int
        :param max_non_target: Maximum number of non_target impulses between two target impulses.
        :type max_non_target: int
        :param color: Name of normal color.
        :type color: str
        :param target_color: Target color.
        :type target_color: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__(
            min_non_target,
            max_non_target,
            exposure_time,
            stimuli_record,
            inter_stim_time,
            early_stop)

        self.color = color
        self.target_color = target_color

    def set_up(self) -> None:
        """Add label with instructions to listen to the sounds.
        """
        super().set_up()
        self._label = tk.Label(self._window)
        self._label.config(bg="black", fg=self.color, font=("Arial", 700))
        self._label.pack(side="bottom", fill="both", expand="yes")
        self._label["text"] = u"\u25CF"
        self._window.update()

    def main(self) -> None:
        """Main loop for task. Takes care of updating picture and send
        info to main process.
        """
        # Ask scheduler for next action
        target = self._scheduler()

        # Update image
        if target:
            self._label["fg"] = self.target_color
        else:
            self._label["fg"] = self.color

        super().main()
        self._send_stimulus_info(StimuliTime(time(), target))

        # Exposure
        sleep(self._get_exposure_time())

        # Inter wait time
        self._label["fg"] = "black"
        super().main()
        sleep(self._get_inter_stim_time())


class ProbabilisticColorTask(ColorTask):
    def __init__(self,
                 target_p: float,
                 color: str,
                 target_color: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Color task. Displays one of two colors. Probability of target can be set.

        :param target_p: Probability of target impulse.
        :type target_p: float
        :param color: Name of normal color.
        :type color: str
        :param target_color: Target color.
        :type target_color: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """

        super().__init__(
            1,
            1,
            color,
            target_color,
            exposure_time,
            stimuli_record,
            inter_stim_time,
            early_stop)
        self.target_p = target_p
        self.first = True

    def _scheduler(self) -> bool:
        """Overwritten scheduler. Schedules target and non target
        per given probability.

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

        # First stimuli should never be target
        if self.first:
            self.first = False
            return False

        # Choose next stimuli based on given probability
        return random() < self.target_p


class PersistentColorTask(PersistentTaskBase):
    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 color: str,
                 target_color: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Persistent color task. Displays one of two colors. Task can be resumed once stopped.

        :param min_non_target: Minimum number of non target stimuli before target.
        :type min_non_target: int
        :param max_non_target: Maximum number of non target stimuli before target.
        :type max_non_target: int
        :param color: Name of normal color.
        :type color: str
        :param target_color: Target color.
        :type target_color: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.color = color
        self.target_color = target_color
        self.exposure_time = exposure_time
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of ColorTask using original parameters.
        """
        self.task = ColorTask(
            self.min_non_target,
            self.max_non_target,
            self.color,
            self.target_color,
            self.exposure_time,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)


class PersistentProbabilisticColorTask(PersistentTaskBase):
    def __init__(self,
                 target_p: float,
                 color: str,
                 target_color: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Persistent probabilistic color task. Displays one of two colors. Task can be resumed once stopped.

        :param target_p: Probability of target impulse.
        :type target_p: float
        :param color: Name of normal color.
        :type color: str
        :param target_color: Target color.
        :type target_color: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.target_p = target_p
        self.color = color
        self.target_color = target_color
        self.exposure_time = exposure_time
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of ProbabilisticColorTask using original parameters.
        """
        self.task = ProbabilisticColorTask(
            self.target_p,
            self.color,
            self.target_color,
            self.exposure_time,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)
