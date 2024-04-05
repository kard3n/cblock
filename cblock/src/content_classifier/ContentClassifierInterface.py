from abc import ABC, abstractmethod

from editor.ContentExtractionResult import ContentExtractionResult


class ContentClassifierInterface(ABC):

    # returns true if the passed content should be filtered, false otherwise
    @abstractmethod
    def classify(self, content: ContentExtractionResult) -> bool:
        raise NotImplementedError("Not implemented")
