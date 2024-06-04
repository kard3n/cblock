import logging

from bs4 import BeautifulSoup, Tag
from regex import regex

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from content_factory.Content import Content
from content_factory.ContentFactory import ContentFactory
from editor.ContentEditorFactory import ContentEditorFactory
from editor.ContentEditorInterface import ContentEditorInterface
from editor.ContentExtractionResult import ContentExtractionResult
from schema.ContentTag import ContentTag
from schema.SchemaFactory import SchemaFactory
from schema.html_schema.HTMLSchema import HTMLSchema


class HTMLContentEditor(ContentEditorInterface):
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

    def edit(self, input_raw: str, schema: HTMLSchema) -> str:

        try:
            soup = BeautifulSoup(input_raw, "lxml")

        except Exception as e:
            logging.warning(f"Error parsing input to HTML representation: {e}")
            return input_raw

        try:
            self.__explore_parsed(element=soup, schema=schema)
        except Exception as e:
            logging.warning(f"Error editing input: {e}")
            return input_raw

        return soup.__str__()

    def extract_content(
        self,
        input_value: str,
        schema: HTMLSchema,
        result_container: ContentExtractionResult | None = None,
    ) -> ContentExtractionResult:
        """
        Exists only for calls from other editors.
        :param input_value:
        :param schema:
        :param result_container:
        :return:
        """
        return self.extract_content_parsed(
            element=BeautifulSoup(input_value, "lxml"), schema=schema
        )

    def extract_content_parsed(
        self,
        element: Tag,
        schema: HTMLSchema,
        result_container: ContentExtractionResult | None = None,
    ) -> ContentExtractionResult:
        """
        Extracts all content from the given element according to schema
        :param element:
        :param schema:
        :param result_container:
        :return: (ContentExtractionResult)
        """

        if result_container is None:
            result_container = ContentExtractionResult()

        for attribute in schema.attributes_to_edit:
            if (
                attribute in element.attrs
                and ContentTag.ANALYZE in schema.attributes_to_edit[attribute]
            ):
                result_container.add_value(
                    value=element.attrs[attribute],
                    tags=schema.attributes_to_edit[attribute],
                )

        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema_id=schema.embedded_schema
            ).extract_content(
                input_value=element.get_text(),
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
                result_container=result_container,
            )

        # if schema has the "analyze" tag, the value gets returned
        if ContentTag.ANALYZE in schema.content_tags:
            result_container.add_value(value=element.text, tags=schema.content_tags)

            return result_container

        # in case the "analyze" tag isn't set and the schema has children, their content should be extracted too
        if schema.children is not None:
            for child_schema in schema.children:
                for matched_element in element.find_all(
                    child_schema.html_tag,
                    attrs=child_schema.attributes_regex,
                    recursive=child_schema.search_recursive,
                ):
                    # If the matched element does not have one of the blacklisted attributes, edit it
                    if not self.has_attribute_overlap(
                        element=matched_element, attributes=child_schema.not_attributes
                    ) and self._multival_attributes_match(
                        matched_element, attributes=child_schema.attributes_multival
                    ):
                        self.extract_content_parsed(
                            matched_element, child_schema, result_container
                        )

        return result_container

    def _multival_attributes_match(self, element: Tag, attributes: {}):
        """
        Return true if element has all the attributes and they contain all the specified values
        :param element:
        :param attributes:
        :return:
        """

        for attribute in attributes.keys():
            if attribute in element.attrs.keys():
                element_attr_values = element.attrs[attribute].split()
                for value in attributes[attribute]:
                    if value not in element_attr_values:
                        return False
            else:
                return False
        return True

    def has_attribute_overlap(self, element: Tag, attributes: list[str]) -> bool:
        """
        Returns True if element has at least one of the attributes specified in attributes
        :param element:
        :param attributes:
        :return:
        """
        for attribute in attributes:
            if element.has_attr(attribute):
                return True
        return False

    def __explore_parsed(self, element: Tag, schema: HTMLSchema):
        """
        Explores the element and it's children, any container element found is edited
        :param element:
        :param schema:
        :return:
        """

        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema.embedded_schema
            ).edit(
                element.__str__(),
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
            )

        if (
            ContentTag.CONTAINER in schema.content_tags
            and self.content_analyzer.classify(
                content=self.extract_content_parsed(element=element, schema=schema)
            )
        ):
            self.__edit_container_element_parsed(
                element=element,
                schema=schema,
                content=self.content_factory.get_content(),
            )
        elif ContentTag.DELETE_UNCONDITIONAL in schema.content_tags:
            # Deletes the whole element, not just its content
            element.decompose()
        else:
            for child_schema in schema.children:
                matched_elements = element.find_all(
                    child_schema.html_tag,
                    attrs=child_schema.attributes_regex,
                    recursive=child_schema.search_recursive,
                )
                for child_element in matched_elements:
                    # check that the child does not have one of the black-listed attributes
                    if self.has_attribute_overlap(
                        element=child_element, attributes=child_schema.not_attributes
                    ) or not self._multival_attributes_match(
                        child_element, attributes=child_schema.attributes_multival
                    ):
                        return
                    self.__explore_parsed(child_element, child_schema)

    def edit_container_element(
        self, input_value, schema: HTMLSchema, content: Content
    ) -> any:
        return self.__extract_body_if_not_in_input(
            input_str=input_value,
            output_str=self.__edit_container_element_parsed(
                element=BeautifulSoup(input_value, "lxml"),
                schema=schema,
                content=content,
            ).__str__(),
        )

    # Gets passed content, and for each identified child element applies the action specified for it
    # If a leaf tag is set, the value is edited and the child elements will be ignored
    def __edit_container_element_parsed(
        self, element: Tag, schema: HTMLSchema, content: Content
    ) -> any:
        """
        Traverses the element according to the schema and edits matching leaf elements
        :param element:
        :param schema:
        :param content:
        :return:
        """

        if schema.embedded_schema is not None:
            return self.editor_factory.get_content_editor_by_schema_id(
                schema.embedded_schema
            ).edit_container_element(
                element.__str__(),
                schema=self.schema_factory.get_schema_by_id(schema.embedded_schema),
                content=content,
            )

            # the element is not a leaf, so the exploration continues further down according to schema

        if len(set(ContentTag.get_leaf_tags()) & set(schema.content_tags)) > 0:
            # In case this element is a leaf, all children are deleted and the new content inserted as this element's only child
            for tag in schema.content_tags:
                if tag in ContentTag.get_leaf_tags():
                    element.clear()
                    element.insert(
                        new_child=content.get_content_by_tag(tag), position=1
                    )
                    break
        else:
            for child_schema in schema.children:
                matched_elements = element.find_all(
                    child_schema.html_tag,
                    attrs=child_schema.attributes_regex,
                    recursive=child_schema.search_recursive,
                )
                for item in matched_elements:
                    if not self.has_attribute_overlap(
                        element=item, attributes=child_schema.not_attributes
                    ) and self._multival_attributes_match(
                        item, attributes=child_schema.attributes_multival
                    ):
                        self.__edit_container_element_parsed(
                            element=item, schema=child_schema, content=content
                        )

        # Edit attributes:
        for attribute in schema.attributes_to_edit:
            if attribute in element.attrs.keys() and len(
                set(schema.attributes_to_edit[attribute])
                & set(ContentTag.get_leaf_tags())
            ):
                element.attrs[attribute] = content.get_content_for_tags(
                    content_tags=schema.attributes_to_edit[attribute]
                )
        return element

    def __extract_body_if_not_in_input(self, input_str: str, output_str: str) -> str:
        """
        If input_str does not contain <body> element, returns only the content of the <body> added automatically by BeautifulSoup to output_str
        Otherwise returns output_str without changing anything
        :param input_str:
        :param output_str:
        :return: (str)
        """

        if regex.search(
            pattern=regex.compile(r".*?<body.*?>.*?<\/body.*?>"), string=input_str
        ):
            return output_str
        else:
            # return "".join(soup.body.contents)  # For some reason isn't updated???
            return regex.search(
                pattern=regex.compile(r"<body.*?>(?P<content>.*?)<\/body.*?>"),
                string=output_str,
            ).group("content")
