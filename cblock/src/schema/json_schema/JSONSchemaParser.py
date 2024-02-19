from src.schema.ContentTag import ContentTag
from src.schema.json_schema.JSONSchema import JSONSchema, ValueType
from src.exceptions.SchemaParsingException import SchemaParsingException
from utils.string_utils import jump_whitespaces_linebreaks


class JsonSchemaParser:

    @classmethod
    def parse_schema(cls, schema: str) -> JSONSchema:
        pos: int = 0

        jump_whitespaces_linebreaks(schema, pos)

        return cls.__parse_schema_element(schema[pos:])

    # converts the received element to an ElementContainer. element must start with the tags followed by a ":"
    # and then the content (list, dict or string)
    # if element does not start with tags followed by a ':', then comes_with_tags needs to be set to False
    @classmethod
    def __parse_schema_element(
        cls, element: str, inherited_tags: list[ContentTag] = None
    ) -> JSONSchema:
        element_container: JSONSchema = JSONSchema()

        # add inherited tags to initially empty tag list. Disables dor now, maybe remove later
        # if inherited_tags is not None:
        #    element_container.tags = deepcopy(inherited_tags)

        pos: int = 0

        # check if the passed element has tags, if it does adds them
        if element[pos].isalpha() or element[pos] == ":":
            while element[pos] != ":":
                if ContentTag(element[pos]) in ContentTag:
                    element_container.tags.append(
                        ContentTag[ContentTag(element[pos]).name]
                    )
                    pos += 1
                elif element[pos].isnumeric():
                    editor_id: str = ""
                    while element[pos].isnumeric():
                        editor_id += element[pos]
                        pos += 1
                    element_container.editor_id = int(editor_id)

                else:
                    raise SchemaParsingException(
                        f'Invalid content tag "{element[pos]}" at position {pos}'
                    )

            # jump ':'
            pos += 1

        pos = jump_whitespaces_linebreaks(element, pos)

        # tags have been read, now check for type of the value
        # it starts with a quote, so it must be a string
        if element[pos] == '"':
            element_container.value_type = ValueType.LEAF
            element_container.value = ""

            # jump quote
            pos += 1

            while (
                pos < len(element) and element[pos] != '"' and element[pos - 1] != "\\"
            ):
                element_container.value += element[pos]
                pos += 1

            # jump quote
            pos += 1

            if pos < len(element):
                raise SchemaParsingException(
                    f'Unexpected character "{element[pos]}" at relative position {pos}'
                )

        # starts with a bracket, must be a list
        elif element[pos] == "[":
            element_container.value_type = ValueType.LIST
            current_value: str = ""
            opened_lists: int = 1
            while not (
                element[pos] == "]" and element[pos - 1] != "\\" and opened_lists == 0
            ):
                pos += 1

                if element[pos] == "[" and element[pos - 1] != "\\":
                    opened_lists += 1
                elif element[pos] == "]" and element[pos - 1] != "\\":
                    opened_lists -= 1

                current_value += element[pos]
            element_container.value = cls.__parse_schema_element(
                current_value[0 : len(current_value) - 1], element_container.tags
            )

        # starts with a curly bracket, must be a dictionary
        elif element[pos] == "{":
            element_container.value_type = ValueType.DICT
            element_container.value = {}
            open_dividers: int = 0

            current_value: str = ""
            current_name: str = ""

            current_divider_open: str = ""

            current_divider_close: str = ""

            # jump curly bracket
            pos += 1

            while not (
                element[pos] == "}" and element[pos - 1] != "\\" and open_dividers == 0
            ):
                if element[pos] == "}" and element[pos - 1] != "\\":
                    open_dividers += 1
                elif element[pos] == "{" and element[pos - 1] != "\\":
                    open_dividers -= 1

                pos = jump_whitespaces_linebreaks(element, pos)

                # if there's a comma, jump over it
                if element[pos] == ",":
                    pos += 1
                    pos = jump_whitespaces_linebreaks(element, pos)

                # found a quotation mark, so we got a new name and therefore a new element
                if element[pos] == '"':
                    # extract name
                    end_of_name: int = cls.__get_name(element, pos)
                    current_name = element[pos + 1 : end_of_name]

                    # extract value, +1 to jump over quotation mark
                    pos = end_of_name + 1

                    pos = jump_whitespaces_linebreaks(element, pos)

                    while pos < len(element) and not element[pos] in ['"', "{", "["]:

                        current_value += element[pos]
                        pos += 1

                    if not element[pos] in ['"', "{", "["]:
                        raise ValueError(
                            f"The following character does not correspond to a type: {element[pos]}"
                        )

                    current_divider_open = element[pos]

                    if current_divider_open == "{":
                        current_divider_close = "}"
                    elif current_divider_open == '"':
                        current_divider_close = '"'
                    elif current_divider_open == "[":
                        current_divider_close = "]"

                    open_dividers = 0

                    if current_divider_open == '"':
                        current_value += element[pos]
                        pos += 1
                        while not (
                            element[pos] == current_divider_close
                            and element[pos - 1] != "\\"
                        ):
                            current_value += element[pos]
                            pos += 1

                        # add close divider
                        current_value += element[pos]
                        pos += 1
                    else:
                        # add to child value until end of current value
                        pos -= 1
                        while not (
                            open_dividers == 0
                            and element[pos] == current_divider_close
                            and element[pos - 1] != "\\"
                        ):
                            pos += 1
                            if (
                                element[pos] == current_divider_close
                                and element[pos - 1] != "\\"
                            ):
                                open_dividers -= 1
                            elif (
                                element[pos] == current_divider_open
                                and element[pos - 1] != "\\"
                            ):
                                open_dividers += 1

                            current_value += element[pos]

                        pos += 1

                element_container.value[current_name] = cls.__parse_schema_element(
                    current_value, element_container.tags
                )
                current_value = ""

                # remove comma after last element, if it exists.
                # Otherwise, the loop won't be able to check for closing the divider '}'
                pos = jump_whitespaces_linebreaks(element, pos)
                if element[pos] == ",":
                    pos += 1
                pos = jump_whitespaces_linebreaks(element, pos)

        else:
            raise SchemaParsingException(
                f"Symbol does not correspond to a type: {element[pos]}"
            )

        return element_container

    @classmethod
    def __get_name(cls, input: str, start_pos: int) -> int:
        pos: int = start_pos

        pos = jump_whitespaces_linebreaks(input, pos)

        if input[pos] != '"':
            raise SchemaParsingException(
                f'Could not determine beginning of name "{input[start_pos:]}". No '
                + "quotation mark could be found."
            )

        # jump quotation mark
        pos += 1

        while pos < len(input) and not (input[pos] == '"' and input[pos - 1] != "\\"):
            pos += 1

        if input[pos] != '"':
            raise SchemaParsingException(
                f'Could not determine ending of name "{input[start_pos:]}".'
            )

        return pos
