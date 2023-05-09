from typing import Callable, List, Optional, Tuple, Union

from .base import PersistentTaskBase, StimuliTime
from .multi_image_task import MultiImageTask, ProbabilisticMultiImageTask


class ImageTask(MultiImageTask):
    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: Union[int, Tuple[int, int]],
            all_images: List[str],
            target_image: str,
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Modifed MultiImageTask to use only one target image. This is useful for simpler tasks to acquire P300.

        :param min_non_target: Minimum number of non-target images to be shown.
        :type min_non_target: int
        :param max_non_target: Maximum number of non-target images to be shown.
        :type max_non_target: int
        :param exposure_time: Exposure time of each image in milliseconds. If tuple, then a random value between the two values is chosen for each image.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param all_images: List of all images to be shown.
        :type all_images: List[str]
        :param target_image: Target image to be shown.
        :type target_image: str
        :param stimuli_record: List of booleans to record stimuli. If None, then a new list is created.
        :type stimuli_record: Optional[List[bool]]
        :param inter_stim_time: Inter-stimulus time in milliseconds. If tuple, then a random value between the two values is chosen for each image.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback function called if the task is stopped early by user.
        :type early_stop: Optional[Callable], optional
        """
        super().__init__(
            min_non_target,
            max_non_target,
            exposure_time,
            all_images,
            [target_image],
            stimuli_record,
            inter_stim_time,
            early_stop)


class ProbabilisticImageTask(ProbabilisticMultiImageTask):
    def __init__(
            self,
            target_p: float,
            exposure_time: Union[int, Tuple[int, int]],
            all_images: List[str],
            target_image: str,
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[Union[int, Tuple[int, int]]] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Probabilistic version of ImageTask.

        :param target_p: Probability of target image being shown.
        :type target_p: float
        :param exposure_time: Exposure time of each image in milliseconds. If tuple, then a random value between the two values is chosen for each image.
        :type exposure_time: Union[int, Tuple[int, int]]
        :param all_images: List of all images to be shown.
        :type all_images: List[str]
        :param target_image: Target image to be shown.
        :type target_image: str
        :param stimuli_record: List of booleans to record stimuli. If None, then a new list is created.
        :type stimuli_record: Optional[List[bool]]
        :param inter_stim_time: Inter-stimulus time in milliseconds. If tuple, then a random value between the two values is chosen for each image.
        :type inter_stim_time: Optional[Union[int, Tuple[int, int]]], optional
        :param early_stop: Callback function called if the task is stopped early by user.
        :type early_stop: Optional[Callable], optional
        """
        super().__init__(
            target_p,
            exposure_time,
            all_images,
            [target_image],
            stimuli_record,
            inter_stim_time,
            early_stop)


class PersistentImageTask(PersistentTaskBase):
    def __init__(
            self,
            min_non_target: int,
            max_non_target: int,
            exposure_time: int,
            all_images: List[str],
            target_image: str,
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[int] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Persistent version of ImageTask. Can be resumed after being stopped.

        :param min_non_target: Minimum number of non-target images to be shown.
        :type min_non_target: int
        :param max_non_target: Maximum number of non-target images to be shown.
        :type max_non_target: int
        :param exposure_time: Exposure time of each image in milliseconds.
        :type exposure_time: int
        :param all_images: List of all images to be shown.
        :type all_images: List[str]
        :param target_image: Target image to be shown.
        :type target_image: str
        :param stimuli_record: List of booleans to record stimuli. If None, then a new list is created.
        :type stimuli_record: Optional[List[bool]]
        :param inter_stim_time: Inter-stimulus time in milliseconds.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback function called if the task is stopped early by user.
        :type early_stop: Optional[Callable], optional
        """
        super().__init__()
        self.min_non_target = min_non_target
        self.max_non_target = max_non_target
        self.exposure_time = exposure_time
        self.all_images = all_images
        self.target_image = target_image
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        """Create new instance of ImageTask using original parameters.
        """
        self.task = ImageTask(
            self.min_non_target,
            self.max_non_target,
            self.exposure_time,
            self.all_images,
            self.target_image,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)


class PersistentProbabilisticImageTask(PersistentTaskBase):
    def __init__(
            self,
            target_p: float,
            exposure_time: int,
            all_images: List[str],
            target_image: str,
            stimuli_record: Optional[List[bool]] = None,
            inter_stim_time: Optional[int] = 200,
            early_stop: Optional[Callable] = None) -> None:
        """Persistent version of ProbabilisticImageTask. Can be resumed after being stopped.

        :param target_p: Probability of target image being shown.
        :type target_p: float
        :param exposure_time: Exposure time of each image in milliseconds.
        :type exposure_time: int
        :param all_images: List of all images to be shown.
        :type all_images: List[str]
        :param target_image: Target image to be shown.
        :type target_image: str
        :param stimuli_record: List of booleans to record stimuli. If None, then a new list is created.
        :type stimuli_record: Optional[List[bool]]
        :param inter_stim_time: Inter-stimulus time in milliseconds.
        :type inter_stim_time: Optional[int], optional
        :param early_stop: Callback function called if the task is stopped early by user.
        :type early_stop: Optional[Callable], optional
        """
        super().__init__()
        self.target_p = target_p
        self.exposure_time = exposure_time
        self.all_images = all_images
        self.target_image = target_image
        self.stimuli_record = stimuli_record
        self.inter_stim_time = inter_stim_time
        self.early_stop = early_stop

    def create_task(self):
        self.task = ProbabilisticImageTask(
            self.target_p,
            self.exposure_time,
            self.all_images,
            self.target_image,
            self.stimuli_record,
            self.inter_stim_time,
            self.early_stop)
        self.task.only_target_data(self.target_only)
