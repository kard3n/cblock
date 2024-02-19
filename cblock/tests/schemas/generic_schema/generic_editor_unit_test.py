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
