from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class AlwaysTrueClassifier(ContentClassifierInterface):
    def __init__(self, topics_to_remove: list[str], aggressiveness: float):
        pass

    def classify(
        self,
        content: ContentExtractionResult,
    ) -> bool:
        return True

    def get_supported_topics(self) -> list[str]:
        return []

    def set_topic_blacklist(self, topics: list[str]):
        pass

    def set_aggressiveness(self, aggressiveness: float):
        pass

    def get_aggressiveness(self) -> float:
        return 1.0


classifier = AlwaysTrueClassifier
