"""
Entry point for CBlock

mitmproxy -m regular -s cblock/src/cblock.py
mitmproxy -m regular --set anticomp=true --set  body_size_limit=3m --set console_eventlog_verbosity=warn -s cblock/src/cblock.py


Enable utf-8 support (needs to be done only once per environment):
conda env config vars set PYTHONUTF8=1
"""

import json
import logging
import os
import threading
import traceback

import regex
from jinja2 import Environment, FileSystemLoader

from configuration.Configuration import Configuration
from content_classifier.ClassifierManager import ClassifierManager
from content_factory.ContentFactory import ContentFactory
from db.PathSearchResult import PathSearchResult
from db.SQLiteManager import SQLiteManager
from editor.ContentEditorFactory import ContentEditorFactory
from mitmproxy.mitmproxy import http
from schema.parser.SchemaParserFactory import SchemaParserFactory
from schema.parser.SchemaReader import SchemaReader

# TODO configure project root


class CBlockAddonMain:

    def __init__(
        self,
        config: Configuration,
        classifier_manager: ClassifierManager,
        shutdown_event: threading.Event,
    ):
        print("Initializing CBlockAddon")
        self.shutdown_event = shutdown_event
        self.config = config
        self.classifier_manager = classifier_manager

        self.schema_parser_factory = SchemaParserFactory()
        self.db_manager = SQLiteManager(
            database_name="cb_database.db", table_name="cb_schema"
        )

        try:
            self.content_analyzer = self.classifier_manager.get_classifier(
                config.classifier
            )
            self.content_analyzer_name = config.classifier
        except KeyError as e:
            raise KeyError(
                f"The content analyzer '{config.classifier}' does not exist."
            )

        self.content_editor_factory = ContentEditorFactory(
            content_analyzer=self.content_analyzer,
            content_factory=ContentFactory(),
            db_manager=self.db_manager,
        )

        if not self.db_manager.has_database():
            logging.warning("No database was found, initializing...")
            self.db_manager.create_schema_table()

            try:
                schema_reader: SchemaReader = SchemaReader(
                    db_manager=self.db_manager,
                    schema_location="cblock/schema_definitions/",
                )
                schema_reader.run()
            except Exception as e:
                self.db_manager.close_connection()
                os.remove("cb_database.db")
                logging.error(
                    f"Error while initializing database: {traceback.format_exc()}"
                )

        self.jinja_environment = Environment(loader=FileSystemLoader("templates/"))
        self.home_template = self.jinja_environment.get_template("index.html")

    async def response(self, flow: http.HTTPFlow):
        # logging.warning(f"URI: {flow.request.pretty_host + flow.request.path}")
        # logging.warning(f"Pretty host: {flow.request.pretty_host}")
        paths: list[PathSearchResult] = self.db_manager.get_paths_for_url(
            url=flow.request.pretty_host.removeprefix("www.")
        )

        for search_result in paths:
            if regex.compile(search_result.path).match(flow.request.path) is not None:
                flow.response.text = await self.__edit(
                    schema_id=search_result.id,
                    content=flow.response.text,
                )

    async def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.pretty_host.removeprefix("www.") == self.config.application_url:
            if (
                flow.request.path == "/shutdown" and flow.request.method == "GET"
            ):  # Shut down ContentBlock
                self.shutdown_event.set()
                flow.response = http.Response.make(
                    200,
                    "Server shutting down...",
                    {
                        "Content-Type": "text/html",
                    },
                )
            elif (
                flow.request.path == "/supported_topics"
                and flow.request.method == "GET"
            ):
                flow.response = http.Response.make(
                    200,
                    json.dumps(
                        {"topics": self.content_analyzer.get_supported_topics()}
                    ),
                    {
                        "Content-Type": "application/json",
                    },
                )
            elif (
                flow.request.path == "/topic_blacklist"
                and flow.request.method == "POST"
            ):
                request_body = json.loads(flow.request.text)
                try:
                    self.classifier_manager.set_topic_blacklist(
                        self.content_analyzer_name, request_body["topics"]
                    )
                    flow.response = http.Response.make(
                        201,
                        '{"message": "Success"}',
                        {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                        },
                    )
                except Exception as e:
                    print(traceback.format_exc())
                    flow.response = http.Response.make(
                        status_code=400,
                        content=traceback.format_exc(),
                        headers={
                            "Content-Type": "text/html",
                        },
                    )
            elif (
                flow.request.path == "/aggressiveness" and flow.request.method == "POST"
            ):
                request_body = json.loads(flow.request.text)
                try:
                    new_aggressiveness = float(request_body["aggressiveness"])
                    self.classifier_manager.set_aggressiveness(
                        self.content_analyzer_name,
                        float(request_body["aggressiveness"]),
                    )
                    flow.response = http.Response.make(
                        201,
                        '{"message": "Success"}',
                        {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                        },
                    )
                except ValueError as e:
                    flow.response = http.Response.make(
                        400,
                        "Data invalid",
                        {
                            "Content-Type": "text/html",
                        },
                    )
            elif (
                flow.request.path == "/" and flow.request.method == "GET"
            ):  # Return Home page
                flow.response = http.Response.make(
                    200,
                    self.home_template.render(
                        supported_topics=self.content_analyzer.get_supported_topics(),
                        topic_blacklist=self.classifier_manager.classifier_info[
                            self.content_analyzer_name
                        ].topic_blacklist,
                        aggressiveness=self.classifier_manager.classifier_info[
                            self.content_analyzer_name
                        ].aggressiveness,
                    ),
                    {
                        "Content-Type": "text/html",
                    },
                )
            else:
                flow.response = http.Response.make(
                    404,
                    "Not Found",
                    {
                        "Content-Type": "text/html",
                    },
                )

    async def __edit(self, schema_id: str, content: str) -> str:

        schema_search_result = self.db_manager.get_schema(schema_id=schema_id)

        return self.content_editor_factory.get_content_editor(
            schema_type=schema_search_result.schema_type
        ).edit(
            input_raw=content,
            schema=schema_search_result.schema,
        )
