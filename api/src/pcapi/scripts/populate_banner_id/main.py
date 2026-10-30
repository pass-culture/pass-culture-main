"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42695-populate-banner-id \
  -f NAMESPACE=populate_banner_id \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import re

from pcapi import settings
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
GOOGLE_PLACES_BANNER_STORAGE_FOLDER = settings.THUMBS_FOLDER_NAME + "/google_places"
BASE_BANNER_STORAGE_FOLDER = settings.OBJECT_STORAGE_URL + "/" + GOOGLE_PLACES_BANNER_STORAGE_FOLDER + "/"


@atomic()
def main(apply: bool) -> None:
    places_info_lines = db.session.query(offerers_models.GooglePlacesInfo).filter(
        offerers_models.GooglePlacesInfo.bannerId.is_(None), offerers_models.GooglePlacesInfo._bannerUrl.is_not(None)
    )

    logger.info("Starting import of %d lines", places_info_lines.count())

    for places_info_line in places_info_lines:
        assert places_info_line._bannerUrl  #  helps mypy
        logger.info("GooglePlacesInfo with id %d has bannerUrl %s...", places_info_line.id, places_info_line._bannerUrl)
        match = re.search(f"{BASE_BANNER_STORAGE_FOLDER}(.+)", places_info_line._bannerUrl)
        if not match:
            logger.warning(
                "GooglePlacesInfo with id %d does not contains the expected base url. Banner url: %s",
                places_info_line.id,
                places_info_line._bannerUrl,
            )
            continue
        extracted_id = match.group(1)

        logger.info("... updating its bannerId to %s", extracted_id)

        places_info_line.bannerId = extracted_id

    if not apply:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(apply=args.apply)

    logger.info("Finished")
