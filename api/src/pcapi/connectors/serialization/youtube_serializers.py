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


def parse_iso8601_duration_to_seconds(duration_str: str | None) -> int | None:
    def get_match_value(match: re.Match[str], group: str) -> int:
        return int(match.group(group)) if match.group(group) else 0

    if not duration_str:
        return None

    match = re.match(
        r"^P(\d+Y)?(\d+M)?((?P<days>\d+)D)?(T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?)?((?P<weeks>\d+)W)?$",
        duration_str,
    )

    if not match:
        raise ValueError(f"Invalid ISO 8601 duration format: {duration_str}")

    # We ignore years, and months because they have variable duration.
    duration = datetime.timedelta(
        days=get_match_value(match, "weeks") * 7 + get_match_value(match, "days"),
        hours=get_match_value(match, "hours"),
        minutes=get_match_value(match, "minutes"),
        seconds=get_match_value(match, "seconds"),
    )
    return int(duration.total_seconds())


class ContentDetails(BaseModel):
    duration: int | None

    _parse_duration = validator("duration", pre=True)(parse_iso8601_duration_to_seconds)


class VideoItem(BaseModel):
    id: str
    snippet: Snippet
    contentDetails: ContentDetails


class YoutubeApiResponse(BaseModel):
    items: list[VideoItem]
