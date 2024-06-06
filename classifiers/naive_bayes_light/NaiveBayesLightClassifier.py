import pathlib
import pickle
import nltk

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class NaiveBayesLightClassifier(ContentClassifierInterface):
    def __init__(self, topics_to_remove: list[str], aggressiveness: float):
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        self.model = pickle.load(
            open(
                pathlib.Path(__file__).parent.resolve().as_posix()
                + "/classifier.pickle",
                "rb",
            )
        )

        self.forbidden_topics = topics_to_remove
        self.aggressiveness = aggressiveness
        self.topics = self.model.classes_

    def classify(self, content: ContentExtractionResult) -> bool:
        if content.title != "":
            topic_probabilities = self.model.predict_proba(
                [content.title + " " + content.text]
            )[0]

            topic_probabilities_max = max(topic_probabilities)

            # scales the probability of each topic by self.aggressiveness.
            # If the result has a higher or equal probability to the max probability, returns true
            for topic, probability in zip(self.topics, topic_probabilities):
                if topic in self.forbidden_topics:
                    if probability * self.aggressiveness >= topic_probabilities_max:
                        return True

        return False

    def get_supported_topics(self) -> list[str]:
        return self.model.classes_

    def set_topic_blacklist(self, topics: list[str]):
        self.forbidden_topics = topics

    def set_aggressiveness(self, aggressiveness: float):
        self.aggressiveness = aggressiveness

    def get_aggressiveness(self) -> float:
        return self.aggressiveness


classifier = NaiveBayesLightClassifier
