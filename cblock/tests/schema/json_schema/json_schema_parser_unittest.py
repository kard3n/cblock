import unittest

from schema.ContentTag import ContentTag
from schema.json_schema.JSONSchema import JSONSchema, ValueType
from schema.json_schema.JSONSchemaParser import JSONSchemaParser


class TestJsonSchemaParser(unittest.TestCase):
    parser: JSONSchemaParser

    @classmethod
    def setUpClass(cls):
        cls.parser = JSONSchemaParser()

    def test_parse_one(self):
        schema: str = """{"second_name"e: {"value": "val"}, "firstName"p: "John", }"""
        assert self.parser.parse_string(schema) == JSONSchema(
            tags=[],
            schema_id=None,
            value_type=ValueType.DICT,
            value={
                "firstName": JSONSchema(
                    tags=[ContentTag.PICTURE],
                    schema_id=None,
                    value_type=ValueType.LEAF,
                    value="John",
                ),
                "second_name": JSONSchema(
                    tags=[ContentTag.ELEMENT],
                    schema_id=None,
                    value_type=ValueType.DICT,
                    value={
                        "value": JSONSchema(
                            tags=[],
                            schema_id=None,
                            value_type=ValueType.LEAF,
                            value="val",
                        )
                    },
                ),
            },
        )

    def test_parse_two(self):
        schema: str = '''{"contained_list"e: [{"picture"p:"pic.jpg",}]}"'''
        assert self.parser.parse_string(schema) == JSONSchema(
            tags=[],
            schema_id=None,
            value_type=ValueType.DICT,
            value={
                "contained_list": JSONSchema(
                    tags=[ContentTag.ELEMENT],
                    schema_id=None,
                    value_type=ValueType.LIST,
                    value=JSONSchema(
                        tags=[],
                        schema_id=None,
                        value_type=ValueType.DICT,
                        value={
                            "picture": JSONSchema(
                                tags=[ContentTag.PICTURE],
                                schema_id=None,
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
        assert self.parser.parse_string(schema) == JSONSchema(
            tags=[],
            schema_id=None,
            value_type=ValueType.DICT,
            value={
                "items": JSONSchema(
                    tags=[],
                    schema_id=None,
                    value_type=ValueType.LIST,
                    value=JSONSchema(
                        tags=[],
                        schema_id=None,
                        value_type=ValueType.DICT,
                        value={
                            "data": JSONSchema(
                                tags=[],
                                schema_id=None,
                                value_type=ValueType.DICT,
                                value={
                                    "partenerData": JSONSchema(
                                        tags=[],
                                        schema_id=None,
                                        value_type=ValueType.DICT,
                                        value={
                                            "summary": JSONSchema(
                                                tags=[ContentTag.SUMMARY],
                                                schema_id=None,
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
        assert self.parser.parse_string(schema) == JSONSchema(
            tags=[],
            schema_id=None,
            value_type=ValueType.DICT,
            value={
                "summary": JSONSchema(
                    tags=[ContentTag.SUMMARY, ContentTag.ANALYZE],
                    schema_id=None,
                    value_type=ValueType.LEAF,
                    value="This is a summary",
                )
            },
        )

    def test_parse_five(self):
        schema: str = """{"embedded"(otherSchema):"Some interesting text"}"""
        assert self.parser.parse_string(schema) == JSONSchema(
            tags=[],
            schema_id=None,
            value_type=ValueType.DICT,
            value={
                "embedded": JSONSchema(
                    tags=[],
                    schema_id="otherSchema",
                    value_type=ValueType.LEAF,
                    value="Some interesting text",
                )
            },
        )
