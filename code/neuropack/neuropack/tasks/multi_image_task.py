import tkinter as tk
from random import choice, random
from time import sleep, time
from typing import Callable, List, Optional, Tuple, Union

from PIL import Image, ImageTk

from .base import PersistentTaskBase, StimuliTime
from .base.graphic_task_base import GraphicTaskBase
from .base.task_util import file_filter


class MultiImageTask(GraphicTaskBase):
    __slots__ = "all_images", "target_images", "_allowed_extensions", "_panel"

    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: Union[int, Tuple[int, int]],
            all_images: List[str],
            target_images: List[str],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Multi image oddball paradigm. Allows for multiple odd images. Target is randomly chosen
        from provided list.

        :param min_non_target: Minimum number of non_target impulses between two target impulses.
        :type min_non_target: int
        :param max_non_target: Maximum number of non_target impulses between two target impulses.
        :type max_non_target: int
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param all_images: All paths to images [*.png, *jpg], which are not the target.
        :type all_images: List[str]
        :param target_images: Paths to target images [*.png, *jpg].
        :type target_images: List[str]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target.
        :type target_image: Optional[List[bool]]
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__(min_non_target, max_non_target, exposure_time,
                         stimuli_record, inter_stim_time, early_stop)
        self._allowed_extensions = ["png", "jpg"]

        # Target should not occur without our knowledge
        for img in target_images:
            if img in all_images:
                all_images.remove(img)

        # Make sure all paths lead to valid  pictures
        self.target_images = [x for x in target_images if file_filter(
            x,
            self._allowed_extensions,
            False)]
        self.all_images = [x for x in all_images if file_filter(
            x,
            self._allowed_extensions,
            False)]

    def set_up(self) -> None:
        """Add label for displaying image to window.
        """
        super().set_up()
        self._panel = tk.Label(self._window)
        self._panel.config(bg="black")
        self._panel.pack(side="bottom", fill="both", expand="yes")

    def main(self) -> None:
        """Main loop for task. Takes care of updating picture and send
        info to main process.
        """
        # Ask scheduler for next action
        target = self._scheduler()

        # Update image
        if target:
            self.__update_image(choice(self.target_images))
        else:
            self.__update_image(choice(self.all_images))

        # Update GUI
        super().main()

        # Send to main process
        self._send_stimulus_info(StimuliTime(time(), target))

        # Expose
        sleep(self._get_exposure_time())

        # Inter wait time
        self.__remove_image()
        super().main()
        sleep(self._get_inter_stim_time())

    def __remove_image(self) -> None:
        """Remove displayed image.
        """
        self._panel.configure(image="")

    def __update_image(self, img_path: str) -> None:
        """Update image in window label.

        :param img_path: Path to new image.
        :type img_path: str
        """
        t_img = ImageTk.PhotoImage(Image.open(img_path))
        self._panel.configure(image=t_img)
        self._panel.image = t_img


class ProbabilisticMultiImageTask(MultiImageTask):
    def __init__(
            self,
            target_p: float,
            exposure_time: Union[int, Tuple[int, int]],
            all_images: List[str],
            target_images: List[str],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Multi image oddball paradigm. Allows for multiple odd images. Target frequency is given by target_p.

        :param target_p: Probability of target image.
        :type target_p: float
        :param exposure_time: Exposure of single impulse in ms. If tuple, takes random value in range at each impulse.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param all_images: All paths to images [*.png, *jpg], which are not the target.
        :type all_images: List[str]
        :param target_images: Paths to target images [*.png, *jpg].
        :type target_images: List[str]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target.
        :type target_image: Optional[List[bool]]
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200. If tuple, takes random value in range.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__(
            1,
            1,
            exposure_time,
            all_images,
            target_images,
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


class PersistentProbabilisticMultiImageTask(PersistentTaskBase):
    def __init__(
            self,
            target_p: float,
            exposure_time: int,
            all_images: List[str],
            target_images: List[str],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[int] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Persistent multi image oddball paradigm. Allows for multiple odd images. Target frequency is given by target_p.

        :param target_p: Probability of target image.
        :type target_p: float
        :param exposure_time: Exposure of single impulse in ms.
        :type exposure_time: int
        :param all_images: All paths to images [*.png, *jpg], which are not the target.
        :type all_images: List[str]
        :param target_images: Paths to target images [*.png, *jpg].
        :type target_images: List[str]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target.
        :type target_image: Optional[List[bool]]
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.target_p = target_p
        self.exposure_time = exposure_time
        self.all_images = all_images
        self.target_images = target_images
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create task object. Uses previously defined parameters"""
        self.task = ProbabilisticMultiImageTask(
            self.target_p,
            self.exposure_time,
            self.all_images,
            self.target_images,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)


class PersistentMultiImageTask(PersistentTaskBase):
    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: int,
            all_images: List[str],
            target_images: List[str],
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[int] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Persistent multi image oddball paradigm. Allows for multiple odd images.

        :param min_non_target: Minimum number of non target images between two target images.
        :type min_non_target: int
        :param max_non_target: Maximum number of non target images between two target images.
        :type max_non_target: int
        :param exposure_time: Exposure of single impulse in ms.
        :type exposure_time: int
        :param all_images: All paths to images [*.png, *jpg], which are not the target.
        :type all_images: List[str]
        :param target_images: Paths to target images [*.png, *jpg].
        :type target_images: List[str]
        :param stimuli_record: Optional parameter. Replay a previous run of this task.
        List is used for scheduling. True = target, False = non_target.
        :type target_image: Optional[List[bool]]
        :param inter_stim_time: Time between two stimuli in ms, defaults to 200.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback if task is stopped by user.
        :type instructions: Optional[Callable], optional
        """
        super().__init__()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.exposure_time = exposure_time
        self.all_images = all_images
        self.target_images = target_images
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of MultiImageTask using original parameters.
        """
        self.task = MultiImageTask(
            self.min_non_target,
            self.max_non_target,
            self.exposure_time,
            self.all_images,
            self.target_images,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)
