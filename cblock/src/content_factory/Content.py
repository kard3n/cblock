from dataclasses import dataclass


@dataclass
class Content:
    title: str = "Title removed by CBlock"
    subtitle: str = "Subtitle removed by CBlock"
    summary: str = "Summary removed by CBlock"
    full: str = "Full Content removed by CBlock"  # Example: an article
    picture: str = "picture.png"
    video: str = "video.mp4"
    audio: str = "audio.mp3"
    link: str = "https://www.example.com/"
    origin: str = "ContentBlock"
    tags: list[str] = list
