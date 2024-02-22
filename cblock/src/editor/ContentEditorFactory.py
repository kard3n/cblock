from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.ContentFactory import ContentFactory
from editor.EditorInterface import EditorInterface
from editor.editors.generic_editor.GenericEditor import GenericEditor
from editor.editors.json_editor.JSONEditor import JSONEditor


class ContentEditorFactory:

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
    ):
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory

        # TODO use singletons instead
        self.generic_editor = GenericEditor(
            content_analyzer=self.content_analyzer,
            content_factory=self.content_factory,
        )
        self.json_editor = JSONEditor(
            content_analyzer=self.content_analyzer,
            content_factory=self.content_factory,
        )

    def get_content_editor(self, editor_type: str) -> EditorInterface:
        if editor_type == "json":
            return self.json_editor
        if editor_type == "generic":
            return self.generic_editor
