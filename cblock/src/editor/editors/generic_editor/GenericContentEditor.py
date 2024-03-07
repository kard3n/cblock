import logging

from regex import Match, regex

from content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.ContentExtractionResult import ContentExtractionResult
from exceptions.EditException import EditException
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.generic_schema.GenericSchema import GenericSchema


class GenericContentEditor(ContentEditorInterface):
    content_analyzer: ContentAnalyzerInterface
    content_factory: ContentFactory

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
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

                if match.group("content") is not None:
                    # found a substring that matches, so we have to check for tags and do something
                    # extract start and end position of "content" group
                    match_list.append(match)

                else:
                    # there's no closer for the opened match, return Exception
                    raise EditException(f"No closer found for match: {match.group()}")

            # we start editing from left to right. This is to avoid problems due to differing content length
            match_list.reverse()

            # check if an embedded schema has been specified, the editor used will be changed to the one related
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
                content_start: int = (
                    match.start()
                    + regex.search(match.group("content"), match.group()).start()
                )
                content_end: int = (
                    match.start()
                    + regex.search(match.group("content"), match.group()).end()
                )

                # check whether it is an element with offending content or not. If so, it will be edited
                # Otherwise, take content and pass it to the next recursive iteration
                if (
                    ContentTag.ELEMENT in child_schema.tags
                    and self.content_analyzer.analyze(
                        next_editor.extract_content(match.group("content"), next_schema)
                    )
                ):
                    input_raw = (
                        input_raw[:content_start]
                        + next_editor.apply_action(
                            match.group("content"),
                            next_schema,
                            content=self.content_factory.get_content(),
                        )
                        + input_raw[content_end:]
                    )
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

        # if schema has the "analyze" tag, the value gets returned
        if ContentTag.ANALYZE in schema.tags:
            result_container.text += input_value
            return result_container

        # schema did not mark this as a leaf element, therefore it should have children whose content
        # needs to be extracted

        for child_schema in schema.children:
            matches_iter = regex.finditer(child_schema.pattern, input_value)

            for match in matches_iter:
                if match.group("content") is not None:
                    self.extract_content(
                        match.group("content"),
                        child_schema,
                        result_container=result_container,
                    )

                    if child_schema.children is None or child_schema.children == []:
                        result_container.text += " "
                else:
                    # No content could be identified
                    raise EditException(f"No closer found for match: {match.group()}")
        return result_container

    # Gets passed content, and for each identified child element applies the action specified for it
    # If a leaf tag is set, the value is edited and the child elements will be ignored
    def apply_action(self, input_value, schema: GenericSchema, content: Content) -> str:
        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema.embedded_schema
            ).apply_action(
                input_value,
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
                content=content,
            )

        # No embedded schema has been identified, so the function continues as usual
        for tag in schema.tags:
            if tag == ContentTag.TITLE:
                return content.title
            if tag == ContentTag.SUMMARY:
                return content.summary
            if tag == ContentTag.FULL_CONTENT:
                return content.full
            if tag == ContentTag.PICTURE:
                return content.video
            if tag == ContentTag.CATEGORIES:
                result = ""
                for cat in content.tags:
                    result += cat + " "
                return result[0:-1]

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

        content_start: int = (
            match.start() + regex.search(match.group("content"), match.group()).start()
        )
        content_end: int = (
            match.start() + regex.search(match.group("content"), match.group()).end()
        )

        input_raw = (
            input_raw[:content_start]
            + self.apply_action(
                match.group("content"),
                schema,
                self.content_factory.get_content(),
            )
            + input_raw[content_end:]
        )

        return input_raw
