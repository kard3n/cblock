import pathlib
import pickle

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class NaiveBayesClassifier(ContentClassifierInterface):
    def __init__(self, topics_to_remove: list[str]):
        with open(
            pathlib.Path(__file__).parent.resolve().as_posix() + "/classifier.pickle",
            "rb",
        ) as pickled_classifier:
            self.model = pickle.load(pickled_classifier)

        self.forbidden_topics = topics_to_remove

    def classify(self, content: ContentExtractionResult) -> bool:
        if content.title != "":
            """topic_probabilities = self.model.predict_proba(
                content.title + " " + content.text
            )"""
            return (
                self.model.predict(content.title + " " + content.text)
                in self.forbidden_topics
            )
        return False

    def get_supported_topics(self) -> list[str]:
        return self.model.classes_

    def set_topics_to_remove(self, topics: list[str]):
        self.forbidden_topics = topics
