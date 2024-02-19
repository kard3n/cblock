from dataclasses import dataclass
from enum import Enum

from src.schema.generic_schema.GenericSchema import GenericSchema
from src.schema.json_schema.JSONSchema import JSONSchema


class SchemaType(str, Enum):
    GENERIC = "generic"
    JSON = "json"


@dataclass
class Schema:
    name: str
    url: str
    id: str
    type: SchemaType
    schema: JSONSchema | GenericSchema
