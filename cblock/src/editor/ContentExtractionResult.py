from dataclasses import dataclass, field


@dataclass
class ContentExtractionResult:
    title: str = ""
    text: str = ""
    pictures: list[str] = field(default_factory=list[str])
    categories: str = ""
