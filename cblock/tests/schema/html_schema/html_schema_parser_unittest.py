import unittest

from pytest import raises
from regex import regex

from exceptions.SchemaParsingException import SchemaParsingException
from schema.ContentTag import ContentTag
from schema.html_schema.HTMLSchema import HTMLSchema
from schema.parser.HTMLSchemaParser import HTMLSchemaParser


class TestHTTPSchemaParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser: HTMLSchemaParser = HTMLSchemaParser()

    def test_parse_string_single_line(self):
        schema: str = (
            r"html_tag:'a', content_tags:'a', edit_attrs:'test:at var:d', href: 'https:\/\/example\.com'"
        )
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE],
                    attributes_to_edit={
                        "test": [ContentTag.ANALYZE, ContentTag.TITLE],
                        "var": [ContentTag.DELETE],
                    },
                    attributes={"href": regex.compile(r"https:\/\/example\.com")},
                    embedded_schema=None,
                    children=None,
                )
            ],
        )

    def test_parse_string_multiple_children(self):
        schema: str = r"""html_tag:'a', content_tags:'e', edit_attrs:'test:e', href: 'https:\/\/example\.com'
    html_tag:'b', content_tags:'at', edit_attrs:'random:at', class: 'headline'
    html_tag:'span', content_tags:'as', class: 'summary'"""
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.CONTAINER],
                    attributes={"href": regex.compile(r"https:\/\/example\.com")},
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("b"),
                            content_tags=[ContentTag.CONTAINER],
                            attributes_to_edit={
                                "test": [ContentTag.ANALYZE, ContentTag.TITLE],
                                "var": [ContentTag.ANALYZE],
                            },
                            attributes={"class": regex.compile(r"headline")},
                            embedded_schema=None,
                            children=None,
                        ),
                        HTMLSchema(
                            html_tag=regex.compile("span"),
                            content_tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                            attributes={"class": regex.compile(r"summary")},
                            embedded_schema=None,
                            children=None,
                        ),
                    ],
                )
            ],
        )
