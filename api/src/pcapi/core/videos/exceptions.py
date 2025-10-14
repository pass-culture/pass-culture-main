class InvalidYoutubeVideoUrl(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The video URL must be from the Youtube plateform, it should be public and should not be a short nor a user's profile."
        )


class YoutubeVideoNotFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "This video cannot be found on youtube. It is most likely a private video. Please check your URL."
        )


class UnsupportedVideoUrlError(Exception):
    def __init__(self, available_platforms: str):
        message = (
            f"L'URL vidéo n'est pas supportée. "
            f"Veuillez utiliser une URL d'une des plateformes suivantes : {available_platforms}"
        )
        super().__init__(message)
