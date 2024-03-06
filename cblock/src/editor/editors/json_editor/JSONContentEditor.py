import json
import logging

from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.json_schema.JSONSchema import JSONSchema, ValueType


class JSONContentEditor(ContentEditorInterface):
    content_analyzer: ContentAnalyzerInterface
    content_factory: ContentFactory

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
        schema_factory: SchemaFactory,
        editor_factory: ContentEditorFactory,
    ) -> None:
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory
        self.editor_factory = editor_factory
        self.schema_factory = schema_factory

    def edit(self, input_raw: str, schema: JSONSchema) -> str:
        try:
            input_decoded: dict = json.loads(input_raw)
            return self.edit_parsed(input_decoded, schema).__str__()

        except json.decoder.JSONDecodeError as e:
            logging.warning(f"DecodeError at position: {e.pos}")

    # Only returns a string if the passed element is a leaf, and an embedded schema was specified
    def edit_parsed(self, input_parsed: any, schema: JSONSchema) -> dict | str:
        if ContentTag.ELEMENT in schema.tags:  # we got an element, so we analyze it
            if schema.value_type == ValueType.DICT:
                if self.content_analyzer.analyze(
                    self.extract_content(input_parsed, schema)
                ):
                    # The analyzer returned true, so the content gets replaced. Last argument is the content that should be inserted
                    input_parsed = self.apply_action(
                        input_parsed, schema, self.content_factory.get_content()
                    )

            elif schema.value_type == ValueType.LIST:
                for item in input_parsed:
                    if self.content_analyzer.analyze(
                        self.extract_content(item, schema.value[0])
                    ):  # The analyzer returned true, so the content gets replaced. Last argument is the content that should be inserted
                        input_parsed[input_parsed.index(item)] = self.apply_action(
                            item,
                            schema.value[0],
                            self.content_factory.get_content(),
                        )
            elif schema.value_type == ValueType.LEAF:
                if self.content_analyzer.analyze(input_parsed):
                    input_parsed = self.apply_action(
                        input_parsed,
                        schema,
                        self.content_factory.get_content(),
                    )
        else:
            if schema.value_type == ValueType.DICT:
                for key in schema.value:
                    input_parsed[key] = self.edit_parsed(
                        input_parsed[key], schema.value[key]
                    )
            elif schema.value_type == ValueType.LIST:
                for item in input_parsed:
                    input_parsed[input_parsed.index(item)] = self.edit_parsed(
                        item, schema.value[0]
                    )
            elif schema.value_type == ValueType.LEAF:
                # If it's a leaf, we just need to check if an embedded editor has been specified and, if so, edit
                if schema.embedded_schema is not None and type(input_parsed) not in [
                    list,
                    dict,
                ]:
                    input_parsed = self.__get_editor_by_schema_id(
                        schema.embedded_schema
                    ).edit(
                        input_raw=input_parsed,
                        schema=self.__get_schema_by_id(schema.embedded_schema),
                    )
                elif schema.embedded_schema is not None:
                    logging.info(
                        f"An embedded schema was found, but the content was not a leaf. Schema: {schema}"
                    )

        return input_parsed

    def extract_content(self, input_value, schema: JSONSchema) -> str:
        result: str = ""

        # If an embedded schema is specified, it gets applied instead
        if schema.embedded_schema is not None:
            return self.__get_editor_by_schema_id(
                schema.embedded_schema
            ).extract_content(
                input_value=input_value,
                schema=self.__get_schema_by_id(schema.embedded_schema),
            )

        if schema.value_type == ValueType.DICT:
            for key in schema.value:
                result += self.extract_content(input_value[key], schema.value[key])
        elif schema.value_type == ValueType.LIST:
            for elem in input_value:
                # This is correct, in the case of lists, the value is directly a JSONSchema
                result += self.extract_content(elem, schema.value)
        elif schema.value_type == ValueType.LEAF:
            if ContentTag.ANALYZE in schema.tags:
                result += input_value

        return result

    def apply_action(self, input_value, schema: JSONSchema, content: Content) -> any:
        # If an embedded schema is specified, input_value must be a leaf (str, int, ...)
        if schema.embedded_schema is not None and type(input_value) not in [list, dict]:
            input_value = self.__get_editor_by_schema_id(
                schema_id=schema.embedded_schema
            ).apply_action(
                content=content,
                input_value=input_value,
                schema=self.__get_schema_by_id(schema.embedded_schema),
            )
        elif schema.embedded_schema is not None:
            logging.info(
                f"An embedded schema was found, but the content was not a leaf. Schema: {schema}"
            )
        else:  # No embedded schema has been specified
            if schema.value_type == ValueType.DICT:
                for key in schema.value:
                    input_value[key] = self.apply_action(
                        input_value=input_value[key],
                        schema=schema.value[key],
                        content=content,
                    )
            elif schema.value_type == ValueType.LIST:
                for elem in input_value:
                    # This is correct, in the case of lists, the value is directly a JSONSchema
                    input_value[input_value.index(elem)] = self.apply_action(
                        input_value=elem, schema=schema.value, content=content
                    )
            elif schema.value_type == ValueType.LEAF:
                if ContentTag.TITLE in schema.tags:
                    input_value = content.title
                elif ContentTag.FULL_CONTENT in schema.tags:
                    input_value = content.full
                elif ContentTag.VIDEO in schema.tags:
                    input_value = content.video
                elif ContentTag.PICTURE in schema.tags:
                    input_value = content.picture
                elif ContentTag.SUMMARY in schema.tags:
                    input_value = content.summary

        return input_value

    def __get_editor_by_schema_id(self, schema_id) -> ContentEditorInterface:
        return self.editor_factory.get_content_editor_by_schema_id(schema_id=schema_id)

    def __get_schema_by_id(self, schema_id) -> any:
        return self.schema_factory.get_schema_by_id(schema_id=schema_id)
