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
        print("Reading schemas from '" + self.schema_location + "'.")
        filename_list = os.listdir(f"{self.schema_location}")

        self.db_manager.create_schema_table()

        data_to_insert = []
        for filename in filename_list:
            result: any = None
            if filename.endswith(".cbs"):
                try:
                    result = self.read_schema(
                        directory=self.schema_location, filename=filename
                    )

                    data_to_insert.append(result)

                except SchemaParsingException as e:
                    logging.warning(
                        f"The schema with ID {filename} could not be parsed and was therefore not added: {e}"
                    )

        self.db_manager.insert_multiple(values=data_to_insert)
        print("Finished reading schemas.")

    # Returns a list, with the following content (order): schema name, url, schema type, underlying schema (as string)
    def read_schema(self, directory: str, filename: str) -> list | str:
        factory: SchemaParserFactory = SchemaParserFactory()

        schema_type: str | None = None
        url: str | None = None
        path: str | None = None
        pickled_object: bytes | None = None

        found_underlying_schema: bool = False

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
                except ValueError as e:
                    raise SchemaParsingException(
                        f"Schema type {schema_type} is not recognized: {e}"
                    )
            if file_content[pos:].startswith("schema:"):
                pos += 7
                while pos < len(file_content) and file_content[pos] != "\n":
                    pos += 1
                pos += 1

                found_underlying_schema = True
                break

            else:
                # invalid row, jump to next
                while file_content[pos] != "\n" and pos < len(file_content):
                    pos += 1

                pos += 1

        if url is None or path is None or schema_type is None:
            missing_field_list: list[str] = []
            if url is None:
                missing_field_list.append("url")
            if path is None:
                missing_field_list.append("path")
            if schema_type is None:
                missing_field_list.append("schema_type")

            raise SchemaParsingException(
                f"Schema {filename} is missing the following fields: {missing_field_list}."
            )
        elif (
            found_underlying_schema is False
            or len(file_content[pos:].strip(" \n")) == 0
        ):
            raise SchemaParsingException(
                f"Schema {filename} is missing an underlying schema."
            )
        else:
            # parse schema and pickle the result
            try:
                parser = factory.get_parser(schema_type)
                pickled_object = pickle.dumps(parser.parse_string(file_content[pos:]))
            except Exception as e:
                raise SchemaParsingException(
                    f"Underlying {schema_type} schema could not be parsed: {e}"
                )

            return [filename[:-4], url, path, schema_type, pickled_object]
