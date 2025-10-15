import abc
import dataclasses
import re

from pcapi.connectors import youtube

from . import exceptions


@dataclasses.dataclass
class VideoMetadata:
    id: str
    title: str
    thumbnail_url: str
    duration: int


class VideoPlatform(abc.ABC):
    CACHE_PREFIX: str
    BASE_URL_REGEX: str
    URL_REGEX: str

    display_name: str

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        if not isinstance(url, str):
            return False

        pattern = re.compile(cls.BASE_URL_REGEX)
        return bool(pattern.match(url))

    @classmethod
    @abc.abstractmethod
    def get_video_id(cls, url: str) -> str:
        pass

    @abc.abstractmethod
    def fetch_metadata(self, video_id: str) -> VideoMetadata | None:
        pass


class YouTubePlatform(VideoPlatform):
    CACHE_PREFIX = "youtube_video_"
    # This regex is a replicate of what exists frontend-side in isYoutubeValid.ts file
    # Mind that frontend / backend controls regarding video url always match.
    BASE_URL_REGEX = (
        r"^(https?://)"
        r"(www\.)?"
        r"(m\.)?"
        r"(youtube\.com\b|youtu\.be\b)"
    )
    URL_REGEX = BASE_URL_REGEX + r"(/watch\?v=|/embed/|/v/|/e/|/)(?P<video_id>[\w-]{11})\b"
    display_name = "YouTube"

    @classmethod
    def get_video_id(cls, url: str) -> str:
        pattern = re.compile(cls.URL_REGEX)
        if match := pattern.match(url):
            return match.group("video_id")
        raise exceptions.InvalidYoutubeVideoUrl()

    def fetch_metadata(self, video_id: str) -> VideoMetadata | None:
        if metadata := youtube.get_video_metadata(video_id=video_id):
            return VideoMetadata(
                id=metadata.id,
                title=metadata.title,
                thumbnail_url=metadata.thumbnail_url,
                duration=metadata.duration,
            )
        raise exceptions.YoutubeVideoNotFound()


AVAILABLE_PLATFORMS = [cls for cls in VideoPlatform.__subclasses__() if not cls.__abstractmethods__]


def get_supported_platform_names() -> list[str]:
    return [cls.display_name for cls in AVAILABLE_PLATFORMS]


def get_platform_for_url(video_url: str) -> VideoPlatform:
    available_platforms_classes: list[type[VideoPlatform]] = AVAILABLE_PLATFORMS
    for PlatformCls in available_platforms_classes:
        if PlatformCls.is_valid_url(video_url):
            return PlatformCls()
    available_platforms = ", ".join(get_supported_platform_names())
    raise exceptions.UnsupportedVideoUrlError(available_platforms)
