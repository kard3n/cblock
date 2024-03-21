from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_classifier.classifiers.naive_bayes.NaiveBayesClassifier import (
    NaiveBayesClassifier,
)
from content_classifier.classifiers.simple.SimpleContentClassifier import (
    SimpleContentClassifier,
)


class ContentAnalyzerFactory:
    def get_content_analyzer(self) -> ContentClassifierInterface:
        # TODO depending on configuration, use one or another
        return SimpleContentClassifier()
        return NaiveBayesClassifier(
            forbidden_topics=[
                "finance",
                "disaster_environment",
                "politics",
                "war_crime",
                "religion_belief",
                "health",
            ]
        )
