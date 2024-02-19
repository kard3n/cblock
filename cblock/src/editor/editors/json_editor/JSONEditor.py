import json
import logging

from src.content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from src.content_factory.Content import Content
from src.content_factory.ContentFactory import ContentFactory
from src.editor.EditorInterface import EditorInterface
from src.schema.ContentTag import ContentTag
from src.schema.json_schema.JSONSchema import JSONSchema, ValueType


class JSONEditor(EditorInterface):
    content_analyzer: ContentAnalyzerInterface
    content_factory: ContentFactory

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
    ) -> None:
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory

    def edit(self, input_raw: str, schema: JSONSchema) -> str:
        try:
            input_decoded: dict = json.loads(input_raw)
            return self.edit_parsed(input_decoded, schema).__str__()

        except json.decoder.JSONDecodeError as e:
            logging.warning(f"DecodeError at position: {e.pos}")

    def edit_parsed(self, input_parsed: any, schema: JSONSchema) -> dict:
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

            # If it's a leaf, we don't need to do anything
            return input_parsed

        return input_parsed

    def extract_content(self, input_value, schema: JSONSchema) -> str:
        result: str = ""

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
