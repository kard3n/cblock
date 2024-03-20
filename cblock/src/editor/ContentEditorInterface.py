from abc import ABC, abstractmethod

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from editor.ContentExtractionResult import ContentExtractionResult


class ContentEditorInterface(ABC):

    @abstractmethod
    def __init__(
        self,
        content_analyzer: ContentClassifierInterface,
        content_factory: ContentFactory,
    ) -> None:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def edit(self, input_raw: str, schema: any) -> str:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def extract_content(
        self,
        input_value,
        schema,
        result_container: ContentExtractionResult | None = None,
    ) -> ContentExtractionResult:
        raise NotImplementedError("Not implemented")

    def apply_action(self, input_value, schema: any, content: Content) -> str:
        raise NotImplementedError("Not implemented")
