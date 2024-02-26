from schema.parser.SchemaParserInterface import SchemaParserInterface
from schema.parser.GenericSchemaParser import GenericSchemaParser
from schema.parser.JSONSchemaParser import JSONSchemaParser
from utils.Singleton import Singleton


class SchemaParserFactory(metaclass=Singleton):
    def getParser(self, parser_type: str) -> SchemaParserInterface:
        if parser_type == "json":
            return JSONSchemaParser()
        if parser_type == "generic":
            return GenericSchemaParser()
