import logging

from regex import Match, regex

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content.Content import Content
from content.ContentFactory import ContentFactory
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.ContentExtractionResult import ContentExtractionResult
from exceptions.EditException import EditException
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.generic_schema.GenericSchema import GenericSchema


class GenericContentEditor(ContentEditorInterface):
    content_analyzer: ContentClassifierInterface
    content_factory: ContentFactory

    def __init__(
        self,
        content_analyzer: ContentClassifierInterface,
        content_factory: ContentFactory,
        schema_factory: SchemaFactory,
        editor_factory: ContentEditorFactory,
    ) -> None:
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory
        self.editor_factory = editor_factory
        self.schema_factory = schema_factory

    def edit(self, input_raw: str, schema: GenericSchema) -> str:
        # the current schema's pattern was evaluated in the previous recursion, and input_raw is its "content"
        # group that was passed. If input_raw is the root, it works the same way (it's as if the "previous" one just
        # matched the whole text)

        for child_schema in schema.children:
            matches_iter = regex.finditer(child_schema.pattern, input_raw)
            match_list: list[Match] = []

            for match in matches_iter:

                try:
                    if match.group("content") is not None:
                        # found a substring that matches, so we have to check for tags and do something
                        # extract start and end position of "content" group
                        match_list.append(match)

                    else:
                        # there's no closer for the opened match, return Exception
                        raise EditException(
                            f"No closer found for match: {match.group()}"
                        )
                except Exception:
                    logging.warning(
                        f"Could not find content group in match: {match.group()}"
                    )

            # we start editing from left to right. This is to avoid problems due to differing content length
            match_list.reverse()

            # check if an embedded schema has been specified, if so the editor used will be the one related
            # to the embedded schema
            if child_schema.embedded_schema is not None:
                next_editor: ContentEditorInterface = (
                    self.editor_factory.get_content_editor_by_schema_id(
                        child_schema.embedded_schema
                    )
                )
                next_schema = self.schema_factory.get_schema_by_id(
                    child_schema.embedded_schema
                )
            else:
                next_editor: ContentEditorInterface = self
                next_schema = child_schema

            for match in match_list:
                content_start: int = match.start() + match.group().find(
                    match.group("content")
                )
                content_end: int = (
                    match.start()
                    + match.group().find(match.group("content"))
                    + len(match.group("content"))
                )

                # check whether it is an element with offending content or not. If so, it will be edited
                # Otherwise, take content and pass it to the next recursive iteration
                if (
                    ContentTag.CONTAINER in child_schema.tags
                    and self.content_analyzer.classify(
                        next_editor.extract_content(match.group("content"), next_schema)
                    )
                ):
                    input_raw = (
                        input_raw[:content_start]
                        + next_editor.edit_container_element(
                            match.group("content"),
                            next_schema,
                            content=self.content_factory.get_content(),
                        )
                        + input_raw[content_end:]
                    )
                elif ContentTag.DELETE_UNCONDITIONAL in child_schema.tags:
                    # remove matched content
                    input_raw = input_raw[:content_start] + input_raw[content_end:]
                else:

                    input_raw = (
                        input_raw[:content_start]
                        + next_editor.edit(
                            match.group("content"),
                            next_schema,
                        )
                        + input_raw[content_end:]
                    )

        return input_raw

    # Extracts all content from a certain subsegment
    def extract_content(
        self,
        input_value,
        schema: GenericSchema,
        result_container: ContentExtractionResult | None = None,
    ) -> ContentExtractionResult:
        # input_value is the content extracted using the schema's pattern.
        # schema either contains ContentTag.Element, or is child of an element

        if result_container is None:
            result_container = ContentExtractionResult()

        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema_id=schema.embedded_schema
            ).extract_content(
                input_value=input_value,
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
                result_container=result_container,
            )

        if ContentTag.ANALYZE in schema.tags:
            result_container.add_value(value=input_value, tags=schema.tags)
            return result_container

        # in case the schema has children, their content should be extracted too
        if schema.children is not None:
            for child_schema in schema.children:
                matches_iter = regex.finditer(child_schema.pattern, input_value)

                for match in matches_iter:
                    if match.group("content") is not None:
                        self.extract_content(
                            match.group("content"),
                            child_schema,
                            result_container=result_container,
                        )
                    else:
                        # No content could be identified
                        raise EditException(
                            f"No closer found for match: {match.group()}"
                        )
        return result_container

    # Gets passed content, and for each identified child element applies the action specified for it
    # If a leaf tag is set, the value is edited and the child elements will be ignored
    def edit_container_element(
        self, input_value, schema: GenericSchema, content: Content
    ) -> str:
        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema.embedded_schema
            ).edit_container_element(
                input_value,
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
                content=content,
            )

        # No embedded schema has been identified, so the function continues as usual
        for tag in schema.tags:
            if tag in ContentTag.get_leaf_tags():
                return content.get_content_by_tag(tag)

        # there was no leaf tag, so we iterate through the child schemas
        for child_schema in schema.children:
            matches_iter = regex.finditer(child_schema.pattern, input_value)
            match_list: list[Match] = []

            for match in matches_iter:

                if match.group("content") is not None:
                    # found a substring that matches
                    # extract start and end position of "content" group
                    match_list.append(match)

                else:
                    # there's no closer for the opened match, return Exception
                    raise EditException(f"No closer found for match: {match.group()}")

            # we start editing from left to right. This is to avoid problems due to differing content length
            match_list.reverse()

            for match in match_list:
                input_value = self.edit_content(input_value, match, child_schema)

        return input_value

    def edit_content(self, input_raw: str, match: Match, schema: GenericSchema) -> str:

        content_start: int = match.start() + match.group().find(match.group("content"))
        content_end: int = (
            match.start()
            + match.group().find(match.group("content"))
            + len(match.group("content"))
        )

        input_raw = (
            input_raw[:content_start]
            + self.edit_container_element(
                match.group("content"),
                schema,
                self.content_factory.get_content(),
            )
            + input_raw[content_end:]
        )

        return input_raw
