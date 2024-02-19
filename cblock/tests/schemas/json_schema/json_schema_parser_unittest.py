import unittest

from src.schema.ContentTag import ContentTag
from src.schema.json_schema.JSONSchema import JSONSchema, ValueType
from src.schema.json_schema.JSONSchemaParser import JsonSchemaParser


class TestJsonSchemaParser(unittest.TestCase):
    parser: JsonSchemaParser

    @classmethod
    def setUpClass(cls):
        cls.parser = JsonSchemaParser()

    def test_parse_one(self):
        schema: str = """{"second_name"e: {"value": "val"}, "firstName"p: "John", }"""
        assert self.parser.parse_schema(schema) == JSONSchema(
            tags=[],
            editor_id=None,
            value_type=ValueType.DICT,
            value={
                "firstName": JSONSchema(
                    tags=[ContentTag.PICTURE],
                    editor_id=None,
                    value_type=ValueType.LEAF,
                    value="John",
                ),
                "second_name": JSONSchema(
                    tags=[ContentTag.ELEMENT],
                    editor_id=None,
                    value_type=ValueType.DICT,
                    value={
                        "value": JSONSchema(
                            tags=[],
                            editor_id=None,
                            value_type=ValueType.LEAF,
                            value="val",
                        )
                    },
                ),
            },
        )

    def test_parse_two(self):
        schema: str = '''{"contained_list"e: [{"picture"p:"pic.jpg",}]}"'''
        assert self.parser.parse_schema(schema) == JSONSchema(
            tags=[],
            editor_id=None,
            value_type=ValueType.DICT,
            value={
                "contained_list": JSONSchema(
                    tags=[ContentTag.ELEMENT],
                    editor_id=None,
                    value_type=ValueType.LIST,
                    value=JSONSchema(
                        tags=[],
                        editor_id=None,
                        value_type=ValueType.DICT,
                        value={
                            "picture": JSONSchema(
                                tags=[ContentTag.PICTURE],
                                editor_id=None,
                                value_type=ValueType.LEAF,
                                value="pic.jpg",
                            )
                        },
                    ),
                )
            },
        )

    def test_parse_three(self):
        schema: str = (
            """{"items":[{"data":{"partenerData":{"summary"s:"This is a summary"}}}]}"""
        )
        assert self.parser.parse_schema(schema) == JSONSchema(
            tags=[],
            editor_id=None,
            value_type=ValueType.DICT,
            value={
                "items": JSONSchema(
                    tags=[],
                    editor_id=None,
                    value_type=ValueType.LIST,
                    value=JSONSchema(
                        tags=[],
                        editor_id=None,
                        value_type=ValueType.DICT,
                        value={
                            "data": JSONSchema(
                                tags=[],
                                editor_id=None,
                                value_type=ValueType.DICT,
                                value={
                                    "partenerData": JSONSchema(
                                        tags=[],
                                        editor_id=None,
                                        value_type=ValueType.DICT,
                                        value={
                                            "summary": JSONSchema(
                                                tags=[ContentTag.SUMMARY],
                                                editor_id=None,
                                                value_type=ValueType.LEAF,
                                                value="This is a summary",
                                            )
                                        },
                                    )
                                },
                            )
                        },
                    ),
                )
            },
        )

    def test_parse_four(self):
        schema: str = """{"summary"sa:"This is a summary"}"""
        assert self.parser.parse_schema(schema) == JSONSchema(
            tags=[],
            editor_id=None,
            value_type=ValueType.DICT,
            value={
                "summary": JSONSchema(
                    tags=[ContentTag.SUMMARY, ContentTag.ANALYZE],
                    editor_id=None,
                    value_type=ValueType.LEAF,
                    value="This is a summary",
                )
            },
        )
