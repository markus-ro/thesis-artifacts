import tkinter as tk
from random import random
from time import sleep, time
from typing import Callable, List, Optional, Tuple, Union

from .base import PersistentTaskBase, StimuliTime
from .base.graphic_task_base import GraphicTaskBase


class SymbolTask(GraphicTaskBase):
    __slots__ = "symbol", "target_symbol", "instructions"

    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 symbol: str,
                 target_symbol: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Symbol task. Displays one of two characters.

        :param min_non_target: Minimum number of non_target impulses between two target impulses.
        :type min_non_target: int
        :param max_non_target: Maximum number of non_target impulses between two target impulses.
        :type max_non_target: int
        :param symbol: Regular character symbol.
        :type symbol: str
        :param target_symbol: Stimuli character symbol.
        :type target_symbol: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
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

        self.symbol = symbol
        self.target_symbol = target_symbol
        if instructions:
            self.instructions = instructions

    def set_up(self) -> None:
        """Add label with instructions to listen to the sounds.
        """
        super().set_up()
        self._label = tk.Label(self._window, text=self.symbol)
        self._label.config(bg="black", fg="white", font=("Arial", 512))
        self._label.pack(side="bottom", fill="both", expand="yes")
        self._window.update()

    def main(self) -> None:
        """Main loop for task. Takes care of updating picture and send
        info to main process.
        """
        # Ask scheduler for next action
        target = self._scheduler()

        # Update image
        if target:
            self._label["text"] = self.target_symbol
        else:
            self._label["text"] = self.symbol

        super().main()

        self._send_stimulus_info(StimuliTime(time(), target))

        # Expose
        sleep(self._get_exposure_time())

        # Inter wait time
        self._label["text"] = ""
        super().main()
        sleep(self._get_inter_stim_time())


class ProbabilisticSymbolTask(SymbolTask):
    def __init__(self,
                 target_p: float,
                 symbol: str,
                 target_symbol: str,
                 exposure_time: Union[int, Tuple[int, int]],
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """Symbol task. Displays one of two characters. Probability of target stimuli is given by target_p.

        :param target_p: Probability of target stimuli.
        :type target_p: float
        :param symbol: Regular character symbol.
        :type symbol: str
        :param target_symbol: Stimuli character symbol.
        :type target_symbol: str
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
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
            symbol,
            target_symbol,
            exposure_time,
            instructions,
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


class PersistentSymbolTask(PersistentTaskBase):
    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 symbol: str,
                 target_symbol: str,
                 exposure_time: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[int] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """ Persistent Symbol task. Displays one of two characters. Can be restarted after being stopped.

        :param min_non_target: Minimum number of non target stimuli between two target stimuli.
        :type min_non_target: int
        :param max_non_target: Maximum number of non target stimuli between two target stimuli.
        :type max_non_target: int
        :param symbol: Regular character symbol.
        :type symbol: str
        :param target_symbol: Stimuli character symbol.
        :type target_symbol: str
        :param exposure_time: Exposure of single impulse in ms.
        :type exposure_time: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.symbol = symbol
        self.target_symbol = target_symbol
        self.exposure_time = exposure_time
        self.instructions = instructions
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of SymbolTask using original parameters.
        """
        self.task = SymbolTask(
            self.min_non_target,
            self.max_non_target,
            self.symbol,
            self.target_symbol,
            self.exposure_time,
            self.instructions,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)


class PersistentProbabilisticSymbolTask(PersistentTaskBase):
    def __init__(self,
                 target_p: float,
                 symbol: str,
                 target_symbol: str,
                 exposure_time: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 inter_stim_time: Optional[int] = 200,
                 early_stop: Optional[Callable] = None) -> None:
        """ Persistent Probabilistic Symbol task. Displays one of two characters. Can be restarted after being stopped. Probability of target stimuli is given by target_p.

        :param target_p: Probability of target stimuli.
        :type target_p: float
        :param symbol: Regular character symbol.
        :type symbol: str
        :param target_symbol: Stimuli character symbol.
        :type target_symbol: str
        :param exposure_time: Exposure of single impulse in ms.
        :type exposure_time: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.target_p = target_p
        self.symbol = symbol
        self.target_symbol = target_symbol
        self.exposure_time = exposure_time
        self.instructions = instructions
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of ProbabilisticSymbolTask using original parameters.
        """
        self.task = ProbabilisticSymbolTask(
            self.target_p,
            self.symbol,
            self.target_symbol,
            self.exposure_time,
            self.instructions,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)
