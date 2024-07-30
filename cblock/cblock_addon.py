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
from typing import Type

import regex
from jinja2 import Environment, FileSystemLoader

from configuration.Configuration import Configuration
from content_classifier.ClassifierManager import ClassifierManager
from content.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
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
        db_manager_class: Type[DBManagerInterface] = SQLiteManager,
        schema_parser_factory: SchemaParserFactory = SchemaParserFactory(),
    ):
        print("Initializing CBlockAddon")
        self.config = config
        self.classifier_manager = classifier_manager
        self.shutdown_event = shutdown_event

        self.db_manager = db_manager_class(database_name="cb_database.db")
        self.schema_parser_factory = schema_parser_factory

        try:
            self.content_classifier = self.classifier_manager.get_classifier(
                config.classifier
            )
            self.content_classifier_name = config.classifier
        except KeyError as e:
            raise KeyError(
                f"The content analyzer '{config.classifier}' does not exist."
            )

        self.content_editor_factory = ContentEditorFactory(
            content_classifier=self.content_classifier,
            content_factory=ContentFactory(),
            db_manager=self.db_manager,
        )

        self.schema_reader: SchemaReader = SchemaReader(
            db_manager=self.db_manager,
            schema_location="schema_definitions/",
        )

        if not self.db_manager.has_database():
            logging.warning("No database was found, initializing...")
            self.db_manager.initialize_database()

            try:

                self.schema_reader.run()
            except Exception as e:
                self.db_manager.close_connection()
                os.remove("cb_database.db")
                logging.error(
                    f"Error while initializing database: {traceback.format_exc()}"
                )

        self.jinja_environment = Environment(loader=FileSystemLoader("templates/"))
        self.home_template = self.jinja_environment.get_template("index.html")
        self.settings_template = self.jinja_environment.get_template("settings.html")

    async def response(self, flow: http.HTTPFlow):
        # logging.warning(f"URI: {flow.request.pretty_host + flow.request.path}")
        # logging.warning(f"Pretty host: {flow.request.pretty_host}")
        url = flow.request.pretty_host.removeprefix("www.")

        dot_pos = url[0 : url.rfind(".")].rfind(".")
        if dot_pos > 0:
            paths: list[PathSearchResult] = self.db_manager.get_paths_for_url(
                url=url[dot_pos + 1 :]
            )
        else:
            paths: list[PathSearchResult] = self.db_manager.get_paths_for_url(url=url)

        check_passed: bool

        for search_result in paths:
            check_passed = True
            if search_result.allowed_subdomains:
                if dot_pos > 0 and url[0:dot_pos] in search_result.allowed_subdomains:
                    check_passed = True
                elif "" in search_result.allowed_subdomains:
                    check_passed = True
                else:
                    check_passed = False

            if (
                check_passed
                and regex.compile(search_result.path).match(flow.request.path)
                is not None
            ):
                flow.response.text = await self.__edit(
                    schema_id=search_result.id,
                    content=flow.response.text,
                )

    async def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.pretty_host.removeprefix("www.") == self.config.application_url:
            if (
                flow.request.path == "/shutdown" and flow.request.method == "GET"
            ):  # Shut down ContentBlock
                await self.process_shutdown_get(flow)
            elif (
                flow.request.path == "/supported_topics"
                and flow.request.method == "GET"
            ):
                await self.process_supported_topics_get(flow)
            elif (
                flow.request.path == "/topic_blacklist"
                and flow.request.method == "POST"
            ):
                await self.process_blacklist_post(flow)
            elif (
                flow.request.path == "/aggressiveness" and flow.request.method == "POST"
            ):
                await self.process_aggressiveness_post(flow)
            elif (
                flow.request.path == "/" and flow.request.method == "GET"
            ):  # Return Home page
                await self.process_main_get(flow)
            elif flow.request.path == "/classifier" and flow.request.method == "POST":
                await self.process_classifier_post(flow)
            elif (
                flow.request.path == "/settings" and flow.request.method == "GET"
            ):  # Shut down ContentBlock
                await self.process_settings_get(flow)
            elif (
                flow.request.path == "/reload_schemata"
                and flow.request.method == "POST"
            ):  # Shut down ContentBlock
                await self.process_reload_schemata_post(flow)
            else:
                flow.response = http.Response.make(
                    404,
                    "Not Found",
                    {
                        "Content-Type": "text/html",
                    },
                )

    async def process_supported_topics_get(self, flow: http.HTTPFlow) -> None:
        """
        Processes POST requests to /topic_blacklist and edits the flow
        :param flow:
        :return:
        """
        flow.response = http.Response.make(
            200,
            json.dumps({"topics": self.content_classifier.get_supported_topics()}),
            {
                "Content-Type": "application/json",
            },
        )

    async def process_shutdown_get(self, flow: http.HTTPFlow) -> None:
        """
        Processes GET requests to /shutdown and edits the flow
        :param flow:
        :return:
        """

        self.shutdown_event.set()
        flow.response = http.Response.make(
            200,
            "Server shutting down...",
            {
                "Content-Type": "text/html",
            },
        )

    async def process_blacklist_post(self, flow: http.HTTPFlow) -> None:
        """
        Processes POST requests to /topic_blacklist and edits the flow
        :param flow:
        :return:
        """
        request_body = json.loads(flow.request.text)
        try:
            self.classifier_manager.set_topic_blacklist(
                self.content_classifier_name, request_body["topics"]
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

    async def process_aggressiveness_post(self, flow: http.HTTPFlow) -> None:
        """
        Processes POST requests to /aggressiveness and edits the flow
        :param flow:
        :return:
        """
        request_body = json.loads(flow.request.text)
        try:
            new_aggressiveness = float(request_body["aggressiveness"])
            self.classifier_manager.set_aggressiveness(
                self.content_classifier_name,
                new_aggressiveness,
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

    async def process_classifier_post(self, flow: http.HTTPFlow) -> None:
        """
        Processes POST requests to /classifier and edits the flow
        :param flow:
        :return:
        """
        request_body = json.loads(flow.request.text)
        try:
            new_classifier_name = request_body["classifier"]
            self.content_classifier = self.classifier_manager.get_classifier(
                new_classifier_name
            )
            self.content_classifier_name = new_classifier_name

            # Update config
            self.config.set_attribute("classifier", self.content_classifier_name)

            self.content_editor_factory.set_content_classifier(self.content_classifier)

            # recharge page
            flow.response = http.Response.make(
                201,
                '{"message": "Success"}',
                {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        except KeyError as e:
            flow.response = http.Response.make(
                400,
                "Data invalid",
                {
                    "Content-Type": "text/html",
                },
            )

    async def process_main_get(self, flow) -> None:
        """
        Process GET requests to /
        :return:
        """
        flow.response = http.Response.make(
            200,
            self.home_template.render(
                supported_topics=self.content_classifier.get_supported_topics(),
                topic_blacklist=self.classifier_manager.classifier_info[
                    self.content_classifier_name
                ].topic_blacklist,
                active_classifier=self.classifier_manager.classifier_info[
                    self.content_classifier_name
                ].to_dict(),
                classifiers=[
                    {
                        "name": classifier_info.name,
                        "nickname": classifier_info.nickname,
                        "description": classifier_info.description,
                    }
                    for classifier_info in self.classifier_manager.classifier_info.values()
                ],
            ),
            {
                "Content-Type": "text/html",
            },
        )

    async def process_reload_schemata_post(self, flow: http.HTTPFlow) -> None:
        """
        Processes POST requests to /reload_schemata and edits the flow
        :param flow:
        :return:
        """
        try:
            self.db_manager.create_schema_table()
            self.schema_reader.run()

            flow.response = http.Response.make(
                201,
                '{"message": "Schemata Reloaded Successfully"}',
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

    async def process_settings_get(self, flow) -> None:
        """
        Process GET requests to /
        :return:
        """
        flow.response = http.Response.make(
            200,
            self.settings_template.render(),
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
