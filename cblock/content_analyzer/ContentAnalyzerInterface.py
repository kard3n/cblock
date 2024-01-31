from abc import ABC, abstractmethod

from source_filter.Action import Action


class ContentAnalyzerInterface(ABC):

    #returns true if the passed content should be filtered, false otherwise
    @abstractmethod
    def analyze(self, content: str) -> bool:
        raise NotImplementedError("Not implemented")
