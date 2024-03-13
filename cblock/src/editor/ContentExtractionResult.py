from dataclasses import dataclass, field


@dataclass
class ContentExtractionResult:
    text: str = ""
    pictures: list[str] = field(default_factory=list[str])
    categories: str = ""
