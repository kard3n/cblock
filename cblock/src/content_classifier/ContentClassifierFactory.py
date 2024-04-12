import logging

from configuration.Configuration import Configuration
from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_classifier.classifiers.content_to_file.ContentToFileClassifier import (
    ContentToFileClassifier,
)
from content_classifier.classifiers.naive_bayes.NaiveBayesClassifier import (
    NaiveBayesClassifier,
)
from content_classifier.classifiers.simple.SimpleContentClassifier import (
    SimpleContentClassifier,
)


class ContentAnalyzerFactory:
    name_to_classifier = {
        "naive_bayes": NaiveBayesClassifier,
        "content_to_file": ContentToFileClassifier,
        "simple_content_classifier": SimpleContentClassifier,
    }

    def get_content_analyzer(
        self, configuration: Configuration
    ) -> ContentClassifierInterface:
        if configuration.classifier in self.name_to_classifier.keys():
            return self.name_to_classifier[configuration.classifier](
                topics_to_remove=configuration.get_topics_to_remove()
            )
        return SimpleContentClassifier(
            topics_to_remove=configuration.get_topics_to_remove()
        )
