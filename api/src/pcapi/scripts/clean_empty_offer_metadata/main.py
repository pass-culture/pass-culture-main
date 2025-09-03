"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-37688-clean-empty-offer-metadata/api/src/pcapi/scripts/clean_empty_offer_metadata/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offers.models import OfferMetaData
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_empty_offer_metadata() -> None:
    db.session.query(OfferMetaData).filter(
        OfferMetaData.videoUrl.is_(None),
        OfferMetaData.videoDuration.is_(None),
        OfferMetaData.videoExternalId.is_(None),
        OfferMetaData.videoThumbnailUrl.is_(None),
        OfferMetaData.videoTitle.is_(None),
    ).delete(synchronize_session=False)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    delete_empty_offer_metadata()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
