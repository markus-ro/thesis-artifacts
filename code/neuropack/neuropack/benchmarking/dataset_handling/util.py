from itertools import combinations
from typing import List, Tuple

import numpy as np

from ...container import EEGContainer, EventContainer
from ...preprocessing import PreprocessingPipeline
from ...utils import oavg
from .benchmark_container import BenchmarkContainer


def load_dataset(id: str,
                 enrollment_record: str,
                 authentication_records: List[str],
                 channel_names: List[str] = ["TP9", "AF7", "AF8", "TP10"],
                 sample_rate: int = 256,
                 epoch_length: Tuple[int,
                                     int] = (100,
                                             500),
                 preprossessing: PreprocessingPipeline = None,
                 artifact_removal=False):
    """ Function to load a dataset into a BenchmarkContainer.

    :param id: ID of the participant
    :type id: str
    :param enrollment_record: Path to the enrollment record
    :type enrollment_record: str
    :param authentication_records: List of paths to the authentication records
    :type authentication_records: List[str]
    :param channel_names: List of channel names
    :type channel_names: List[str]
    :param sample_rate: Sample rate of the EEG data
    :type sample_rate: int
    :param epoch_length: Length of the epochs in ms
    :type epoch_length: Tuple[int, int]
    :param preprossessing: Preprocessing pipeline to apply to the data
    :type preprossessing: PreprocessingPipeline
    :param artifact_removal: If true, artifacts will be removed
    :type artifact_removal: bool
    :return: BenchmarkContainer
    """
    # Create lists to store epochs
    template_epochs = []
    authentication_epochs = []

    # Get template epochs
    enroll_cont = EEGContainer.from_file(
        channel_names, sample_rate, enrollment_record)

    if preprossessing:
        preprossessing.apply(enroll_cont)

    template_epochs = enroll_cont.get_all_events(
        epoch_length[0], epoch_length[1])[:-1]
    while len(template_epochs[-1]) != len(template_epochs[-2]):
        template_epochs = template_epochs[:-1]

    # Get authentication epochs
    for set in authentication_records:
        auth_cont = EEGContainer.from_file(channel_names, sample_rate, set)

        if preprossessing:
            preprossessing.apply(auth_cont)

        # Get all events
        events = auth_cont.get_all_events(epoch_length[0], epoch_length[1])
        while len(events[-1]) != len(events[-2]):
            events = events[:-1]

        authentication_epochs += events

    if artifact_removal:
        # Artifcat removal
        template_epochs = [
            x for x in template_epochs if not x.contains_blink()]
        authentication_epochs = [
            x for x in authentication_epochs if not x.contains_blink()]

    # Return collected epochs
    return BenchmarkContainer(
        id,
        template_epochs,
        authentication_epochs)


def extract_features(
        participant_data: List[BenchmarkContainer],
        model,
        tuple_size=2):
    """ Function to extract features from a list of BenchmarkContainer objects using a given model.
    The features are extracted from tuples of authentication epochs. Paired authentication epochs are
    averaged and then the features are extracted from the averaged epoch.

    :param participant_data: List of BenchmarkContainer objects
    :type participant_data: List[BenchmarkContainer]
    :param model: Model to extract features with
    :type model: Model
    :param tuple_size: Size of the tuples to extract features from
    :type tuple_size: int
    :return: List of extracted features
    :rtype: List[np.ndarray]"""
    samples = []
    for i in participant_data:
        epochs = [x for x in i.authentication_epochs]
        comb = combinations(epochs, tuple_size)
        for j in comb:
            samples.append(model.extract_features(oavg(j)))
    return samples
