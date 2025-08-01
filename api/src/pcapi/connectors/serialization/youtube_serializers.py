import datetime
import re

from pydantic.v1 import BaseModel
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator


class Thumbnail(BaseModel):
    url: HttpUrl


class Thumbnails(BaseModel):
    default: Thumbnail | None
    high: Thumbnail | None
    medium: Thumbnail | None
    standard: Thumbnail | None

    def get_thumbnail_url(self) -> HttpUrl | None:
        if self.high:
            return self.high.url
        if self.medium:
            return self.medium.url
        if self.standard:
            return self.standard.url
        if self.default:
            return self.default.url
        return None


class Snippet(BaseModel):
    title: str
    thumbnails: Thumbnails


def parse_iso8601_duration_to_seconds(duration_str: str) -> int:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration format: {duration_str}")

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return int(duration.total_seconds())


class ContentDetails(BaseModel):
    duration: int

    _parse_duration = validator("duration", pre=True)(parse_iso8601_duration_to_seconds)


class VideoItem(BaseModel):
    id: str
    snippet: Snippet
    contentDetails: ContentDetails


class YoutubeApiResponse(BaseModel):
    items: list[VideoItem]
