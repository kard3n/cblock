import unittest

from pytest import raises
from regex import regex

from exceptions.SchemaParsingException import SchemaParsingException
from schema.ContentTag import ContentTag
from schema.generic_schema.GenericSchema import GenericSchema
from schema.parser.GenericSchemaParser import GenericSchemaParser


class TestGenericSchemaParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser: GenericSchemaParser = GenericSchemaParser()

    def test_parse_string_one(self):
        schema: str = r"pattern:'bb(?P<content>hola)bb', tags:'a'"
        assert self.parser.parse_string(schema) == GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("bb(?P<content>hola)bb"),
                    tags=[ContentTag.ANALYZE],
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

    def test_parse_string_two(self):
        schema: str = r"""pattern:'bb(?P<content>xxholaxx)bb', tags:'e'
    pattern:'xx(?P<content>hola)xx', tags:'at'"""
        self.assertEqual(GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("bb(?P<content>xxholaxx)bb"),
                    tags=[ContentTag.CONTAINER],
                    embedded_schema=None,
                    children=[
                        GenericSchema(
                            pattern=regex.Regex("xx(?P<content>hola)xx"),
                            tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                            embedded_schema=None,
                            children=[],
                        )
                    ],
                )
            ],
        ), self.parser.parse_string(schema))

    def test_parse_embedded_schema(self):
        schema: str = r"""pattern:'xx(?P<content>hola)xx', tags:'', schema_id:'example_schema-'"""
        self.assertEqual(GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[GenericSchema(
                            pattern=regex.Regex("xx(?P<content>hola)xx"),
                            tags=[],
                            embedded_schema="example_schema-",
                            children=[],
                        )
            ],
        ), self.parser.parse_string(schema))

    def test_parse_string_multi_root(self):
        schema: str = r"""pattern:'__(?P<content>hola)__', tags:'e'
pattern:'xx(?P<content>hola)xx', tags:'e'"""
        assert self.parser.parse_string(schema) == GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("__(?P<content>hola)__"),
                    tags=[ContentTag.CONTAINER],
                    embedded_schema=None,
                    children=[],
                ),
                GenericSchema(
                    pattern=regex.Regex("xx(?P<content>hola)xx"),
                    tags=[ContentTag.CONTAINER],
                    embedded_schema=None,
                    children=[],
                ),
            ],
        )

    def test_parse_string_conflict_tags_and_embedded(self):
        schema: str = r"pattern:'bb(?P<content>hola)bb', tags:'a', schema_id:'example_schema'"

        with raises(SchemaParsingException):
            self.parser.parse_string(schema)
