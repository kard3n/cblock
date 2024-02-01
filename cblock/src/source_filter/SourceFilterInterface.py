from abc import ABC, abstractmethod

from src.source_filter.SourceAction import SourceAction


# The source filter returns the action the application should take for every request or response
# based on its source (URL, IP, ...)
class SourceFilterInterface(ABC):

    @abstractmethod
    def get_action(self, source: str) -> SourceAction:
        raise NotImplementedError("Not implemented")
