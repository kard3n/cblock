from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class SimpleContentClassifier(ContentClassifierInterface):

    def classify(self, content: ContentExtractionResult) -> bool:
        if content.text.__contains__("war"):
            return True
        return True
