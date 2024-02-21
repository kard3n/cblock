from enum import Enum


class ContentTag(Enum):
    ELEMENT = "e"  # Marks element as container/segment, whose children should be analyzed together
    DELETE = "d"  # Element should be deleted.
    DELETE_LEAVE_ONE = "o"  # Child elements should be deleted, but at least one must remain (for lists).
    DELETE_UNCONDITIONAL = "u"  # element should be deleted unconditionally
    TITLE = (
        "t"  # A leaf element that contains a title as value. The action will be REPLACE
    )
    SUMMARY = "s"  # A leaf element that contains a summary as value. The action will be REPLACE
    FULL_CONTENT = (
        "f"  # A leaf element whose value is a larger text. The action will be REPLACE
    )
    PICTURE = "p"  # A leaf element that has a picture as its value. The action will be REPLACE
    VIDEO = (
        "v"  # A leaf element that has a videos as its value. The action will be REPLACE
    )
    CATEGORIES = (
        "c"  # A leaf element that contains one or more tags/categories for the content
    )
    ANALYZE = "a"  # Needs to be set for every item that should be analyzed

    @classmethod
    def get_leaf_tags(cls) -> list:
        return [
            cls.SUMMARY,
            cls.FULL_CONTENT,
            cls.PICTURE,
            cls.VIDEO,
            cls.CATEGORIES,
            cls.ANALYZE,
        ]
