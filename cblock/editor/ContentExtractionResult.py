from dataclasses import dataclass, field

from schema.ContentTag import ContentTag


@dataclass
class ContentExtractionResult:
    title: str = ""
    text: str = ""
    pictures: list[str] = field(default_factory=list[str])
    categories: str = ""

    def add_value(self, value: str, tags: list[ContentTag]):
        if len(value.strip()):
            if ContentTag.TITLE in tags:
                self.title += value + " "
            elif ContentTag.CATEGORIES in tags:
                self.categories += value + " "
            elif ContentTag.PICTURE in tags:
                self.pictures.append(value)
            else:
                self.text += value + " "
