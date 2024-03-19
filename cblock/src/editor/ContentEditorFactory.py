from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_factory.ContentFactory import ContentFactory
from db.DBManagerInterface import DBManagerInterface
from editor.ContentEditorInterface import ContentEditorInterface
from schema.SchemaFactory import SchemaFactory
from utils.Singleton import Singleton


class ContentEditorFactory(metaclass=Singleton):

    def __init__(
        self,
        content_analyzer: ContentClassifierInterface,
        content_factory: ContentFactory,
        db_manager: DBManagerInterface,
    ):
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory
        self.db_manager = db_manager
        self.schema_factory: SchemaFactory = SchemaFactory(db_manager=self.db_manager)

    def get_content_editor(self, schema_type: str) -> ContentEditorInterface:
        # Imports are needed due to circular imports. Editors are singletons, so there's no major performance impact
        if schema_type == "json":

            from editor.editors.json_editor.JSONContentEditor import JSONContentEditor

            return JSONContentEditor(
                content_analyzer=self.content_analyzer,
                content_factory=self.content_factory,
                editor_factory=self,
                schema_factory=self.schema_factory,
            )
        if schema_type == "generic":
            from editor.editors.generic_editor.GenericContentEditor import (
                GenericContentEditor,
            )

            return GenericContentEditor(
                content_analyzer=self.content_analyzer,
                content_factory=self.content_factory,
                editor_factory=self,
                schema_factory=self.schema_factory,
            )

    def get_content_editor_by_schema_id(self, schema_id: str) -> ContentEditorInterface:
        schema_type: str = self.db_manager.get_schema(schema_id).schema_type

        return self.get_content_editor(schema_type=schema_type)
