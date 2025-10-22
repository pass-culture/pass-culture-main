"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=ogeber/pc-37882-fill-missing-video-metadata   -f NAMESPACE=fill_missing_video_metadata   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.connectors import youtube
from pcapi.core.offers import models as offers_models
from pcapi.core.videos import api as videos_api
from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.models import db
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    if not not_dry:
        mark_transaction_as_invalid()

    offer_metadata_with_video_url_but_empty_metadata = (
        db.session.query(offers_models.OfferMetaData)
        .filter(
            offers_models.OfferMetaData.videoDuration.is_(None),
            offers_models.OfferMetaData.videoExternalId.is_(None),
            offers_models.OfferMetaData.videoThumbnailUrl.is_(None),
            offers_models.OfferMetaData.videoTitle.is_(None),
            offers_models.OfferMetaData.videoUrl.is_not(None),
        )
        .all()
    )

    for offer_meta_data in offer_metadata_with_video_url_but_empty_metadata:
        assert offer_meta_data.videoUrl  # helps mypy
        try:
            video_id = videos_api.extract_video_id(offer_meta_data.videoUrl)
        except videos_exceptions.InvalidVideoUrl:
            logger.warning(
                "The video Url of this offer is not valid, removing video URL (PC-37882)",
                extra={
                    "offer_id": offer_meta_data.offerId,
                    "video_url": offer_meta_data.videoUrl,
                    "reason": "Supprimé par script lors du rattrapage le 22/20/2025",
                },
                technical_message_id="offer.video.deleted",
            )
            offer_meta_data.videoUrl = None
            continue

        metadata = youtube.get_video_metadata(video_id=video_id)
        if metadata:
            logger.info(
                "Video metadata fetched and added to offer",
                extra={
                    "offer_id": offer_meta_data.offerId,
                    "current video_url": offer_meta_data.videoUrl,
                    "new video_id": metadata.id,
                    "new video_title": metadata.title,
                    "new video thumbnail url": metadata.thumbnail_url,
                    "new video duration": metadata.duration,
                },
            )
            offer_meta_data.videoExternalId = metadata.id
            offer_meta_data.videoTitle = metadata.title
            offer_meta_data.videoThumbnailUrl = metadata.thumbnail_url
            offer_meta_data.videoDuration = metadata.duration
        else:
            logger.warning(
                "This video is private, removing video URL (PC-37882)",
                extra={
                    "offer_id": offer_meta_data.offerId,
                    "video_url": offer_meta_data.videoUrl,
                    "reason": "Supprimé par script lors du rattrapage le 22/20/2025",
                },
                technical_message_id="offer.video.deleted",
            )
            offer_meta_data.videoUrl = None


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
