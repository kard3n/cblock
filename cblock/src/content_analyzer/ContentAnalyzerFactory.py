from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer


class ContentAnalyzerFactory:
    def get_content_analyzer(self) -> ContentAnalyzerInterface:
        # TODO depending on configuration, use one or another
        return SimpleContentAnalyzer()
