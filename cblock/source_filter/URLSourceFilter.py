from source_filter.Action import Action
from source_filter.SourceFilterInterface import SourceFilterInterface


class URLSourceFilter(SourceFilterInterface):
    def __init__(self):
        pass

    def get_action(self, source: str) -> Action:
        if source in ["formella.webs.uvigo.es", "motherfuckingwebsite.com"]:
            return Action.FILTER
        else:
            return Action.PASS
