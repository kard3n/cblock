from src.content_editor.ContentEditorInterface import ContentEditorInterface
from src.content_editor.editors.html_editor.HTMLEditor import HTMLEditor


class ContentEditorFactory():

    def __init__(self):
        pass

    def get_content_editor(self, doctype: str) -> ContentEditorInterface:
        # TODO switch depending on doctype
        return HTMLEditor()