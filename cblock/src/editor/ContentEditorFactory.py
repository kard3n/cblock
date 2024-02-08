from src.editor.editors.html_editor.HTMLEditor import HTMLEditor

from src.editor.EditorInterface import ContentEditorInterface


class ContentEditorFactory:

    def __init__(self):
        pass

    def get_content_editor(self, doctype: str) -> ContentEditorInterface:
        # TODO switch depending on doctype
        return HTMLEditor()
