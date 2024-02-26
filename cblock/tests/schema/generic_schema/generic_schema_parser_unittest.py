import unittest

from regex import regex

from schema.ContentTag import ContentTag
from schema.generic_schema.GenericSchema import GenericSchema
from schema.generic_schema.GenericSchemaParser import GenericSchemaParser


class TestGenericSchemaParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser: GenericSchemaParser = GenericSchemaParser()

    def test_parse_string_one(self):
        schema: str = r'pattern:"bb(?P<content>hola)bb", tags:"a", schema_id: 20'
        assert (
            self.parser.parse_string(schema).__str__()
            == GenericSchema(
                pattern=None,
                tags=[],
                schema_id=None,
                children=[
                    GenericSchema(
                        pattern=regex.Regex("bb(?P<content>hola)bb"),
                        tags=[ContentTag.ANALYZE],
                        schema_id=20,
                        children=None,
                    )
                ],
            ).__str__()
        )

    def test_parse_string_two(self):
        schema: str = r'''pattern:"bb(?P<content>xxholaxx)bb", tags:"e", schema_id: 20
    pattern:"xx(?P<content>hola)xx", tags:"at"'''
        assert (
            self.parser.parse_string(schema).__str__()
            == GenericSchema(
                pattern=None,
                tags=[],
                schema_id=None,
                children=[
                    GenericSchema(
                        pattern=regex.Regex("bb(?P<content>xxholaxx)bb"),
                        tags=[ContentTag.ELEMENT],
                        schema_id=20,
                        children=[
                            GenericSchema(
                                pattern=regex.Regex("xx(?P<content>hola)xx"),
                                tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                                schema_id=None,
                                children=None,
                            )
                        ],
                    )
                ],
            ).__str__()
        )
