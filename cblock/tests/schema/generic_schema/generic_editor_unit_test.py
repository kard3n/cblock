import unittest
from unittest.mock import Mock


from regex import regex

import test_utils
from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.editors.generic_editor.GenericEditor import GenericContentEditor
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.generic_schema.GenericSchema import GenericSchema


class GenericSchemaEditorUnitTest(unittest.TestCase):
    content_factory: ContentFactory
    content_analyzer: ContentAnalyzerInterface
    schema_factory: SchemaFactory
    editor_factory: ContentEditorFactory
    editor: GenericContentEditor

    def setUp(self):
        self.db_manager: DBManagerInterface = Mock(DBManagerInterface)
        self.content_factory = Mock(ContentFactory)
        self.content_analyzer = Mock(ContentAnalyzerInterface)
        self.schema_factory = Mock(SchemaFactory)
        self.editor_factory = Mock(ContentEditorFactory)

        self.editor: GenericContentEditor = GenericContentEditor(
            content_analyzer=self.content_analyzer,
            content_factory=self.content_factory,
            editor_factory=self.editor_factory,
            schema_factory=self.schema_factory,
        )

    def test_extract_content_with_schema_depth_one(self):
        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("bb(?P<content>hola)bb"),
                    tags=[ContentTag.ANALYZE],
                    embedded_schema=None,
                    children=None,
                )
            ],
        )

        assert (
            self.editor.extract_content(input_value="bbholabb", schema=schema)
            == "hola "
        )

        assert (
            self.editor.extract_content(input_value="bbholabb_bbholabb", schema=schema)
            == "hola hola "
        )

        assert (
            self.editor.extract_content(input_value="bb_hola_bb", schema=schema) == ""
        )

    def test_extract_content_with_schema_depth_two(self):
        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("_(?P<content>(<p>.*</p>)+)_"),
                    tags=[ContentTag.ELEMENT],
                    embedded_schema=None,
                    children=[
                        GenericSchema(
                            pattern=regex.Regex("<p>(?P<content>\w{3})</p>"),
                            tags=[ContentTag.ANALYZE],
                            embedded_schema=None,
                            children=None,
                        )
                    ],
                )
            ],
        )

        assert (
            self.editor.extract_content(
                input_value="_<p>abc</p><p>def</p><p>ghi</p>_", schema=schema
            )
            == "abc def ghi "
        )

        assert (
            self.editor.extract_content(
                input_value="_<p>abc</p><p>def</p>_", schema=schema
            )
            == "abc def "
        )

    def test_extract_content_with_embedded_schema(self):
        embedded_editor = Mock(ContentEditorInterface)

        editor_return_value: str = test_utils.random_string(10)
        embedded_editor.extract_content.return_value = editor_return_value
        embedded_schema_id: str = test_utils.random_string(10)

        self.editor_factory.get_content_editor_by_schema_id.return_value = (
            embedded_editor
        )

        get_schema_return_value: str = test_utils.random_string(10)
        self.schema_factory.get_schema_by_id.return_value = get_schema_return_value

        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("_(?P<content>\w{10})_"),
                    tags=[],
                    embedded_schema=embedded_schema_id,
                    children=None,
                )
            ],
        )

        assert (
            self.editor.extract_content(
                input_value="_" + editor_return_value + "_", schema=schema
            )
            == editor_return_value + " "
        )

        self.editor_factory.get_content_editor_by_schema_id.assert_called_once_with(
            schema_id=embedded_schema_id
        )

        embedded_editor.extract_content.assert_called_once_with(
            input_value=editor_return_value, schema=get_schema_return_value
        )

    def test_apply_action_with_schema_depth_one(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("_(?P<content>\w{10})_"),
                    tags=[ContentTag.TITLE],
                    embedded_schema=None,
                    children=None,
                )
            ],
        )

        assert (
            self.editor.apply_action(
                input_value=f"_{test_utils.random_string(10)}_",
                schema=schema,
                content=generated_content,
            )
            == f"_{generated_content.title}_"
        )

        assert (
            self.editor.apply_action(
                input_value=f"_{test_utils.random_string(10)}__{test_utils.random_string(10)}_",
                schema=schema,
                content=generated_content,
            )
            == f"_{generated_content.title}__{generated_content.title}_"
        )

    def test_apply_action_with_embedded_schema(self):
        embedded_editor = Mock(ContentEditorInterface)

        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        embedded_editor.apply_action.return_value = generated_content.title
        embedded_schema_id: str = test_utils.random_string(10)

        self.editor_factory.get_content_editor_by_schema_id.return_value = (
            embedded_editor
        )

        get_schema_return_value: str = test_utils.random_string(10)
        self.schema_factory.get_schema_by_id.return_value = get_schema_return_value

        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("_(?P<content>\w{10})_"),
                    tags=[],
                    embedded_schema=embedded_schema_id,
                    children=None,
                )
            ],
        )

        assert (
            self.editor.apply_action(
                input_value=f"_{test_utils.random_string(10)}_",
                schema=schema,
                content=generated_content,
            )
            == f"_{generated_content.title}_"
        )

    def test_edit(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        self.content_analyzer.analyze.return_value = True

        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            embedded_schema=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex(r"__(?P<content>A\w{10}A)+__"),
                    tags=[ContentTag.ELEMENT],
                    embedded_schema=None,
                    children=[
                        GenericSchema(
                            pattern=regex.Regex(r"A(?P<content>\w{10})A"),
                            tags=[ContentTag.TITLE, ContentTag.ANALYZE],
                            embedded_schema=None,
                            children=[],
                        )
                    ],
                )
            ],
        )

        random_content = test_utils.random_string(10)
        assert (
            self.editor.edit(input_raw=f"__A{random_content}A__", schema=schema)
            == f"__A{generated_content.title}A__"
        )

        self.content_analyzer.analyze.assert_called_once_with(f"{random_content} ")
