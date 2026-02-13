"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39384 \
  -f NAMESPACE=create_artist_mini_thumbs \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi import settings
from pcapi.app import app
from pcapi.core import object_storage
from pcapi.core.artist import api as artist_api
from pcapi.core.artist.models import Artist
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    logger.info("Starting artist mini thumb backfill (dry=%s)", not not_dry)

    # List existing mini thumbs to skip artists that already have them
    mini_thumbs_folder = f"{settings.ARTIST_MINI_THUMBS_FOLDER_NAME}"
    logger.info("Listing existing mini thumbs from folder: %s", mini_thumbs_folder)

    existing_files = object_storage.list_files(mini_thumbs_folder, max_results=100000)
    mediation_uuids_with_mini_thumbs = {
        file_path.split("/")[-1] for file_path in existing_files if not file_path.endswith(".type")
    }
    logger.info("Found %d existing mini thumbs", len(mediation_uuids_with_mini_thumbs))

    # select artists that don't have mini thumbs and have a mediation uuid
    artists = (
        db.session.query(Artist.id, Artist.mediation_uuid)
        .filter(Artist.mediation_uuid.is_not(None))
        .filter(Artist.mediation_uuid.notin_(mediation_uuids_with_mini_thumbs))
        .all()
    )

    total = len(artists)
    logger.info("Found %d artists to process", total)

    processed = 0

    for artist_id, mediation_uuid in artists:
        try:
            image_list = object_storage.get_public_object(
                folder=settings.ARTIST_THUMBS_FOLDER_NAME,
                object_id=mediation_uuid,
            )

            if not_dry:
                artist_api.store_mini_thumb(image_list[0], mediation_uuid)
            else:
                logger.info("Dry run, would create mini thumb for artist %s", artist_id)

            processed += 1

        except Exception as e:
            logger.warning(
                "Error processing artist %s with mediation uuid %s", artist_id, mediation_uuid, extra={"exc": e}
            )

    logger.info("Finished mini thumb backfill")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
