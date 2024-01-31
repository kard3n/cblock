from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from content_editor.ContentEditorInterface import ContentEditorInterface
from content_editor.editors.HTMLEditor import HTMLEditor


class ContentEditorFactory():

    def __init__(self):
        pass

    def get_content_editor(self, doctype: str) -> ContentEditorInterface:
        # TODO switch depending on doctype
        return HTMLEditor()