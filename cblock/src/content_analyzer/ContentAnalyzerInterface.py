from abc import ABC, abstractmethod

from editor.ContentExtractionResult import ContentExtractionResult


class ContentAnalyzerInterface(ABC):

    # returns true if the passed content should be filtered, false otherwise
    @abstractmethod
    def analyze(self, content: ContentExtractionResult) -> bool:
        raise NotImplementedError("Not implemented")
