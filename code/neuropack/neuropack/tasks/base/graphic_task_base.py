import sys
from tkinter import Tk
from typing import Callable, List, Optional, Tuple, Union

from . import TaskBase


class GraphicTaskBase(TaskBase):
    __slots__ = "_window", "_early_stop", "_key_pressed"

    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: Union[int, Tuple[int, int]],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Union[int, Tuple[int, int]] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Base class for tasks with graphic display. It is based on tkinter. It is not recommended to use it directly.

        :param min_non_target: Minimum number of non-target stimuli.
        :param type: int
        :param max_non_target: Maximum number of non-target stimuli.
        :param type: int
        :param exposure_time: Exposure time of stimuli in ms.
        :param type: Union[int, Tuple[int, int]]
        :param stimuli_record: List of bools. True means target stimulus, False means non-target stimulus.
        :param type: list
        :param inter_stim_time: Time between stimuli in ms.
        :param type: Union[int, Tuple[int, int]]
        :param early_stop: Function to be called when task is stopped early.
        :param type: function"""
        super().__init__(min_non_target, max_non_target,
                         exposure_time, stimuli_record, inter_stim_time)
        self._early_stop = early_stop
        self._key_pressed = False

    def set_up(self) -> None:
        """Setup tk windows for further graphic displays.
        """
        self._window = Tk()
        self._window.wm_attributes('-fullscreen', True)
        self._window.wm_attributes("-topmost", True)
        self._window.configure(background='black')
        self._window.configure(cursor='none')
        self._window.bind("<Escape>", self.__early_stop_call)

    def main(self) -> None:
        """Async main loop for tk windows. Otherwise it would keep whole process
        busy.
        """
        self._window.update()

    def __early_stop_call(self, ev):
        """Stop task early due to user intervention.
        Task will be stopped at next update or through external intervention.
        """
        if self._running and not self._key_pressed:
            self._aborted.value = 1
            self._key_pressed = True
            if self._early_stop:
                self._early_stop()
