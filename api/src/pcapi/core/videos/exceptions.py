class InvalidVideoUrl(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The video URL must be from the Youtube plateform, it should be public and should not be a short nor a user's profile."
        )


class YoutubeVideoNotFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "This video cannot be found on youtube. It is most likely a private video. Please check your URL."
        )
