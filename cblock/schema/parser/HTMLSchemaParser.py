import logging

import regex

from schema.ContentTag import ContentTag
from schema.html_schema.HTMLSchema import HTMLSchema
from schema.parser.SchemaParserInterface import SchemaParserInterface
from exceptions.SchemaParsingException import SchemaParsingException
from utils.string_utils import (
    count_whitespaces,
    extract_from_inbetween_symbol,
    count_continuous,
    split_safe,
)


class HTMLSchemaParser(SchemaParserInterface):

    @classmethod
    def parse_string(cls, schema: str) -> HTMLSchema:
        result: HTMLSchema = HTMLSchema()

        cleaned_list: list[str] = []

        for line in schema.split("\n"):
            if not (len(line.strip()) == 0 or line.lstrip().startswith("#")):
                cleaned_list.append(line)

        if len(cleaned_list) > 0:
            result.children = cls.parse_list(cleaned_list)
            pass
        else:
            raise SchemaParsingException("Schema can not be empty.")

        return result

    @classmethod
    def parse_element_single(cls, element: str) -> HTMLSchema:
        result = HTMLSchema()
        for item in split_safe(element, ","):
            # remove whitespaces
            item = item.lstrip()
            if item.startswith("html_tag:"):
                result.html_tag = regex.compile(
                    extract_from_inbetween_symbol(item[9:], "'")
                )
            elif item.startswith("recursive:"):
                if extract_from_inbetween_symbol(item[10:], "'").lower() == "false":
                    result.search_recursive = False
                elif extract_from_inbetween_symbol(item[10:], "'").lower() != "true":
                    logging.warning(
                        f"Recursive flag was neither 'False' nor 'True', applying default: {result.search_recursive}.\n\tElement: {element}"
                    )
            elif item.startswith("not_attrs:"):
                for not_attr in extract_from_inbetween_symbol(item[10:], "'").split():
                    result.not_attributes.append(not_attr)
            elif item.startswith("content_tags:"):
                for letter in extract_from_inbetween_symbol(item[13:], "'"):
                    if ContentTag(letter) in ContentTag:
                        result.content_tags.append(ContentTag[ContentTag(letter).name])
            elif item.startswith("edit_attrs:"):
                for pair in extract_from_inbetween_symbol(item[11:], "'").split():
                    split_result = pair.split(":")
                    if len(split_result) == 2:
                        result.attributes_to_edit[split_result[0]] = [
                            ContentTag[ContentTag(letter).name]
                            for letter in split_result[1]
                        ]
                    else:
                        logging.warning(
                            f"Could not extract attribute name or ContentTags from the following item: {pair}"
                        )
                        raise SchemaParsingException(
                            f"Could not extract attribute name or ContentTags from the following item: {pair}"
                        )

            elif item.startswith("embedded_schema:"):
                id_pos: int = count_whitespaces(item, 16) + 1

                num: str = ""
                while id_pos < len(item) and (item[id_pos].isalnum() or item[id_pos] in ["-", "_"]):
                    num += item[id_pos]
                    id_pos += 1

                if num != "":
                    result.embedded_schema = num
                else:
                    raise SchemaParsingException(
                        '"embedded_schema" tag must be followed by the name of another schema.'
                    )
            elif item.startswith("precondition:"):
                result.precondition = regex.compile(
                    extract_from_inbetween_symbol(item[13:], "'")
                )
            else:
                # If it is none of the before, it's an attribute
                colon_pos: int = item.find(":")

                if colon_pos < 0:
                    raise SchemaParsingException(f'"{item}" does not contain a value.')
                item_name = item[0:colon_pos]
                if item_name.endswith("!"):
                    result.attributes_multival[item_name[0:-1]] = (
                        extract_from_inbetween_symbol(
                            item[colon_pos + 1 :], "'"
                        ).split()
                    )
                else:
                    result.attributes_regex[item_name] = regex.compile(
                        extract_from_inbetween_symbol(item[colon_pos + 1 :], "'")
                    )

        if result.embedded_schema is not None and result.content_tags != []:
            raise SchemaParsingException(
                f"The resulting schema '{result}' has both an embedded schema and tags."
            )

        return result

    @classmethod
    def parse_list(cls, line_list: list) -> list:
        line_position: int = 0
        child_line_position: int
        result: list[HTMLSchema] = []

        while line_position < len(line_list):
            current_element: HTMLSchema
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
                    i: int = 0
                    while i < len(child_list):
                        child_list[i] = child_list[i][4:]
                        i = i + 1
                    # parse the list of children
                    current_element.children = cls.parse_list(child_list)

                line_position = child_line_position
            else:
                raise SchemaParsingException(
                    f'Invalid indent: "{line_list[line_position]}"'
                )

            result.append(current_element)
        return result
