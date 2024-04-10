from enum import Enum


class ContentTag(Enum):
    # Marks element as container/segment whose children should be analyzed and edited together
    CONTAINER = "e"
    # Element should be deleted unconditionally.
    # Has no effect if the element is the descendent of a CONTAINER element
    DELETE_UNCONDITIONAL = "u"
    # The following may only be used for leaf elements of the schema that are descendents of a CONTAINER element
    ANALYZE = "a"  # Needs to be set for every item that should be analyzed
    DELETE = "d"  # Element should be deleted.
    # When sensitive content is detected, the content of elements with the following tags will be replaced:
    TITLE = "t"
    SUMMARY = "s"
    FULL_CONTENT = "f"
    PICTURE = "p"
    VIDEO = "v"
    CATEGORIES = "c"
    LINK = "l"
    ORIGIN = "o"

    @classmethod
    def get_leaf_tags(cls, include_not_content: bool = True) -> list:
        """
        Returns a list of all content tags that correspond to leave elements
        :param include_not_content: (bool) If set to True, tags that aren't a content category such as "DELETE" will be included. Defaults to True
        :return:
        """
        if include_not_content:
            return [
                cls.SUMMARY,
                cls.FULL_CONTENT,
                cls.PICTURE,
                cls.VIDEO,
                cls.CATEGORIES,
                cls.DELETE,
                cls.TITLE,
                cls.LINK,
                cls.ORIGIN,
            ]
        else:
            return [
                cls.SUMMARY,
                cls.FULL_CONTENT,
                cls.PICTURE,
                cls.VIDEO,
                cls.CATEGORIES,
                cls.TITLE,
                cls.LINK,
                cls.ORIGIN,
            ]
