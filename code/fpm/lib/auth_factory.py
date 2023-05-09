# from neuropack.tasks.color_task import PersistentColorTask
import os
import sys
from os import getcwd, listdir, path

from neuropack import KeyWave, TemplateDatabase
from neuropack.devices import BrainFlowDevice
from neuropack.feature_extraction import BandpowerModel
from neuropack.preprocessing import PreprocessingPipeline
from neuropack.preprocessing.filters import BandpassFilter, DetrendFilter
from neuropack.similarity_metrics import bounded_cosine_similarity as cosine_similarity
from neuropack.tasks.image_task import PersistentImageTask

# sys.path.append("./code/Library")


def build_verification() -> KeyWave:
    # Create device
    #device = BrainFlowDevice.CreateMuse2BLEDDevice()
    device = BrainFlowDevice.CreateMuse2Device()

    # Create image task
    dataset_dir = path.join(
        getcwd(),
        "code",
        "neuropack",
        "examples",
        "data",
        "images",
        "random")

    # Create acquistion task
    target_image = "1.jpg"
    images = [path.join(dataset_dir, x) for x in listdir(dataset_dir)]
    target_image = path.join(dataset_dir, target_image)
    task = PersistentImageTask(
        2,
        5,
        220,
        images,
        target_image,
        inter_stim_time=300)

    # Create Pipeline
    prepocessing_pipeline = PreprocessingPipeline()
    prepocessing_pipeline.add_filter(BandpassFilter())

    # Create Feature extraction model
    feature_extraction_model = BandpowerModel()

    # Create Database
    database = TemplateDatabase()

    # Define threshold
    t = 0.725

    # Create verification system
    veri = KeyWave(
        device,
        task,
        prepocessing_pipeline,
        feature_extraction_model,
        database,
        cosine_similarity,
        0.725)
    return veri
