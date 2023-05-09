import tkinter as tk
from random import random
from time import sleep, time
from typing import Callable, List, Optional

from play_sounds import play_file

from .base import PersistentTaskBase, StimuliTime
from .base.graphic_task_base import GraphicTaskBase
from .base.task_util import file_filter


class AudioTask(GraphicTaskBase):
    __slots__ = "sound_path", "target_sound_path", "instructions"

    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 sound_path: str,
                 target_sound_path: str,
                 time_between_sounds: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 early_stop: Optional[Callable] = None) -> None:
        """Auditory task for P300. Uses two different sounds.

        :param min_non_target: Minimum number of non_target impulses between two targets.
        :type min_non_target: int
        :param max_non_target: Maximum number of non_target impulses between two targets.
        :type max_non_target: int
        :param sound_path: Path to regular sound file. Supported formats mp3 and wav.
        :type sound_path: str
        :param target_sound_path: Path to target sound file. Supported formats mp3 and wav.
        :type target_sound_path: str
        :param time_between_sounds: time between one sound finishing and next sound playing.
        :type time_between_sounds: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non-target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__(
            min_non_target,
            max_non_target,
            time_between_sounds,
            stimuli_record,
            early_stop=early_stop)

        file_formats = ["mp3", "wav"]
        assert file_filter(sound_path, file_formats)
        assert file_filter(target_sound_path, file_formats)

        self.sound_path = sound_path
        self.target_sound_path = target_sound_path
        self.instructions = "Please listen to the played sounds."
        if instructions:
            self.instructions = instructions

    def set_up(self) -> None:
        """Add label with instructions to listen to the sounds.
        """
        super().set_up()
        self._panel = tk.Label(self._window, text=self.instructions)
        self._panel.config(bg="black", fg="white", font=("Arial", 64))
        self._panel.pack(side="bottom", fill="both", expand="yes")
        self._window.update()

    def main(self) -> None:
        """Main loop for task. Takes care of updating picture and send
        info to main process.
        """
        # Ask scheduler for next action
        target = self._scheduler()

        # Play fitting sound
        self.play_sound(target)

        # Wait till next change
        sleep(self._get_exposure_time())

    def play_sound(self, target: bool):
        self._send_stimulus_info(StimuliTime(time(), target))
        sound = self.target_sound_path if target else self.sound_path

        try:
            play_file(sound)
        except Exception as e:
            print("Exception when trying to play sound with play_sounds library: ", e)

class ProbabilisticAudioTask(AudioTask):
    def __init__(self,
                 target_p: float,
                 sound_path: str,
                 target_sound_path: str,
                 time_between_sounds: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 early_stop: Optional[Callable] = None) -> None:
        """Probabilistic version of AudioTask. Uses given probability to schedule target and non-target.

        :param target_p: Probability of target stimuli.
        :type target_p: float
        :param sound_path: Path to regular sound file. Supported formats mp3 and wav.
        :type sound_path: str
        :param target_sound_path: Path to target sound file. Supported formats mp3 and wav.
        :type target_sound_path: str
        :param time_between_sounds: time between one sound finishing and next sound playing.
        :type time_between_sounds: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non-target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """

        super().__init__(
            1,
            1,
            sound_path,
            target_sound_path,
            time_between_sounds,
            instructions,
            stimuli_record,
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


class PersistentAudioTask(PersistentTaskBase):
    def __init__(self,
                 min_non_target: int,
                 max_non_target: int,
                 sound_path: str,
                 target_sound_path: str,
                 time_between_sounds: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 early_stop: Optional[Callable] = None) -> None:
        """Persistent version of AudioTask. Can be resumed after stopping.

        :param min_non_target: Minimum number of non-target stimuli between two target stimuli.
        :type min_non_target: int
        :param max_non_target: Maximum number of non-target stimuli between two target stimuli.
        :type max_non_target: int
        :param sound_path: Path to regular sound file. Supported formats mp3 and wav.
        :type sound_path: str
        :param target_sound_path: Path to target sound file. Supported formats mp3 and wav.
        :type target_sound_path: str
        :param time_between_sounds: time between one sound finishing and next sound playing.
        :type time_between_sounds: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non-target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.sound_path = sound_path
        self.target_sound_path = target_sound_path
        self.time_between_sounds = time_between_sounds
        self.instructions = instructions
        self.stimuli_record = stimuli_record
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of AudioTask using original parameters.
        """
        self.task = AudioTask(
            self.min_non_target,
            self.max_non_target,
            self.sound_path,
            self.target_sound_path,
            self.time_between_sounds,
            self.instructions,
            self.stimuli_record,
            self.early_stop)
        self.task.only_target_data(self.target_only)


class PersistentProbabilisticAudioTask(PersistentTaskBase):
    def __init__(self,
                 target_p: float,
                 sound_path: str,
                 target_sound_path: str,
                 time_between_sounds: int,
                 instructions: Optional[str] = None,
                 stimuli_record: Optional[List[bool]] = None,
                 early_stop: Optional[Callable] = None) -> None:
        """Persistent probabilistic version of AudioTask. Can be resumed after stopping.

        :param target_p: Probability of target stimuli.
        :type target_p: float
        :param sound_path: Path to regular sound file. Supported formats mp3 and wav.
        :type sound_path: str
        :param target_sound_path: Path to target sound file. Supported formats mp3 and wav.
        :type target_sound_path: str
        :param time_between_sounds: time between one sound finishing and next sound playing.
        :type time_between_sounds: int
        :param instructions: Text instructions shown on screen. Defaults to None.
        :type instructions: Optional[str], optional
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non-target. Defaults to None.
        :type stimuli_record: Optional[List[bool]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.target_p = target_p
        self.sound_path = sound_path
        self.target_sound_path = target_sound_path
        self.time_between_sounds = time_between_sounds
        self.instructions = instructions
        self.stimuli_record = stimuli_record
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of ProbabilisticAudioTask using original parameters.
        """
        self.task = ProbabilisticAudioTask(
            self.target_p,
            self.sound_path,
            self.target_sound_path,
            self.time_between_sounds,
            self.instructions,
            self.stimuli_record,
            self.early_stop)
        self.task.only_target_data(self.target_only)
