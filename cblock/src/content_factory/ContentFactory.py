from content_factory.Content import Content


class ContentFactory:
    def get_content(self) -> Content:
        return Content(
            title="Title",
            subtitle="Subtitle",
            summary="Pretend this is a summary.",
            full="This is a long article, that could fill multiple pages.",
            picture="picture.png",
            video="video.mp4",
            audio="audio.wav",
            tags=["default"],
        )
