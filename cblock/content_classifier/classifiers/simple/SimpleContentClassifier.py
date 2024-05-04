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
