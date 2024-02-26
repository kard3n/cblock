from dataclasses import dataclass, field

from regex import Pattern

from schema.ContentTag import ContentTag


@dataclass
class GenericSchema:
    # pattern: regex that defines the substring to match
    # the following groups can or must be used (ex: (?P<group_name>.*)):
    # content: marks the text that should be extracted. everything not part of this group will
    # be ignored (but still evaluated as part of the regex)
    pattern: Pattern = None
    tags: list[ContentTag] = field(default_factory=list[ContentTag])
    embedded_schema: str | None = (
        None  # Can be specified, if a different schema (and therefore editor) should be used for the matched content
    )
    children: None | list = (
        None  # should be set to a value other than None if the schema element has children
        # substrings matched by the child elements should never overlap
    )


# format:
#
