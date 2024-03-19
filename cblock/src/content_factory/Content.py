from dataclasses import dataclass


@dataclass
class Content:
    title: str = "Title"
    subtitle: str = "Subtitle"
    summary: str = "Summary"
    full: str = "Full Content"  # Example: an article
    picture: str = "picture.png"
    video: str = "video.mp4"
    audio: str = "audio.mp3"
    link: str = "example.com"
    origin: str = "ContentBlock"
    tags: list[str] = list
