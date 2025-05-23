"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36177-eacbackcnl-traitement-en-masse-doffres-vitrines/api/src/pcapi/scripts/cnl_change_price_details/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    logger.info("Finding collective offer templates at venueId 31305 with active status and price '308,01'")
    templates_to_update = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(
            educational_models.CollectiveOfferTemplate.venueId == 31305,
            educational_models.CollectiveOfferTemplate.isActive.is_(True),
            sa.or_(
                educational_models.CollectiveOfferTemplate.priceDetail.contains("308,01"),
                educational_models.CollectiveOfferTemplate.priceDetail.contains("308.01"),
            ),
        )
        .all()
    )

    logger.info(
        "Found %d collective offer templates to update: %s",
        len(templates_to_update),
        [c.id for c in templates_to_update],
    )

    for template in templates_to_update:
        template.priceDetail = template.priceDetail.replace("308,01", "310,47")
        template.priceDetail = template.priceDetail.replace("308.01", "310,47")

    db.session.flush()


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
