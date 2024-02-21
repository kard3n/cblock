import os

from src.db.DBManagerInterface import DBManagerInterface
from src.schema.Schema import SchemaType
from src.schema.SchemaParserFactory import SchemaParserFactory
from utils import string_utils


# Parses all schema in the schema_definitions folder, and adds them to the database
class SchemaReader:
    db_manager: DBManagerInterface
    schema_location: str
    table_name: str

    def __init__(self, db_manager: DBManagerInterface, schema_location: str):
        self.db_manager = db_manager
        self.schema_location = schema_location
        self.table_name = "cbschema"

    def run(self):
        filename_list = os.listdir(f"{self.schema_location}/")

        self.db_manager.create_schema_table()

        data_to_insert = []
        for filename in filename_list:
            if filename.endswith(".cbs"):
                data_to_insert.append(
                    self.read_schema(filename=self.schema_location + "/" + filename)
                )

        self.db_manager.insert_multiple(
            table_name=self.table_name, values=data_to_insert
        )

    # Returns a list, with the following content (order): schema name, url, schema type, underlying schema (as string)
    def read_schema(self, filename: str) -> list | str:
        schema_type: str | None = None
        url: str | None = None
        factory: SchemaParserFactory = SchemaParserFactory()
        with open(filename) as file:
            file_content = file.read()

        pos: int = 0
        while pos < len(file_content):
            pos = string_utils.jump_whitespaces(string=file_content, pos=pos)
            if file_content[pos:].startswith("url:"):
                pos = string_utils.jump_whitespaces(string=file_content, pos=pos + 4)
                url = string_utils.extract_until_symbols(
                    string=file_content, symbols=["\n"], start_pos=pos, end_pos=None
                )
            if file_content[pos:].startswith("type:"):
                pos = string_utils.jump_whitespaces(string=file_content, pos=pos + 5)
                schema_type = string_utils.extract_until_symbols(
                    string=file_content, symbols=["\n"], start_pos=pos, end_pos=None
                )
                # Check if the schema type is valid
                try:
                    SchemaType[SchemaType(schema_type).name]
                except ValueError:
                    return "Invalid schema type {}".format(schema_type)
            if file_content[pos:].startswith("schema:"):
                pos += 7
                while file_content[pos] != "\n":
                    pos += 1
                pos += 1

                # invoke a specific Schema Parser, depending on type, to check if the schema is valid
                try:
                    factory.getParser(schema_type).parse_string(file_content[pos:])
                except Exception as e:
                    return f"Underlying {schema_type} schema could not be parsed: {e}"
                pos = len(file_content)
            else:
                # invalid row, jump to next
                while file_content[pos] != "\n" and pos < len(file_content):
                    pos += 1

                pos += 1

        return [filename[:-4], url, schema_type, file_content[pos:]]
