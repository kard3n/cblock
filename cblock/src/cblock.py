"""
Entry point for CBlock

mitmproxy -m regular -s cblock/src/cblock.py
mitmproxy -m regular --set anticomp=true --set  body_size_limit=3m --set console_eventlog_verbosity=warn -s cblock/src/cblock.py


Enable utf-8 support (needs to be done only once per environment):
conda env config vars set PYTHONUTF8=1
"""

import logging
import os

import regex

from content_classifier.ContentClassifierFactory import ContentAnalyzerFactory
from content_factory.ContentFactory import ContentFactory
from db.PathSearchResult import PathSearchResult
from db.SQLiteManager import SQLiteManager
from editor.ContentEditorFactory import ContentEditorFactory
from mitmproxy import http
from schema.parser.SchemaParserFactory import SchemaParserFactory
from schema.parser.SchemaReader import SchemaReader


# TODO class to load config

# TODO configure project root


class Main:

    def __init__(self):
        logging.info("Starting CBlock")
        self.content_analyzer_factory = ContentAnalyzerFactory()

        self.schema_parser_factory = SchemaParserFactory()
        self.db_manager = SQLiteManager(
            database_name="cb_database.db", table_name="cb_schema"
        )

        self.content_editor_factory = ContentEditorFactory(
            content_analyzer=self.content_analyzer_factory.get_content_analyzer(),
            content_factory=ContentFactory(),
            db_manager=self.db_manager,
        )

        if not self.db_manager.has_database():
            logging.warning("No database was found, initializing...")
            self.db_manager.create_schema_table()

            try:
                schema_reader: SchemaReader = SchemaReader(
                    db_manager=self.db_manager,
                    schema_location="cblock/src/schema_definitions/",
                )
                schema_reader.run()
            except Exception as e:
                os.remove("cb_database.db")
                logging.error(f"Error while initializing database: {e}")

    async def response(self, flow: http.HTTPFlow):
        # logging.warning(f"URI: {flow.request.pretty_host + flow.request.path}")
        # logging.warning(f"Pretty host: {flow.request.pretty_host}")
        paths: list[PathSearchResult] = self.db_manager.get_paths_for_url(
            url=flow.request.pretty_host.removeprefix("www.")
        )

        # logging.warning(f"Paths for {flow.request.pretty_host.removeprefix("www.")}: {paths}")

        for search_result in paths:
            if regex.compile(search_result.path).match(flow.request.path) is not None:
                # logging.warning(f"Paths for {flow.request.pretty_host.removeprefix("www.")}: {paths}")
                flow.response.text = await self.__edit(
                    schema_id=search_result.id,
                    content=flow.response.text,
                )

    async def __edit(self, schema_id: str, content: str) -> str:

        # logging.warning(self.db_manager.get_schema(url=url))
        schema_search_result = self.db_manager.get_schema(schema_id=schema_id)

        logging.info(
            f"""Result: {self.content_editor_factory.get_content_editor(
                schema_type=schema_search_result.schema_type
            ).edit(
                input_raw=content,
                schema=self.schema_parser_factory.getParser(
                    parser_type=schema_search_result.schema_type
                ).parse_string(schema_search_result.schema),
            )[
                0:100
            ]}"""
        )

        return self.content_editor_factory.get_content_editor(
            schema_type=schema_search_result.schema_type
        ).edit(
            input_raw=content,
            schema=self.schema_parser_factory.getParser(
                parser_type=schema_search_result.schema_type
            ).parse_string(schema_search_result.schema),
        )


addons = [Main()]
