from dataclasses import dataclass
from enum import Enum

from schema.generic_schema.GenericSchema import GenericSchema
from schema.html_schema.HTMLSchema import HTMLSchema
from schema.json_schema.JSONSchema import JSONSchema


class SchemaType(str, Enum):
    GENERIC = "generic"
    JSON = "json"
    HTML = "html"


@dataclass
class Schema:
    id: str
    url: str = None
    path: str = None
    schema_type: SchemaType = None
    schema: JSONSchema | GenericSchema | HTMLSchema = None


# The name of the file is the schema's name. The ID is not specified by the user, the app automatically assigns one
# The user-definition also uses names, which when parsed get converted to IDs
"""
name: web_basic
url: basic_web.com/data
type: json
schema: # after the schema line, the definition of the underlying specialized schema is specified.
{}
"""
