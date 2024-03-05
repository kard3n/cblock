from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.EditorInterface import EditorInterface
from utils.Singleton import Singleton


class ContentEditorFactory(metaclass=Singleton):

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
        db_manager: DBManagerInterface,
    ):
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory
        self.db_manager = db_manager

    def get_content_editor(self, schema_type: str) -> EditorInterface:
        # Imports are needed due to circular imports. Editors are singletons, so there's no major performance impact
        if schema_type == "json":

            from editor.editors.json_editor.JSONEditor import JSONEditor

            return JSONEditor(
                content_analyzer=self.content_analyzer,
                content_factory=self.content_factory,
                db_manager=self.db_manager,
            )
        if schema_type == "generic":
            from editor.editors.generic_editor.GenericEditor import GenericEditor

            return GenericEditor(
                content_analyzer=self.content_analyzer,
                content_factory=self.content_factory,
                db_manager=self.db_manager,
            )

    def get_content_editor_by_schema_id(self, schema_id: str) -> EditorInterface:
        schema_type: str = self.db_manager.get_schema(schema_id).schema_type

        return self.get_content_editor(schema_type=schema_type)
