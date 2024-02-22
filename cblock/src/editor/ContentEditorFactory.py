from editor.EditorInterface import EditorInterface


class ContentEditorFactory:

    def __init__(self):
        pass

    def get_content_editor(self, doctype: str) -> EditorInterface:
        # TODO switch depending on doctype
        return HTMLEditor()
