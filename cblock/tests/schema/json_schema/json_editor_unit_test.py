import unittest
from unittest.mock import Mock

import test_utils
from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.ContentExtractionResult import ContentExtractionResult
from editor.editors.json_editor.JSONContentEditor import JSONContentEditor
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.json_schema.JSONSchema import JSONSchema, ValueType


class JsonEditorUnitTest(unittest.TestCase):
    def setUp(self):
        self.db_manager: DBManagerInterface = Mock(DBManagerInterface)
        self.content_factory = Mock(ContentFactory)
        self.content_analyzer = Mock(ContentAnalyzerInterface)
        self.schema_factory = Mock(SchemaFactory)
        self.editor_factory = Mock(ContentEditorFactory)

        self.editor: JSONContentEditor = JSONContentEditor(
            content_analyzer=self.content_analyzer,
            content_factory=self.content_factory,
            editor_factory=self.editor_factory,
            schema_factory=self.schema_factory,
        )

    def test_extract_content_dict(self):
        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.DICT,
            value={
                "name": JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    embedded_schema=None,
                    value_type=ValueType.LEAF,
                    value="Something",
                )
            },
        )

        random_content: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value={"name": random_content}, schema=schema
        ) == ContentExtractionResult(text=random_content + " ", pictures=[])

    def test_extract_content_list(self):
        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.LIST,
            value=JSONSchema(
                tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                embedded_schema=None,
                value_type=ValueType.LEAF,
                value="Something",
            ),
        )

        random_content_one: str = test_utils.random_string(10)
        random_content_two: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=[random_content_one], schema=schema
        ) == ContentExtractionResult(text=random_content_one + " ", pictures=[])

        assert self.editor.extract_content(
            input_value=[random_content_one, random_content_two], schema=schema
        ) == ContentExtractionResult(
            text=random_content_one + " " + random_content_two + " ", pictures=[]
        )

    def test_extract_content_list_2d(self):
        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.LIST,
            value=JSONSchema(
                tags=[],
                embedded_schema=None,
                value_type=ValueType.LIST,
                value=JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                    embedded_schema=None,
                    value_type=ValueType.LEAF,
                    value="Something",
                ),
            ),
        )

        random_content_one: str = test_utils.random_string(10)
        random_content_two: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=[[random_content_one]], schema=schema
        ) == ContentExtractionResult(text=random_content_one + " ", pictures=[])

        assert self.editor.extract_content(
            input_value=[[random_content_one, random_content_two]], schema=schema
        ) == ContentExtractionResult(
            text=random_content_one + " " + random_content_two + " ", pictures=[]
        )

    def test_extract_content_leaf(self):
        schema: JSONSchema = JSONSchema(
            tags=[ContentTag.ANALYZE, ContentTag.FULL_CONTENT],
            embedded_schema=None,
            value_type=ValueType.LEAF,
            value="Something",
        )

        random_content: str = test_utils.random_string(10)

        assert self.editor.extract_content(
            input_value=random_content, schema=schema
        ) == ContentExtractionResult(text=random_content + " ", pictures=[])

    def test_extract_content_with_embedded_schema(self):
        embedded_editor = Mock(ContentEditorInterface)

        embedded_editor_return_value: ContentExtractionResult = ContentExtractionResult(
            text=test_utils.random_string(10), pictures=[]
        )
        embedded_editor.extract_content.return_value = embedded_editor_return_value
        embedded_schema_id: str = test_utils.random_string(10)

        self.editor_factory.get_content_editor_by_schema_id.return_value = (
            embedded_editor
        )

        get_schema_return_value: str = test_utils.random_string(10)
        self.schema_factory.get_schema_by_id.return_value = get_schema_return_value

        random_content: str = test_utils.random_string(10)

        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.DICT,
            value={
                "name": JSONSchema(
                    tags=[],
                    embedded_schema=embedded_schema_id,
                    value_type=ValueType.LEAF,
                    value="Something",
                )
            },
        )

        # The embedded editor is a mock and doesn't edit the object that it gets passed.
        # Therefor the call has no effect
        assert self.editor.extract_content(
            input_value={"name": random_content}, schema=schema
        ) == ContentExtractionResult(text="", pictures=[])

        embedded_editor.extract_content.assert_called_once_with(
            input_value=random_content,
            schema=get_schema_return_value,
            result_container=ContentExtractionResult(text="", pictures=[]),
        )

    def test_apply_action_leaf(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        schema: JSONSchema = JSONSchema(
            tags=[ContentTag.ANALYZE, ContentTag.TITLE],
            embedded_schema=None,
            value_type=ValueType.LEAF,
            value="Something",
        )

        random_content: str = test_utils.random_string(10)

        assert (
            self.editor.apply_action(
                input_value=random_content, schema=schema, content=generated_content
            )
            == generated_content.title
        )

    def test_apply_action_list(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.LIST,
            value=JSONSchema(
                tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                embedded_schema=None,
                value_type=ValueType.LEAF,
                value="Something",
            ),
        )

        assert self.editor.apply_action(
            input_value=[test_utils.random_string(10)],
            schema=schema,
            content=generated_content,
        ) == [generated_content.title]

        assert self.editor.apply_action(
            input_value=[test_utils.random_string(10), test_utils.random_string(10)],
            schema=schema,
            content=generated_content,
        ) == [generated_content.title, generated_content.title]

    def test_apply_action_dict(self):
        generated_content: Content = test_utils.generate_content()
        self.content_factory.get_content.return_value = generated_content

        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.DICT,
            value={
                "name": JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    embedded_schema=None,
                    value_type=ValueType.LEAF,
                    value="Something",
                )
            },
        )

        assert self.editor.apply_action(
            input_value={"name": test_utils.random_string(10)},
            schema=schema,
            content=generated_content,
        ) == {"name": generated_content.title}

        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.DICT,
            value={
                "name": JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    embedded_schema=None,
                    value_type=ValueType.LEAF,
                    value="Something",
                ),
                "class": JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.SUMMARY],
                    embedded_schema=None,
                    value_type=ValueType.LEAF,
                    value="Something",
                ),
            },
        )

        assert self.editor.apply_action(
            input_value={
                "name": test_utils.random_string(10),
                "class": test_utils.random_string(10),
            },
            schema=schema,
            content=generated_content,
        ) == {"name": generated_content.title, "class": generated_content.summary}

    def test_apply_action_with_embedded_schema(self):
        generated_content: Content = test_utils.generate_content()

        embedded_editor = Mock(ContentEditorInterface)

        embedded_editor_return_value: str = test_utils.random_string(10)
        embedded_editor.apply_action.return_value = embedded_editor_return_value
        embedded_schema_id: str = test_utils.random_string(10)

        self.editor_factory.get_content_editor_by_schema_id.return_value = (
            embedded_editor
        )

        get_schema_return_value: str = test_utils.random_string(10)
        self.schema_factory.get_schema_by_id.return_value = get_schema_return_value

        schema: JSONSchema = JSONSchema(
            tags=[],
            embedded_schema=None,
            value_type=ValueType.DICT,
            value={
                "name": JSONSchema(
                    tags=[ContentTag.ANALYZE, ContentTag.TITLE],
                    embedded_schema=embedded_schema_id,
                    value_type=ValueType.LEAF,
                    value="Something",
                )
            },
        )

        random_string: str = test_utils.random_string(10)

        assert self.editor.apply_action(
            input_value={"name": random_string},
            schema=schema,
            content=generated_content,
        ) == {"name": embedded_editor_return_value}

        self.editor_factory.get_content_editor_by_schema_id.assert_called_once_with(
            schema_id=embedded_schema_id
        )

        self.schema_factory.get_schema_by_id.assert_called_once_with(
            schema_id=embedded_schema_id
        )

        embedded_editor.apply_action.assert_called_once_with(
            content=generated_content,
            input_value=random_string,
            schema=get_schema_return_value,
        )

    # TODO tests for edit and tests for apply_action with more complex schemas
