from enum import Enum

from src.schema.SchemaParserInterface import SchemaParserInterface
from src.schema.generic_schema.GenericSchemaParser import GenericSchemaParser
from src.schema.json_schema import JSONSchemaParser


class SchemaParserFactory:
    def getParser(self, parser_type: str) -> SchemaParserInterface:
        if parser_type == "json":
            return JSONSchemaParser()
        if parser_type == "generic":
            return GenericSchemaParser()
