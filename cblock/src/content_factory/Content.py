from dataclasses import dataclass

from schema.ContentTag import ContentTag


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

    def get_content_by_tag(self, content_tag: ContentTag) -> str | None:
        if content_tag == ContentTag.TITLE:
            return self.title
        elif content_tag == ContentTag.SUMMARY:
            return self.summary
        elif content_tag == ContentTag.FULL_CONTENT:
            return self.full
        elif content_tag == ContentTag.PICTURE:
            return self.video
        elif content_tag == ContentTag.LINK:
            return self.link
        elif content_tag == ContentTag.ORIGIN:
            return self.origin
        elif content_tag == ContentTag.CATEGORIES:
            result = ""
            for cat in self.tags:
                result += cat + " "
            return result[0:-1]
        elif content_tag == ContentTag.DELETE:
            return ""

        return "No Content for Tag: " + content_tag.name
