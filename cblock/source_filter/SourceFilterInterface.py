from abc import ABC, abstractmethod

from source_filter.Action import Action


# The source filter returns the action the application should take for every request or response
# based on its source (URL, IP, ...)
class SourceFilterInterface(ABC):

    @abstractmethod
    def get_action(self, source: str) -> Action:
        raise NotImplementedError("Not implemented")
