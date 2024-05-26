from abc import ABC, abstractmethod

from editor.ContentExtractionResult import ContentExtractionResult


class ContentClassifierInterface(ABC):
    @abstractmethod
    def __init__(self, topics_to_remove: list[str]):
        raise NotImplementedError("Not implemented")

    # returns true if the passed content should be filtered, false otherwise
    @abstractmethod
    def classify(self, content: ContentExtractionResult) -> bool:
        """
        Analyzes the given content
        :param content: The content to analyze
        :return: (boolean) True if the content matches one of the forbidden topics, False otherwise
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def get_supported_topics(self) -> list[str]:
        """
        Return a list of all the topics the classifier can identify
        :return:
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def set_topics_to_remove(self, topics: list[str]):
        raise NotImplementedError("Not implemented")
