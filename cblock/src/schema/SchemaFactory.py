from db.DBManagerInterface import DBManagerInterface
from db.SchemaSearchResult import SchemaSearchResult
from schema.parser.SchemaParserFactory import SchemaParserFactory
from utils.Singleton import Singleton


class SchemaFactory(metaclass=Singleton):
    def __init__(self, db_manager: DBManagerInterface):
        self.parser_factory = SchemaParserFactory()
        self.db_manager = db_manager

    # returns a parsed schema given its ID
    def get_schema_by_id(self, schema_id: str) -> any:
        schema_search_result: SchemaSearchResult = self.db_manager.get_schema(schema_id)

        return self.parser_factory.getParser(
            schema_search_result.schema_type
        ).parse_string(schema_search_result.schema)
