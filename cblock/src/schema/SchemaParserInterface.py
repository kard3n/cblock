import abc
from abc import ABC


class SchemaParserInterface(ABC):
    @classmethod
    @abc.abstractmethod
    def parse_string(cls, schema: str) -> any:
        raise NotImplementedError("Not implemented")
