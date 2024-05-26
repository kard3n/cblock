from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class SimpleContentClassifier(ContentClassifierInterface):
    def __init__(self, topics_to_remove: list[str]):
        pass

    def classify(
        self,
        content: ContentExtractionResult,
    ) -> bool:
        return True

    def get_allowed_topics(self) -> list[str]:
        return []

    def set_topics_to_remove(self, topics: list[str]):
        pass
