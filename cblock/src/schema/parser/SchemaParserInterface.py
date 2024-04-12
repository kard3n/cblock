import abc
from abc import ABC


class SchemaParserInterface(ABC):
    # TODO make this and subclasses singleton
    @classmethod
    @abc.abstractmethod
    def parse_string(cls, schema: str) -> any:
        raise NotImplementedError("Not implemented")
