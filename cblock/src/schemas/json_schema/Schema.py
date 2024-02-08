from enum import Enum


class ContentTag(str, Enum):
    REPLACE = (
        "r",
    )  # Element should be replaced according to tag. If it has children, the option applies to them
    DELETE = ("d",)  # Element should be deleted
    DELETE_LEAVE_ONE = (
        "o",
    )  # Element should be deleted, but at least one must remain (for lists)
    TITLE = ("t",)  # A leaf element that contains a title as value
    SUMMARY = ("s",)  # A leaf element that contains a summary as value
    BODY = ("b",)  # A leaf element whose value is a larger text
    PICTURE = ("p",)  # A leaf element that has a picture as its value
    VIDEO = ("v",)  # A leaf element that has a videos as its value
    CATEGORIES = (
        "c",
    )  # A leaf element that contains one or more tags/categories for the content
    DONT_ANALYZE = "d"  # For elements that should be replaced according to another tag, but do not need to be analyzed
