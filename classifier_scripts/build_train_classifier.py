import pathlib
import pickle

from content_classifier.classifiers.naive_bayes.ClassifierPipeline import (
    ClassifierPipeline,
)
from create_dataset import (
    create_dataset,
)


def create_classifier(dataset_location: str | None = None):
    print("Creating dataset...")
    if dataset_location is None:
        dataset_location = (
            pathlib.Path(__file__).parent.resolve().as_posix()
            + "/"
            + "2024_04_05_to_2024_04_17.csv"
        )
    dataset = create_dataset(ds_location=dataset_location, only_title=True)

    dataset_x = dataset["content"]
    dataset_y = dataset["topic"]

    pipeline = ClassifierPipeline()
    pipeline.train(dataset_x, dataset_y)

    with open("classifier.pickle", "wb") as handle:
        pickle.dump(pipeline, handle, protocol=pickle.HIGHEST_PROTOCOL)

    pipeline.test_training(dataset_x, dataset_y)


create_classifier()
