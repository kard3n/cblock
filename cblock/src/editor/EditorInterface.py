from abc import ABC, abstractmethod

from src.content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from src.content_factory.ContentFactory import ContentFactory


class EditorInterface(ABC):

    @abstractmethod
    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
    ) -> None:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def edit(self, input_raw: str, schema: any) -> str:
        raise NotImplementedError("Not implemented")
