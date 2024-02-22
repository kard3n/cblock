from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface


class SimpleContentAnalyzer(ContentAnalyzerInterface):
    def analyze(self, content: str) -> bool:
        if content.__contains__("fuck"):
            return True
        return True
