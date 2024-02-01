from src.source_filter.SourceFilterInterface import SourceFilterInterface
from src.source_filter.URLSourceFilter import URLSourceFilter


class SourceFilterFactory():
    def get_source_filter(self, type: str) -> SourceFilterInterface:
        return URLSourceFilter()