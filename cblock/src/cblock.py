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

from mitmproxy import http
from src.db.DBManagerInterface import DBManagerInterface


# TODO class to load config

# TODO configure project root


class Main:
    # source_filter_factory: SourceFilterFactory
    # content_analyzer_factory: ContentAnalyzerFactory

    def __init__(self):
        logging.info("Starting CBlock")
        # self.source_filter_factory = SourceFilterFactory()
        # self.content_analyzer_factory = ContentAnalyzerFactory()
        self.db_manager: DBManagerInterface = DBManagerInterface()

    def response(self, flow: http.HTTPFlow):
        logging.info(
            f"Pretty host plus path: {flow.request.pretty_host}{flow.request.path}"
        )
        """if (
            self.source_filter_factory.get_source_filter("url").get_action(
                flow.request.pretty_host
            )
            == SourceAction.FILTER
        ):
            try:
                logging.info(f"Host: {flow.request.pretty_host}")
                # logging.info(f"Decoded response: {flow.response.text}")
                logging.info(f"{flow.response.headers.get('content-type')}")
                # if flow.response.headers.get('content-type') == "text/html":
                #    flow.response.text = flow.response.text.replace("para", "LMAO")
                logging.info(
                    f'''Analyzer return: {self.content_analyzer_factory
                             .get_content_analyzer()
                             .analyze(flow.response.text)}'''
                )
                logging.info(f"Path: {flow.request.path}")
            except ValueError as e:
                logging.info("Flow could not be parsed" + e.__str__())"""


addons = [Main()]
