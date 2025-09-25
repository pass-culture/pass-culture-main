"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-38109-nc-offerers-full-validation/api/src/pcapi/scripts/nc_offerers_full_validation/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    offerers = (
        db.session.query(offerers_models.Offerer)
        .filter_by(departementCode="988")
        .outerjoin(offerers_models.Offerer.confidenceRule)
        .filter(offerers_models.OffererConfidenceRule.confidenceLevel.is_(None))
        .all()
    )
    logger.info("Found %s caledonian offerers", len(offerers))
    for offerer in offerers:
        logger.info(
            "Set manual review for offerer %s %s (%s %s)", offerer.id, offerer.siren, offerer.postalCode, offerer.city
        )
        db.session.add(
            offerers_models.OffererConfidenceRule(
                offerer=offerer, confidenceLevel=offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
            )
        )
        history_api.add_action(
            history_models.ActionType.FRAUD_INFO_MODIFIED,
            author=None,
            offerer=offerer,
            comment="Revue manuelle de toutes les offres des acteurs calédoniens - PC-38109",
            modified_info={
                "confidenceRule.confidenceLevel": {"new_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW}
            },
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
