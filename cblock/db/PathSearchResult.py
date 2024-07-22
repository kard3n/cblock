from dataclasses import dataclass


@dataclass
class PathSearchResult:
    id: str
    path: str
    allowed_subdomains: list[str]
