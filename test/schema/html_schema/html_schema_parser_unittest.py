import unittest

from regex import regex

from schema.ContentTag import ContentTag
from schema.html_schema.HTMLSchema import HTMLSchema, AttributeDefinition
from schema.parser.HTMLSchemaParser import HTMLSchemaParser


class TestHTTPSchemaParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser: HTMLSchemaParser = HTMLSchemaParser()

    def test_parse_string_single_line(self):
        schema: str = (
            r"html_tag:'a', content_tags:'a', edit_attrs:'test:at var:d', not_attrs:'bad attr', href: 'https:\/\/example\.com'"
        )
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes=[],
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE],
                    attributes_to_edit={
                        "test": [ContentTag.ANALYZE, ContentTag.TITLE],
                        "var": [ContentTag.DELETE],
                    },
                    attributes=[
                        AttributeDefinition(
                            name="href",
                            value=regex.compile(r"https:\/\/example\.com"),
                            is_not_regex=False,
                        )
                    ],
                    not_attributes=["bad", "attr"],
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

    def test_parse_string_single_line_forbidden_attribute(self):
        schema: str = (
            r"html_tag:'a', content_tags:'a', edit_attrs:'test:at var:d', href: 'https:\/\/example\.com'"
        )
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes=[],
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE],
                    attributes_to_edit={
                        "test": [ContentTag.ANALYZE, ContentTag.TITLE],
                        "var": [ContentTag.DELETE],
                    },
                    attributes=[
                        AttributeDefinition(
                            name="href",
                            value=regex.compile(r"https:\/\/example\.com"),
                            is_not_regex=False,
                        )
                    ],
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

    def test_parse_string_multiple_children(self):
        schema: str = r"""html_tag:'a', content_tags:'e', edit_attrs:'test:o', href: 'https:\/\/example\.com'
    html_tag:'b', content_tags:'at', edit_attrs:'random:at', class: 'headline'
    html_tag:'span', content_tags:'as', class: 'summary'"""
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes=[],
            attributes_to_edit={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.CONTAINER],
                    attributes_to_edit={"test": [ContentTag.ORIGIN]},
                    attributes=[
                        AttributeDefinition(
                            name="href",
                            value=regex.compile(r"https:\/\/example\.com"),
                            is_not_regex=False,
                        )
                    ],
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("b"),
                            content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                            attributes_to_edit={
                                "random": [ContentTag.ANALYZE, ContentTag.TITLE],
                            },
                            attributes=[
                                AttributeDefinition(
                                    name="class",
                                    value=regex.compile(r"headline"),
                                    is_not_regex=False,
                                )
                            ],
                            embedded_schema=None,
                            children=[],
                        ),
                        HTMLSchema(
                            html_tag=regex.compile("span"),
                            content_tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                            attributes=[
                                AttributeDefinition(
                                    name="class",
                                    value=regex.compile(r"summary"),
                                    is_not_regex=False,
                                )
                            ],
                            embedded_schema=None,
                            children=[],
                        ),
                    ],
                )
            ],
        )

    def test_parse_string_multiple_children_non_recursive(self):
        schema: str = r"""html_tag:'a', recursive:'False', content_tags:'e', href: 'https:\/\/example\.com'
    html_tag:'b', content_tags:'at', recursive:'True' ,class: 'headline'
    html_tag:'span', content_tags:'as', recursive:'False', class: 'summary'"""
        assert self.parser.parse_string(schema) == HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes=[],
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.CONTAINER],
                    attributes=[
                        AttributeDefinition(
                            name="href",
                            value=regex.compile(r"https:\/\/example\.com"),
                            is_not_regex=False,
                        )
                    ],
                    search_recursive=False,
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("b"),
                            content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                            search_recursive=True,
                            attributes_to_edit={},
                            attributes=[
                                AttributeDefinition(
                                    name="class",
                                    value=regex.compile(r"headline"),
                                    is_not_regex=False,
                                )
                            ],
                            embedded_schema=None,
                            children=[],
                        ),
                        HTMLSchema(
                            html_tag=regex.compile("span"),
                            search_recursive=False,
                            content_tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                            attributes=[
                                AttributeDefinition(
                                    name="class",
                                    value=regex.compile(r"summary"),
                                    is_not_regex=False,
                                )
                            ],
                            embedded_schema=None,
                            children=[],
                        ),
                    ],
                )
            ],
        )
