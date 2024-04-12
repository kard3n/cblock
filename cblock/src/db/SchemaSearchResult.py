from dataclasses import dataclass

from schema.generic_schema.GenericSchema import GenericSchema
from schema.html_schema.HTMLSchema import HTMLSchema
from schema.json_schema.JSONSchema import JSONSchema


@dataclass
class SchemaSearchResult:
    schema_type: str  # type of the schema
    schema: HTMLSchema | JSONSchema | GenericSchema  # A schema
