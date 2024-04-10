from content_factory.Content import Content


class ContentFactory:
    def get_content(self) -> Content:
        return Content(
            title="Title removed by ContentBlock",
            subtitle="Subtitle removed by ContentBlock",
            summary="Summary removed by ContentBlock.",
            full="Full text removed by ContentBlock.",
            picture="https://i.imgur.com/a0Dq7Sc.png",
            video="video.mp4",
            audio="audio.wav",
            tags=["default"],
            link="https://www.example.com/",
        )
