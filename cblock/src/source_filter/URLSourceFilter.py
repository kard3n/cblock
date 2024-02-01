from src.source_filter.SourceAction import SourceAction
from src.source_filter.SourceFilterInterface import SourceFilterInterface


class URLSourceFilter(SourceFilterInterface):
    def __init__(self):
        pass

    def get_action(self, source: str) -> SourceAction:
        if source in ["formella.webs.uvigo.es", "motherfuckingwebsite.com"]:
            return SourceAction.FILTER
        else:
            return SourceAction.PASS
