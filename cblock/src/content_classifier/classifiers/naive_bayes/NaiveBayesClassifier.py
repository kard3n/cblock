import logging
import pathlib
import pickle

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_classifier.classifiers.naive_bayes.ClassifierPipeline import (
    ClassifierPipeline,
)
from editor.ContentExtractionResult import ContentExtractionResult


class NaiveBayesClassifier(ContentClassifierInterface):
    def __init__(self, forbidden_topics: list[str]):
        with open(
            pathlib.Path(__file__).parent.resolve().as_posix() + "/classifier.pickle",
            "rb",
        ) as pickled_classifier:
            self.model: ClassifierPipeline = pickle.load(pickled_classifier)
        self.forbidden_topics = forbidden_topics

    def classify(self, content: ContentExtractionResult) -> bool:
        logging.info(f"Classifying {content}")
        if content.title != "":
            return self.model.predict(content.title) in self.forbidden_topics
        return self.model.predict(content.text) in self.forbidden_topics
