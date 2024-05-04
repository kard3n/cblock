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
            pathlib.Path(__file__).parent.resolve().as_posix() + "/" + "dataset.csv"
        )
    dataset = create_dataset(ds_location=dataset_location, only_title=False)

    dataset_x = dataset["content"]
    dataset_y = dataset["topic"]

    pipeline = ClassifierPipeline(stem_input=True, stem_tokens=False)
    pipeline.train(dataset_x, dataset_y)

    with open(
        "../cblock/content_classifier/classifiers/naive_bayes/classifier.pickle",
        "wb",
    ) as handle:
        pickle.dump(pipeline, handle, protocol=pickle.HIGHEST_PROTOCOL)

    pipeline.test_training(dataset_x, dataset_y)


create_classifier()
