import logging
from dataclasses import dataclass

from pydantic.v1 import ValidationError

from pcapi import settings
from pcapi.connectors.serialization.youtube_serializers import VideoItem
from pcapi.connectors.serialization.youtube_serializers import YoutubeApiResponse
from pcapi.utils import requests


logger = logging.getLogger(__name__)


@dataclass
class YoutubeVideoMetadata:
    id: str
    title: str
    thumbnail_url: str
    duration: int


def get_video_metadata(video_id: str) -> YoutubeVideoMetadata | None:
    params = {
        "id": video_id,
        "key": settings.YOUTUBE_API_KEY,
        "part": "snippet,contentDetails",
    }

    try:
        response = requests.get(settings.YOUTUBE_API_URL, params=params)
        response.raise_for_status()
        api_response = YoutubeApiResponse.parse_obj(response.json())
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching YouTube video metadata for video_id %s: %s", video_id, e)
        raise requests.ExternalAPIException(True)
    except ValidationError as e:
        logger.error("Error validating YouTube API response for video_id %s: %s", video_id, e)
        raise requests.ExternalAPIException(True)

    if not api_response.items:
        logger.warning("No items found for YouTube video_id %s", video_id)
        return None

    item = api_response.items[0]
    if not item:
        return None

    return parse_item(item, video_id)


def parse_item(item: VideoItem, video_id: str) -> YoutubeVideoMetadata | None:
    thumbnail_url = item.snippet.thumbnails.get_thumbnail_url()
    if not thumbnail_url:
        logger.warning("Missing thumbnail for YouTube video_id %s", video_id)
        return None

    return YoutubeVideoMetadata(
        id=item.id,
        title=item.snippet.title,
        thumbnail_url=str(thumbnail_url),
        duration=item.contentDetails.duration,
    )
