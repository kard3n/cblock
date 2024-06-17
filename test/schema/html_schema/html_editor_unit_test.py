import unittest
from unittest.mock import Mock

from bs4 import BeautifulSoup
from regex import regex

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content.Content import Content
from content.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.ContentExtractionResult import ContentExtractionResult
from editor.editors.html_editor.HTMLContentEditor import HTMLContentEditor
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.html_schema.HTMLSchema import HTMLSchema
from test import test_utils


class HTTPSchemaEditorUnitTest(unittest.TestCase):
    content_factory: ContentFactory
    content_analyzer: ContentClassifierInterface
    schema_factory: SchemaFactory
    editor_factory: ContentEditorFactory
    editor: HTMLContentEditor

    def setUp(self):
        self.db_manager: DBManagerInterface = Mock(DBManagerInterface)
        self.content_factory = Mock(ContentFactory)
        self.content_analyzer = Mock(ContentClassifierInterface)
        self.schema_factory = Mock(SchemaFactory)
        self.editor_factory = Mock(ContentEditorFactory)

        self.editor: HTMLContentEditor = HTMLContentEditor(
            content_analyzer=self.content_analyzer,
            content_factory=self.content_factory,
            editor_factory=self.editor_factory,
            schema_factory=self.schema_factory,
        )

    def test_extract_content(self):
        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    attributes_regex={"href": regex.compile(r"https:\/\/example\.com")},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        assert self.editor.extract_content(
            input_value=r"""<a href="https://example.com">test</a>""", schema=schema
        ) == ContentExtractionResult(title="test ", text="", pictures=[])

        assert self.editor.extract_content(
            input_value=r"""<a href="nothing">test</a>""", schema=schema
        ) == ContentExtractionResult(title="", text="", pictures=[])

        assert self.editor.extract_content(
            input_value=r"""<b href="https://example.com">test</b>""", schema=schema
        ) == ContentExtractionResult(title="", text="", pictures=[])

    def test_extract_content_from_attributes(self):
        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[],
                    attributes_to_edit={
                        "analyze": [ContentTag.ANALYZE, ContentTag.TITLE],
                        "dont_analyze": [ContentTag.DELETE],
                    },
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        random_string_one: str = test_utils.random_string(10)
        random_string_two: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=f"""<a analyze="{random_string_one}" dont_analyze="{random_string_two}"></a>""",
            schema=schema,
        ) == ContentExtractionResult(
            title=random_string_one + " ", text="", pictures=[]
        )

    def test_extract_content_parsed(self):
        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    attributes_regex={"href": regex.compile(r"https:\/\/example\.com")},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        assert self.editor.extract_content_parsed(
            element=BeautifulSoup(
                r"""<a href="https://example.com">test</a>""", parser="lxml"
            ),
            schema=schema,
        ) == ContentExtractionResult(title="test ", text="", pictures=[])

        assert self.editor.extract_content_parsed(
            element=BeautifulSoup(r"""<a href="nothing">test</a>""", parser="lxml"),
            schema=schema,
        ) == ContentExtractionResult(title="", text="", pictures=[])

        assert self.editor.extract_content_parsed(
            element=BeautifulSoup(
                r"""<b href="https://example.com">test</b>""", parser="lxml"
            ),
            schema=schema,
        ) == ContentExtractionResult(title="", text="", pictures=[])

    def test_extract_content_parsed_blacklisted_attribute(self):
        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    not_attributes=["class"],
                    attributes_regex={"href": regex.compile(r"https:\/\/example\.com")},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        assert self.editor.extract_content_parsed(
            element=BeautifulSoup(
                r"""<a class="anything" href="https://example.com">test</a>""",
                parser="lxml",
            ),
            schema=schema,
        ) == ContentExtractionResult(title="", text="", pictures=[])

        assert self.editor.extract_content_parsed(
            element=BeautifulSoup(
                r"""<a href="https://example.com">test</a>""",
                parser="lxml",
            ),
            schema=schema,
        ) == ContentExtractionResult(title="test ", text="", pictures=[])

    def test_extract_content_non_recursive(self):
        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("span"),
                    content_tags=[],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("a"),
                            content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                            search_recursive=False,
                            attributes_regex={},
                            attributes_multival={},
                            embedded_schema=None,
                            children=[],
                        )
                    ],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=f"""<span><b><a>{random_string}</a></b></span>""",
            schema=schema,
        ) == ContentExtractionResult(title="", text="", pictures=[])

        assert self.editor.extract_content(
            input_value=f"""<span><a>{random_string}</a></span>""",
            schema=schema,
        ) == ContentExtractionResult(title=random_string + " ", text="", pictures=[])

        assert self.editor.extract_content(
            input_value=f"""<b><span><a>{random_string}</a></span></b>""",
            schema=schema,
        ) == ContentExtractionResult(title=random_string + " ", text="", pictures=[])

    def test_extract_content_with_embedded_schema(self):
        embedded_editor = Mock(ContentEditorInterface)

        embedded_editor.extract_content.return_value = None
        embedded_schema_id: str = test_utils.random_string(10)

        self.editor_factory.get_content_editor_by_schema_id.return_value = (
            embedded_editor
        )

        get_schema_return_value: str = test_utils.random_string(10)
        self.schema_factory.get_schema_by_id.return_value = get_schema_return_value

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[],
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=embedded_schema_id,
                    children=[],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        # The mocked editor doesn't edit the ContentExtractionResult, therefore the result isn't changed either
        assert self.editor.extract_content(
            input_value=f"<a>{random_string}</a>", schema=schema
        ) == ContentExtractionResult(title="", text="", pictures=[])

        self.editor_factory.get_content_editor_by_schema_id.assert_called_once_with(
            schema_id=embedded_schema_id
        )

        embedded_editor.extract_content.assert_called_once_with(
            input_value=random_string,
            schema=get_schema_return_value,
            result_container=ContentExtractionResult(text="", pictures=[]),
        )

    def test_edit_container_element(self):
        generated_content: Content = test_utils.generate_content()

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=f"<div><a>{random_string}</a></div>",
            schema=schema,
        ) == ContentExtractionResult(
            title=random_string + " ", text="", pictures=[], categories=""
        )

        assert (
            self.editor.edit_container_element(
                input_value=f"<div><a>{random_string}</a></div>",
                schema=schema,
                content=generated_content,
            )
            == f"<div><a>{generated_content.title}</a></div>"
        )

        assert (
            self.editor.edit_container_element(
                input_value=f"<div><a>{random_string}\n{random_string}<p></p></a></div>",
                schema=schema,
                content=generated_content,
            )
            == f"<div><a>{generated_content.title}</a></div>"
        )

    def test_edit_container_element_blacklisted_attribute(self):
        generated_content: Content = test_utils.generate_content()

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    not_attributes=["class"],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        assert (
            self.editor.edit_container_element(
                input_value=f"<div><a>{random_string}</a></div>",
                schema=schema,
                content=generated_content,
            )
            == f"<div><a>{generated_content.title}</a></div>"
        )

        assert (
            self.editor.edit_container_element(
                input_value=f'<div><a class="">{random_string}</a></div>',
                schema=schema,
                content=generated_content,
            )
            == f'<div><a class="">{random_string}</a></div>'
        )

    def test_edit_container_element_with_attributes(self):
        generated_content: Content = test_utils.generate_content()

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[],
                    search_recursive=True,
                    attributes_to_edit={
                        "href": [ContentTag.LINK],
                        "text": [ContentTag.SUMMARY, ContentTag.ANALYZE],
                    },
                    attributes_regex={},
                    attributes_multival={
                        "test_attr": ["one", "two"],
                        "class": ["four", "five"],
                    },
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        random_string_one: str = test_utils.random_string(10)
        random_string_two: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=f'<div><a class="four five" test_attr="one two" href="{random_string_one}" text="{random_string_two}">Anything</a></div>',
            schema=schema,
        ) == ContentExtractionResult(
            title="", text=random_string_two + " ", pictures=[], categories=""
        )

        assert (
            self.editor.edit_container_element(
                input_value=f'<div><a class="four five" href="{random_string_one}" test_attr="one two" text="{random_string_two}">Anything</a></div>',
                schema=schema,
                content=generated_content,
            )
            == f'<div><a class="four five" href="{generated_content.link}" test_attr="one two" text="{generated_content.summary}">Anything</a></div>'
        )

        # test non-multival attribute
        assert (
            self.editor.edit_container_element(
                input_value=f'<div><a href="{random_string_one}" class="four five six" test_attr="three four" text="{random_string_two}">Anything</a></div>',
                schema=schema,
                content=generated_content,
            )
            == f'<div><a class="four five six" href="{random_string_one}" test_attr="three four" text="{random_string_two}">Anything</a></div>'
        )

        # test multival attribute
        assert (
            self.editor.edit_container_element(
                input_value=f'<div><a href="{random_string_one}" class="four six" test_attr="one two" text="{random_string_two}">Anything</a></div>',
                schema=schema,
                content=generated_content,
            )
            == f'<div><a class="four six" href="{random_string_one}" test_attr="one two" text="{random_string_two}">Anything</a></div>'
        )

    def test_edit_container_is_leaf(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content
        self.content_analyzer.classify.return_value = True

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("a"),
                    content_tags=[
                        ContentTag.CONTAINER,
                        ContentTag.ANALYZE,
                        ContentTag.TITLE,
                    ],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        self.assertEqual(
            self.editor.edit(
                input_raw=f"<html><body><div><a>{random_string}</a></div></body></html>", schema=schema
            ),
            f"<html><body><div><a>{generated_content.title}</a></div></body></html>"
        )

        self.assertEqual(
            self.editor.edit(
                input_raw=f"<html><body><div><a>{random_string}\n{random_string}<p></p></a></div></body></html>",
                schema=schema,
            ),
            f"<html><body><div><a>{generated_content.title}</a></div></body></html>"
        )

    def test_edit(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content
        self.content_analyzer.classify.return_value = True

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("div"),
                    content_tags=[ContentTag.CONTAINER],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("a"),
                            content_tags=[
                                ContentTag.ANALYZE,
                                ContentTag.TITLE,
                            ],
                            search_recursive=True,
                            attributes_regex={},
                            attributes_multival={},
                            embedded_schema=None,
                            children=[],
                        )
                    ],
                )
            ],
        )

        random_string: str = test_utils.random_string(10)

        self.assertEqual(
            self.editor.edit(
                input_raw=f"<html><body><div><a>{random_string}</a></div></body></html>", schema=schema
            ),
            f"<html><body><div><a>{generated_content.title}</a></div></body></html>"
        )

        self.assertEqual (
            self.editor.edit(
                input_raw=f"<html><body><div><a>{random_string}\n{random_string}<p></p></a></div></body></html>",
                schema=schema,
            ),
            f"<html><body><div><a>{generated_content.title}</a></div></body></html>"
        )

    def test_edit_with_attributes(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content
        self.content_analyzer.classify.return_value = True

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("div"),
                    content_tags=[ContentTag.CONTAINER],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    children=[
                        HTMLSchema(
                            html_tag=regex.compile("a"),
                            content_tags=[
                                ContentTag.ANALYZE,
                                ContentTag.TITLE,
                            ],
                            attributes_to_edit={
                                "href": [ContentTag.LINK],
                                "src": [ContentTag.PICTURE],
                            },
                            search_recursive=True,
                            attributes_regex={},
                            attributes_multival={},
                            embedded_schema=None,
                            children=[],
                        ),
                        HTMLSchema(
                            html_tag=regex.compile("img"),
                            content_tags=[],
                            attributes_to_edit={
                                "src": [ContentTag.PICTURE],
                            },
                            search_recursive=True,
                            attributes_regex={},
                            attributes_multival={},
                            embedded_schema=None,
                            children=[],
                        ),
                    ],
                )
            ],
        )

        random_string_one: str = test_utils.random_string(10)
        random_string_two: str = test_utils.random_string(10)

        print(generated_content)

        self.assertEqual(
            self.editor.edit(
                input_raw=f"<html><body><div><a>{random_string_one}</a><a>{random_string_two}</a><img src={random_string_two}/></div></body></html>",
                schema=schema,
            ), f'<html><body><div><a>{generated_content.title}</a><a>{generated_content.title}</a><img src="{generated_content.picture}"/></div></body></html>'
        )

        assert (
            self.editor.edit(
                input_raw=f'<html><body><div><a href="https://www.example.com/test" src="https://www.example.com/testimage.png">{random_string_one}</a><img href="https://www.example.com/test" src="https://www.example.com/testimage.png"/></div></body></html>',
                schema=schema,
            )
            == f'<html><body><div><a href="{generated_content.link}" src="{generated_content.picture}">{generated_content.title}</a><img href="https://www.example.com/test" src="{generated_content.picture}"/></div></body></html>'
        )

    def test_edit_precondition(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content
        self.content_analyzer.classify.return_value = True

        schema: HTMLSchema = HTMLSchema(
            html_tag=None,
            content_tags=[],
            attributes_regex={},
            attributes_multival={},
            embedded_schema=None,
            children=[
                HTMLSchema(
                    html_tag=regex.compile("div"),
                    content_tags=[ContentTag.CONTAINER, ContentTag.TITLE],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    precondition=regex.compile("PREC"),
                    children=[],
                ),
                HTMLSchema(
                    html_tag=regex.compile("span"),
                    content_tags=[ContentTag.DELETE_UNCONDITIONAL],
                    search_recursive=True,
                    attributes_regex={},
                    attributes_multival={},
                    embedded_schema=None,
                    precondition=regex.compile("PREC"),
                    children=[],
                ),
            ],
        )

        random_string: str = test_utils.random_string(10)

        assert (
            self.editor.edit(input_raw=f"<div>PREC</div>", schema=schema)
            == f"<html><body><div>{generated_content.title}</div></body></html>"
        )

        assert (
            self.editor.edit(input_raw=f"<div>NO PREC</div>", schema=schema)
            == f"<html><body><div>NO PREC</div></body></html>"
        )

        assert (
            self.editor.edit(input_raw=f"<span>PREC</span>", schema=schema)
            == f"<html><body></body></html>"
        )

        assert (
            self.editor.edit(input_raw=f"<span>NO PREC</span>", schema=schema)
            == f"<html><body><span>NO PREC</span></body></html>"
        )
