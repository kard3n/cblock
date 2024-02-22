from schema.SchemaParserInterface import SchemaParserInterface
from schema.generic_schema.GenericSchemaParser import GenericSchemaParser
from schema.json_schema.JSONSchemaParser import JSONSchemaParser


class SchemaParserFactory:
    # TODO make parsers singleton
    def getParser(self, parser_type: str) -> SchemaParserInterface:
        if parser_type == "json":
            return JSONSchemaParser()
        if parser_type == "generic":
            return GenericSchemaParser()
