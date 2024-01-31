from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from source_filter.SourceFilterInterface import SourceFilterInterface
from source_filter.URLSourceFilter import URLSourceFilter


class SourceFilterFactory():
    def get_source_filter(self, type: str) -> SourceFilterInterface:
        return URLSourceFilter()