"""
Entry point for CBlock

Run as follows:
cd mitmproxy
pip install -e .[dev]
cd ..
mitmproxy -m regular -s cblock.py


Enable utf-8 support (needs to be done only oncer per environment):
conda env config vars set PYTHONUTF8=1
"""
import logging

from src.content_analyzer import ContentAnalyzerFactory
from mitmproxy import http

from src.source_filter import SourceAction
from src.source_filter import SourceFilterFactory

# TODO class to load config


class Main:
    source_filter_factory: SourceFilterFactory
    content_analyzer_factory: ContentAnalyzerFactory
    def __init__(self):
        self.source_filter_factory = SourceFilterFactory()
        self.content_analyzer_factory = ContentAnalyzerFactory()

    def response(self, flow: http.HTTPFlow):
        if self.source_filter_factory.get_source_filter("url").get_action(flow.request.pretty_host) == SourceAction.FILTER:
            try:
                logging.info(f"Host: {flow.request.pretty_host}")
                #logging.info(f"Decoded response: {flow.response.text}")
                logging.info(f"{flow.response.headers.get('content-type')}")
                #if flow.response.headers.get('content-type') == "text/html":
                #    flow.response.text = flow.response.text.replace("para", "LMAO")
                logging.info(f"""Analyzer return: {self.content_analyzer_factory
                             .get_content_analyzer()
                             .analyze(flow.response.text)}""")
                logging.info(f"Path: {flow.request.path}")
            except ValueError as e:
                logging.info("Flow could not be parsed" + e.__str__())


addons = [Main()]