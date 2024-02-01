from src.content_editor.editors.json_editor.ContentTag import ContentTag
from src.content_editor.editors.json_editor.ElementContainer import ElementContainer, ValueType
from utils.SchemaParsingException import SchemaParsingException

class JsonSchemaParser:

    @classmethod
    def parse_schema(cls, schema: str) -> dict:
        result: dict = {}
        item_name: str = ''
        element_container: ElementContainer = ElementContainer()

        pos: int = 0

        # jump all linebreaks and whitespaces
        while schema[pos] in ['\n', " "]:
            pos += 1

        if schema[pos] == '"':
            pos += 1
            while schema[pos] != '"' and schema[pos -1] != '\\':
                item_name += schema[pos]
                pos += 1

        if schema[pos] != '"':
            raise SchemaParsingException(f"Unexpected character {schema[pos]} at position {pos}")


        result[item_name] = cls.__parse_schema_element(schema[pos +1:], comes_with_tags=True)

        return result

    # converts the received element to an ElementContainer. element must start with the tags followed by a ":"
    # and then the content (list, dict or string)
    # if element does not start with tags followed by a ':', then comes_with_tags needs to be set to False
    @classmethod
    def __parse_schema_element(cls, element: str, inherited_tags: list[ContentTag] = None,
                             comes_with_tags: bool = True) -> ElementContainer:
        element_container: ElementContainer = ElementContainer()

        # add inherited tags to initially empty tag list
        if inherited_tags is not None:
            element_container.tags = inherited_tags

        pos: int = 0


        # if element has tags at the beginning, we add them
        if comes_with_tags:
            while element[pos] != ':':
                if ContentTag(element[pos]) in ContentTag:
                    element_container.tags.append(ContentTag[ContentTag(element[pos]).name])
                    pos += 1
                else:
                    raise SchemaParsingException(f'Invalid content tag \"schema[pos]\" at position {pos}')

            # jump over the ":"
            pos += 1
        # jump all linebreaks and whitespaces
        while element[pos] in ['\n', " "]:
            pos += 1
        # it's text, we get it and add it as value
        if element[pos] == '"':
            element_container.value = ""
            element_container.value_type = ValueType.LEAF
            pos += 1
            # add to value until a not-escaped quotation mark is found
            while element[pos] != '"' and element[pos - 1] != '\\':
                element_container.value += element[pos]
                pos += 1

        # it's a list, we get the content and parse it to ElementContainer
        # a list, since all elements have the same structure, contains only one element that will get parsed
        elif element[pos] == '[':
            element_container.value = ElementContainer()
            element_container.value_type = ValueType.LIST
            open_dividers: int = 1  # counts the currently non-closed dividers such as {} and []
            child_value: str = ''

            pos += 1

            # jump all linebreaks and whitespaces
            while element[pos] in ['\n', " "]:
                pos += 1
            while open_dividers > 0:
                if element[pos] in ['[', '{'] and element[pos - 1] != '\\':
                    open_dividers += 1
                elif element[pos] in [']', '}'] and element[pos - 1] != '\\':
                    open_dividers -= 1

                if open_dividers > 0:
                    child_value += element[pos]

                pos += 1
            element_container.value = cls.__parse_schema_element(child_value, element_container.tags, False)
        # it's a dictionary. all elements need to be parsed to ElementContainer and saved
        # with their respective names
        elif element[pos] == '{':
            element_container.value_type = ValueType.DICT
            element_container.value = {}
            open_dividers: int = 1  # counts the currently non-closed dividers such as {} and []
            current_child_value: str = ''
            current_item_name: str = ''

            # jump '{'
            pos += 1

            # jump all linebreaks and whitespaces
            while element[pos] in ['\n', " "]:
                pos += 1

            print(8)
            # get the name
            if element[pos] == '"':
                pos += 1
                while element[pos] != '"' and element[pos - 1] != '\\':
                    current_item_name += element[pos]
                    pos += 1



            if element[pos] != '"':
                raise SchemaParsingException(f"Unexpected character {element[pos]} at position {pos}")

            # jump remaining '"'
            pos += 1

            # jump all linebreaks and whitespaces
            while element[pos] in ['\n', " "]:
                pos += 1

            # extract all text until the comma that denotes the end of the element
            while open_dividers > 0:
                if element[pos] in ['[', '{'] and element[pos - 1] != '\\':
                    open_dividers += 1
                elif element[pos] in [']', '}'] and element[pos - 1] != '\\':
                    open_dividers -= 1

                if open_dividers > 0:
                    current_child_value += element[pos]
                if open_dividers == 1 and element[pos] == ',':
                    print(element[0:pos])
                    print(element[pos:])
                    print(f"current_child_value 1: {current_child_value}")
                    element_container.value[current_item_name] = (
                        cls.__parse_schema_element(current_child_value,
                                                    element_container.tags,
                                                    True))

                pos += 1

        return element_container