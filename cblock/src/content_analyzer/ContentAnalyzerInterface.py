from abc import ABC, abstractmethod


class ContentAnalyzerInterface(ABC):

    # returns true if the passed content should be filtered, false otherwise
    @abstractmethod
    def analyze(self, content: str) -> bool:
        raise NotImplementedError("Not implemented")
