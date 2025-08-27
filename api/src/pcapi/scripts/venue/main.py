"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/bdalbianco/PC-37480_fix_banner_image_addresses/api/src/pcapi/scripts/venue/main.py

"""

import argparse
import logging

import pcapi.core.offerers.models as offerers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    old = "https://storage.googleapis.com/passculture-metier-prod-production-assets/"
    new = "https://storage.googleapis.com/passculture-metier-prod-production-assets-fine-grained/"
    venues = db.session.query(offerers_models.Venue).filter(
        offerers_models.Venue._bannerUrl.startswith(new),
        offerers_models.Venue._bannerMeta["original_image_url"].as_string().contains(old),
    )
    count = 0
    for venue in venues:
        venue.bannerMeta["original_image_url"] = venue.bannerMeta["original_image_url"].replace(old, new)
        count += 1
    logger.info("found %i banners to fix", count)
    pass


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
        db.session.rollback()
