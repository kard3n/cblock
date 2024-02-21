import abc
from abc import ABC, abstractmethod

from src.schema.json_schema.JSONSchema import JSONSchema


class SchemaParserInterface(ABC):
    @classmethod
    @abc.abstractmethod
    def parse_string(cls, schema: str) -> any:
        raise NotImplementedError("Not implemented")
