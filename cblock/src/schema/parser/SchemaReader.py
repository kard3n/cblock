import logging
import os
import pickle

from db.DBManagerInterface import DBManagerInterface
from exceptions.SchemaParsingException import SchemaParsingException
from schema.Schema import SchemaType
from schema.parser.SchemaParserFactory import SchemaParserFactory
from utils import string_utils


# Parses all schema in the schema_definitions folder, and adds them to the database
class SchemaReader:
    db_manager: DBManagerInterface
    schema_location: str
    table_name: str

    def __init__(self, db_manager: DBManagerInterface, schema_location: str):
        self.db_manager = db_manager
        self.schema_location = schema_location

    def run(self):
        filename_list = os.listdir(f"{self.schema_location}/")

        self.db_manager.create_schema_table()

        data_to_insert = []
        for filename in filename_list:
            result: any = None
            if filename.endswith(".cbs"):
                try:
                    result = self.read_schema(
                        directory=self.schema_location, filename=filename
                    )
                except SchemaParsingException as e:
                    logging.warning(f"Exception parsing schema '{filename}: {e}'")
                if type(result) is not str:
                    data_to_insert.append(
                        self.read_schema(
                            directory=self.schema_location, filename=filename
                        )
                    )
                else:
                    raise SchemaParsingException(
                        f"The file {filename} could not be parsed: {result}"
                    )
        self.db_manager.insert_multiple(values=data_to_insert)

    # Returns a list, with the following content (order): schema name, url, schema type, underlying schema (as string)
    def read_schema(self, directory: str, filename: str) -> list | str:
        schema_type: str | None = None
        url: str | None = None
        path: str | None = None
        pickled_object: bytes | None = None
        factory: SchemaParserFactory = SchemaParserFactory()
        if directory.endswith("/"):
            directory = directory[:-1]
        with open(directory + "/" + filename) as file:
            file_content = file.read()

        pos: int = 0
        while pos < len(file_content):
            pos = string_utils.count_whitespaces(string=file_content, pos=pos)
            if file_content[pos:].startswith("url:"):
                pos = string_utils.count_whitespaces(string=file_content, pos=pos + 4)
                url = string_utils.extract_until_symbols(
                    string=file_content, symbols=["\n"], start_pos=pos, end_pos=None
                )
            if file_content[pos:].startswith("path:"):
                pos = string_utils.count_whitespaces(string=file_content, pos=pos + 5)
                path = string_utils.extract_until_symbols(
                    string=file_content, symbols=["\n"], start_pos=pos, end_pos=None
                )
            if file_content[pos:].startswith("type:"):
                pos = string_utils.count_whitespaces(string=file_content, pos=pos + 5)
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
                    pickled_object = pickle.dumps(
                        factory.getParser(schema_type).parse_string(file_content[pos:])
                    )
                except Exception as e:
                    return f"Underlying {schema_type} schema could not be parsed: {e}"
                break

            else:
                # invalid row, jump to next
                while file_content[pos] != "\n" and pos < len(file_content):
                    pos += 1

                pos += 1

        if url is None or path is None or schema_type is None or pickled_object is None:
            raise SchemaParsingException("Schema is missing fields.")

        return [filename[:-4], url, path, schema_type, pickled_object]
