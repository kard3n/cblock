import unittest

from regex import regex

from content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from content_factory.ContentFactory import ContentFactory
from db.SQLiteManager import SQLiteManager
from editor.editors.generic_editor.GenericEditor import GenericEditor
from schema.ContentTag import ContentTag
from schema.generic_schema.GenericSchema import GenericSchema
from schema.parser.SchemaReader import SchemaReader


class GenericSchemaEditorUnitTest(unittest.TestCase):
    editor: GenericEditor

    @classmethod
    def setUpClass(cls):
        db_manager = SQLiteManager(database_name="cb_test.db", table_name="cb_schema")

        if not db_manager.has_database():
            db_manager.create_schema_table()

            try:
                schema_reader: SchemaReader = SchemaReader(
                    db_manager=db_manager, schema_location="../schema_definitions/"
                )
                schema_reader.run()
            except Exception as e:
                print(e.__traceback__)

        cls.editor: GenericEditor = GenericEditor(
            content_analyzer=SimpleContentAnalyzer(),
            content_factory=ContentFactory(),
            db_manager=db_manager,
        )

    def test_extract_content_one(self):
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
            self.editor.extract_content(input_value="bbholabb", schema=schema) == "hola"
        )

        assert (
            self.editor.extract_content(input_value="bb_hola_bb", schema=schema) == ""
        )

    def test_extract_content_two(self):
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
                            pattern=regex.Regex("<p>(?P<content>abc)</p>"),
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
                input_value="_<p>abc</p><p>abc</p>_", schema=schema
            )
            == "abcabc"
        )
