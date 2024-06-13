from dataclasses import dataclass

from schema.ContentTag import ContentTag


@dataclass
class Content:
    title: str = "Title removed by CBlock"
    subtitle: str = "Subtitle removed by CBlock"
    summary: str = "Summary removed by CBlock"
    full: str = "Full Content removed by CBlock"  # Example: an article
    picture: str = "https://i.imgur.com/a0Dq7Sc.png"
    video: str = "video.mp4"
    audio: str = "audio.mp3"
    link: str = "https://www.example.com/"
    origin: str = "ContentBlock"
    tags: list[str] = list

    def get_content_by_tag(self, content_tag: ContentTag) -> str:
        """
        Given a ContentTag object, returns the instance's corresponding content
        :param content_tag:
        :return:(str)
        """
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

    def get_content_for_tags(self, content_tags: list[ContentTag]) -> str | None:
        """
        Given a list of ContentTags, returns the instance's corresponding content to one of them
        :param content_tags: (list[ContentTag])
        :return:(str)
        """
        if ContentTag.TITLE in content_tags:
            return self.title
        elif ContentTag.SUMMARY in content_tags:
            return self.summary
        elif ContentTag.FULL_CONTENT in content_tags:
            return self.full
        elif ContentTag.PICTURE in content_tags:
            return self.picture
        elif ContentTag.LINK in content_tags:
            return self.link
        elif ContentTag.ORIGIN in content_tags:
            return self.origin
        elif ContentTag.CATEGORIES in content_tags:
            result = ""
            for cat in self.tags:
                result += cat + " "
            return result[0:-1]
        elif ContentTag.DELETE in content_tags:
            return ""

        return "No Content for Tags: " + [tag.name for tag in content_tags].__str__()
