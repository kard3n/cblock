from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from editor.ContentExtractionResult import ContentExtractionResult


class SimpleContentAnalyzer(ContentAnalyzerInterface):
    def analyze(self, content: ContentExtractionResult) -> bool:
        if content.text.__contains__("fuck"):
            return True
        return True
