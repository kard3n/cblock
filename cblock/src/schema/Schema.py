from dataclasses import dataclass
from enum import Enum

from src.schema.generic_schema.GenericSchema import GenericSchema
from src.schema.json_schema.JSONSchema import JSONSchema


class SchemaType(str, Enum):
    GENERIC = "generic"
    JSON = "json"


@dataclass
class Schema:
    id: str
    url: str = None
    schema_type: SchemaType = None
    schema: JSONSchema | GenericSchema = None


# The name of the file is the schema's name. The ID is not specified by the user, the app automatically assigns one
# The user-definition also uses names, which when parsed get converted to IDs
"""
name: web_basic
url: basic_web.com/data
type: json
schema: # after the schema line, the definition of the underlying specialized schema is specified.
{}
"""
