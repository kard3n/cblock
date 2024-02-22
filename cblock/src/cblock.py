"""
Entry point for CBlock

Run as follows:
cd mitmproxy
pip install -e .[dev]
cd ..
mitmproxy -m regular -s src/cblock.py


Enable utf-8 support (needs to be done only once per environment):
conda env config vars set PYTHONUTF8=1
"""

import logging

import regex

from content_analyzer.ContentAnalyzerFactory import ContentAnalyzerFactory
from content_factory.ContentFactory import ContentFactory
from db.PathSearchResult import PathSearchResult
from db.SQLiteManager import SQLiteManager
from editor.ContentEditorFactory import ContentEditorFactory
from mitmproxy import http
from schema.SchemaParserFactory import SchemaParserFactory
from schema.SchemaReader import SchemaReader


# TODO class to load config

# TODO configure project root


class Main:
    # source_filter_factory: SourceFilterFactory
    # content_analyzer_factory: ContentAnalyzerFactory

    def __init__(self):
        logging.info("Starting CBlock")
        self.content_analyzer_factory = ContentAnalyzerFactory()
        self.content_editor_factory = ContentEditorFactory(
            content_analyzer=self.content_analyzer_factory.get_content_analyzer(),
            content_factory=ContentFactory(),
        )
        self.schema_parser_factory = SchemaParserFactory()
        self.db_manager = SQLiteManager(
            database_name="cb_database.db", table_name="cb_schema"
        )

        if not self.db_manager.has_database():
            logging.warning("No database was found, initializing...")
            self.db_manager.create_schema_table()

            try:
                schema_reader: SchemaReader = SchemaReader(
                    db_manager=self.db_manager, schema_location="schema_definitions/"
                )
                schema_reader.run()
            except Exception as e:
                print(e.__traceback__)

    async def response(self, flow: http.HTTPFlow):
        # logging.info(f"URI: {flow.request.pretty_host + flow.request.path}")
        paths: list[PathSearchResult] = self.db_manager.get_paths_for_url(
            url=flow.request.pretty_host
        )

        for search_result in paths:
            if regex.compile(search_result.path).match(flow.request.path) is not None:
                flow.response.text = await self.__edit(
                    schema_id=search_result.id,
                    content=flow.response.text,
                )

    async def __edit(self, schema_id: str, content: str) -> str:

        # logging.warning(self.db_manager.get_schema(url=url))
        schema_type, schema = self.db_manager.get_schema(schema_id=schema_id)

        logging.info(
            f"Parsed: {self.schema_parser_factory.getParser(parser_type=schema_type).parse_string(schema)}"
        )

        logging.info(
            f"""Result: {self.content_editor_factory.get_content_editor(
                editor_type=schema_type
            ).edit(
                input_raw=content,
                schema=self.schema_parser_factory.getParser(
                    parser_type=schema_type
                ).parse_string(schema),
            )[
                0:100
            ]}"""
        )

        return self.content_editor_factory.get_content_editor(
            editor_type=schema_type
        ).edit(
            input_raw=content,
            schema=self.schema_parser_factory.getParser(
                parser_type=schema_type
            ).parse_string(schema),
        )


addons = [Main()]
