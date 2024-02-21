import unittest

from regex import regex

from src.content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from src.content_factory.ContentFactory import ContentFactory
from src.editor.editors.generic_editor.GenericEditor import GenericEditor
from src.schema.ContentTag import ContentTag
from src.schema.generic_schema.GenericSchema import GenericSchema


class GenericSchemaEditorUnitTest(unittest.TestCase):
    editor: GenericEditor

    @classmethod
    def setUpClass(cls):
        cls.editor: GenericEditor = GenericEditor(
            content_analyzer=SimpleContentAnalyzer(), content_factory=ContentFactory()
        )

    def test_extract_content_one(self):
        schema: GenericSchema = GenericSchema(
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
        )

        assert (
            self.editor.extract_content(input_value="bbholabb", schema=schema) == "hola"
        )

        assert (
            self.editor.extract_content(input_value="bb_hola_bb", schema=schema) == ""
        )

    def test_extract_content_two(self):
        schema: GenericSchema = GenericSchema(
            pattern=None,
            tags=[],
            schema_id=None,
            children=[
                GenericSchema(
                    pattern=regex.Regex("_(?P<content>(<p>.*</p>)+)_"),
                    tags=[ContentTag.ELEMENT],
                    schema_id=20,
                    children=[
                        GenericSchema(
                            pattern=regex.Regex("<p>(?P<content>abc)</p>"),
                            tags=[ContentTag.ANALYZE],
                            schema_id=20,
                            children=None,
                        )
                    ],
                )
            ],
        )

        assert (
            self.editor.extract_content(
                input_value="_<p>abc</p><p>abc</p>_", schema=schema
            )
            == "abcabc"
        )
