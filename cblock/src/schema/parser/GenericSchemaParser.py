import regex

from schema.ContentTag import ContentTag
from schema.parser.SchemaParserInterface import SchemaParserInterface
from schema.generic_schema.GenericSchema import GenericSchema
from exceptions.SchemaParsingException import SchemaParsingException
from utils.Singleton import Singleton
from utils.string_utils import (
    jump_whitespaces,
    extract_from_inbetween_symbol,
    count_continuous,
)


class GenericSchemaParser(SchemaParserInterface):

    @classmethod
    def parse_string(cls, schema: str) -> GenericSchema:
        result: GenericSchema = GenericSchema()

        cleaned_list: list[str] = []

        for line in schema.split("\n"):
            if not line.isspace() or len(line) == 0:
                cleaned_list.append(line)

        if len(cleaned_list) > 0:
            result.children = cls.parse_list(cleaned_list)
            pass
        else:
            raise SchemaParsingException("Schema can not be empty.")

        return result

    @classmethod
    def parse_element_single(cls, element: str) -> GenericSchema:
        result = GenericSchema()
        for item in element.split(","):
            # remove whitespaces
            item = item[jump_whitespaces(item, 0) :]
            if item.startswith("pattern:"):
                result.pattern = regex.compile(
                    extract_from_inbetween_symbol(item[8:], '"')
                )
            elif item.startswith("tags:"):
                for letter in extract_from_inbetween_symbol(item[5:], '"'):
                    if ContentTag(letter) in ContentTag:
                        result.tags.append(ContentTag[ContentTag(letter).name])

            elif item.startswith("schema_id:"):
                id_pos: int = jump_whitespaces(item, 10)

                num: str = ""
                while id_pos < len(item) and item[id_pos].isalnum():
                    num += item[id_pos]
                    id_pos += 1

                if num != "":
                    result.embedded_schema = num
                else:
                    raise SchemaParsingException(
                        '"editor_id" tag must be followed by an ID.'
                    )
            else:
                raise SchemaParsingException(f'"{item} is not a valid field"')

        if result.embedded_schema is not None and result.tags != []:
            raise SchemaParsingException(
                f"The resulting schema '{result}' has both an embedded schema and tags."
            )

        return result

    @classmethod
    def parse_list(cls, line_list: list) -> list:
        line_position: int = 0
        child_line_position: int = 0
        result: list[GenericSchema] = []

        while line_position < len(line_list):
            current_element: GenericSchema
            if count_continuous(line_list[line_position], " ", 0) == 0:
                current_element = cls.parse_element_single(line_list[line_position])
                line_position += 1
                child_line_position = line_position

                while (
                    child_line_position < len(line_list)
                    and count_continuous(line_list[child_line_position], " ", 0) > 0
                ):
                    child_line_position += 1

                if child_line_position > line_position:
                    # remove indentation
                    child_list = line_list[line_position:child_line_position]
                    # TODO improve efficiency
                    for i in range(0, len(child_list)):
                        child_list[i] = child_list[i][4:]
                    # parse the list of children
                    current_element.children = cls.parse_list(child_list)

                line_position = child_line_position
            else:
                raise SchemaParsingException(
                    f'Invalid indent: "{line_list[line_position]}"'
                )

            result.append(current_element)
        return result

    @classmethod
    def parse_file(cls, filename: str):
        pass


"""    # expects a string, the first line must not have indentation (will be the current element)
    # The next lines must have an indentation of at least 4, to mark them as child elements
    @classmethod
    def parse_element_multi(cls, element: str) -> GenericSchemaElement:
        line_list = element.split("\n")

        if count_continuous(line_list[0], " ", 0) != 0:
            raise SchemaParsingException(
                f"Element has wrong indentation: {line_list[0]}"
            )

        result: GenericSchemaElement = cls.parse_element_single(line_list[0])

        if len(line_list) > 1:
            list_position: int = 1
            current_child_element: GenericSchemaElement
            while list_position < len(line_list):
                if count_continuous(line_list[list_position], " ", 0) == 4:
                    pass  # current_child_element = cls.parse_element_single(line_list[])"""


"""@classmethod
    def parse_string(cls, input: str) -> GenericSchema:
        result: GenericSchema = GenericSchema()
        position: int = 0

        current_element: GenericSchemaElement = GenericSchemaElement()
        for line in input.split("\n"):
            if count_continuous(string=line, symbol=" ", pos=0) == 0:
                for item in line.split(","):
                    # remove whitespaces
                    item = item[jump_whitespaces(item, 0)]
                    if item.startswith("open:"):
                        current_element.open = re.compile(
                            extract_from_inbetween_symbol(item[5:], '"')
                        )
                    if item.startswith("close:"):
                        current_element.close = re.compile(
                            extract_from_inbetween_symbol(item[5:], '"')
                        )
                    if item.startswith("action:"):
                        pass
                    if item.startswith("editor_id"):
                        id_pos: int = jump_whitespaces(item, 9)
                        num: str = ""
                        while item[id_pos].isnumeric():
                            num += item[id_pos]
                            id_pos += 1

                        if num != "":
                            current_element.editor_id = int(num)
                        else:
                            raise SchemaParsingException(
                                '"editor_id" tag must be followed by an ID.'
                            )
                    else:
                        raise SchemaParsingException(f'"{item} is not a valid field"')
            else:  # different indentation, needs recursion
                pass

        return current_element"""
