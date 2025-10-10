import json
import logging
import re

from flask import current_app

from pcapi.connectors import youtube
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


VIDEO_URL_CACHE_TTL = 24 * 60 * 60  # 24 hours
YOUTUBE_INFO_CACHE_PREFIX = "youtube_video_"
# This regex is a replicate of what exists frontend-side in isYoutubeValid.ts file
# Mind that frontend / backend controls regarding video url always match.
YOUTUBE_REGEX = (
    r"^(https?://)"
    r"(www\.)?"
    r"(m\.)?"
    r"(youtube\.com\b|youtu\.be\b)"
    r"(/watch\?v=|/embed/|/v/|/e/|/)(?P<video_id>[\w-]{11})\b"
)


def extract_video_id(url: str) -> str | None:
    pattern = re.compile(YOUTUBE_REGEX)
    if match := pattern.match(url):
        return match.group("video_id")

    return None


def get_video_metadata_from_cache(video_url: str) -> youtube.YoutubeVideoMetadata | None:
    """
    This method tries to fetch video metadata that have been stored in redis

    If no metadata have been found in the cache for the given url, it requests the video API again to fetch its metadata
    (and store it in redis cache for later purpose)

    It returns the video metadata, whether it has been found in the redis cache or requested again.

    It returns None if no metadata have been found requesting the video API
    """
    video_id = extract_video_id(video_url)
    if video_id is None:
        return None
    cached_video_metadata = current_app.redis_client.get(f"{YOUTUBE_INFO_CACHE_PREFIX}{video_id}")

    if cached_video_metadata is None:
        video_metadata_retry = youtube.get_video_metadata(video_id=video_id)
        if video_metadata_retry is not None:
            json_video_metadata = json.dumps(
                {
                    "title": video_metadata_retry.title,
                    "thumbnail_url": video_metadata_retry.thumbnail_url,
                    "duration": video_metadata_retry.duration,
                }
            )
            current_app.redis_client.set(
                f"{YOUTUBE_INFO_CACHE_PREFIX}{video_metadata_retry.id}", json_video_metadata, ex=VIDEO_URL_CACHE_TTL
            )  # 24 hours
            return video_metadata_retry
        else:
            return None
    else:
        video_metadata_dict = json.loads(cached_video_metadata)
        video_metadata = youtube.YoutubeVideoMetadata(
            id=video_id,
            title=video_metadata_dict["title"],
            thumbnail_url=video_metadata_dict["thumbnail_url"],
            duration=video_metadata_dict["duration"],
        )
    return video_metadata


def remove_video_data_from_offer_metadata(
    offer_meta_data: offers_models.OfferMetaData,
    offer_id: int,
    venue_id: int,
    video_url: str,
    provider_id: int | None = None,
) -> None:
    video_metadata_fields = ["videoDuration", "videoExternalId", "videoThumbnailUrl", "videoTitle", "videoUrl"]
    for field in video_metadata_fields:
        setattr(offer_meta_data, field, None)
    logger.info(
        "Video has been deleted from offer",
        extra={
            "offer_id": offer_id,
            "venue_id": venue_id,
            "video_url": video_url,
            "provider_id": provider_id,
        },
        technical_message_id="offer.video.deleted",
    )


def upsert_video_and_metadata(
    video_url: str,
    offer: offers_models.Offer,
    provider_id: int | None = None,
) -> None:
    cached_video_metadata = get_video_metadata_from_cache(video_url)
    if cached_video_metadata is None:
        return None
    if offer.metaData is None:
        offer.metaData = offers_models.OfferMetaData(offer=offer)
        logger.info(
            "Video has been added to offer",
            extra={
                "offer_id": offer.id,
                "venue_id": offer.venueId,
                "video_url": video_url,
                "provider_id": provider_id,
            },
            technical_message_id="offer.video.added",
        )
    elif offer.metaData.videoUrl is None:
        logger.info(
            "Video has been added to offer",
            extra={
                "offer_id": offer.id,
                "venue_id": offer.venueId,
                "video_url": video_url,
                "provider_id": provider_id,
            },
            technical_message_id="offer.video.added",
        )
    else:
        logger.info(
            "Video has been updated on offer",
            extra={
                "offer_id": offer.id,
                "venue_id": offer.venueId,
                "video_url": video_url,
                "provider_id": provider_id,
            },
            technical_message_id="offer.video.updated",
        )
    offer.metaData.videoExternalId = cached_video_metadata.id
    offer.metaData.videoTitle = cached_video_metadata.title
    offer.metaData.videoThumbnailUrl = cached_video_metadata.thumbnail_url
    offer.metaData.videoDuration = cached_video_metadata.duration
    offer.metaData.videoUrl = video_url
    db.session.add(offer.metaData)
