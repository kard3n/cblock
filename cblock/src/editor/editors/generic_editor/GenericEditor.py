from regex import Match, regex

from src.content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from src.content_factory.Content import Content
from src.content_factory.ContentFactory import ContentFactory
from src.editor.EditorInterface import EditorInterface
from src.exceptions.EditException import EditException
from src.schema.ContentTag import ContentTag
from src.schema.generic_schema.GenericSchema import GenericSchema


class GenericEditor(EditorInterface):
    content_analyzer: ContentAnalyzerInterface
    content_factory: ContentFactory

    def __init__(
        self,
        content_analyzer: ContentAnalyzerInterface,
        content_factory: ContentFactory,
    ) -> None:
        self.content_analyzer = content_analyzer
        self.content_factory = content_factory

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

            for match in match_list:
                # check whether it is an element with offending content or not. If so, it will be edited
                # else, take content and pass it to the next recursive iteration
                if (
                    ContentTag.ELEMENT in child_schema.tags
                    and self.content_analyzer.analyze(
                        self.extract_content(input_raw, child_schema)
                    )
                ):
                    input_raw = self.edit_content(
                        input_value=input_raw, match=match, schema=child_schema
                    )
                else:
                    content_start: int = (
                        match.start()
                        + regex.search(match.group("content"), match.group()).start()
                    )
                    content_end: int = (
                        match.start()
                        + regex.search(match.group("content"), match.group()).end()
                    )

                    input_raw = (
                        input_raw[:content_start]
                        + self.edit(match.group("content"), child_schema)
                        + input_raw[content_end:]
                    )

        return input_raw

    # Extracts all content from a certain subsegment
    def extract_content(self, input_value, schema: GenericSchema) -> str:
        # input_value is the content extracted using the schema's pattern.
        # schema either contains ContentTag.Element, or is child of an element

        # if schema has the "analyze" tag, the value gets returned
        if ContentTag.ANALYZE in schema.tags:
            return input_value

        # schema did not mark this as a leaf element, therefore it should have children whose content
        # needs to be extracted
        result: str = ""  # saves the result

        for child_schema in schema.children:
            matches_iter = regex.finditer(child_schema.pattern, input_value)

            for match in matches_iter:
                if match.group("content") is not None:
                    result += self.extract_content(match.group("content"), child_schema)
                else:
                    # No content could be identified
                    raise EditException(f"No closer found for match: {match.group()}")

        return result

    # Gets passed content, and for each identified child element applies the action specified for it
    # If a leaf tag is set, the value is edited and the child elements will be ignored
    def apply_action(self, input_value, schema: GenericSchema, content: Content) -> str:
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

        # there was no tag, so we iterate through the child schema
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

    def edit_content(
        self, input_value: str, match: Match, schema: GenericSchema
    ) -> str:

        content_start: int = (
            match.start() + regex.search(match.group("content"), match.group()).start()
        )
        content_end: int = (
            match.start() + regex.search(match.group("content"), match.group()).end()
        )

        input_value = (
            input_value[:content_start]
            + self.apply_action(
                match.group("content"),
                schema,
                self.content_factory.get_content(),
            )
            + input_value[content_end:]
        )

        return input_value
