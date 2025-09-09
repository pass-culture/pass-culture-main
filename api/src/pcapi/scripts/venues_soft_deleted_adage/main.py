"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37793-extract-venues-adage-id-soft-deleted/api/src/pcapi/scripts/venues_soft_deleted_adage/main.py

"""

import csv
import logging
import os

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    venues: list[offerers_models.Venue] = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.adageId.is_not(None), offerers_models.Venue.isSoftDeleted.is_(True))
        .options(
            sa_orm.joinedload(offerers_models.Venue.managingOfferer).selectinload(offerers_models.Offerer.managedVenues)
        )
        .execution_options(include_deleted=True)
        .all()
    )

    logger.info("Found %s soft deleted venues with adageId", len(venues))

    results = []
    for venue in venues:
        offerer_venues_with_siret = [v for v in venue.managingOfferer.managedVenues if v.siret is not None]

        venue_result = {
            "soft_deleted_venue_id": venue.id,
            "soft_deleted_venue_name": venue.name,
            "adageId": venue.adageId,
            "destination_venue_id": None,
            "destination_venue_name": None,
            "destination_venue_adageId": None,
        }

        if len(offerer_venues_with_siret) == 1:
            [venue_with_siret] = offerer_venues_with_siret
            venue_result["destination_venue_id"] = venue_with_siret.id
            venue_result["destination_venue_name"] = venue_with_siret.name
            venue_result["destination_venue_adageId"] = venue_with_siret.adageId
        else:
            actions: list[history_models.ActionHistory] = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
                    history_models.ActionHistory.venueId == venue.id,
                )
                .all()
            )

            if len(actions) == 1:
                [action] = actions
                assert action.extraData is not None

                destination_venue_id = action.extraData["destination_venue_id"]
                venue_result["destination_venue_id"] = destination_venue_id

                destination_venue: offerers_models.Venue | None = (
                    db.session.query(offerers_models.Venue)
                    .filter(offerers_models.Venue.id == destination_venue_id)
                    .one_or_none()
                )

                if destination_venue is not None:
                    venue_result["destination_venue_name"] = destination_venue.name
                    venue_result["destination_venue_adageId"] = destination_venue.adageId
                else:
                    logger.warning(
                        "destination_venue_id %s: did not find the corresponding venue", destination_venue_id
                    )
            else:
                logger.warning("Venue %s: did not find a single venue with siret or a single action history", venue.id)

        results.append(venue_result)

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/venues_soft_deleted_adage_id.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "soft_deleted_venue_id",
                "soft_deleted_venue_name",
                "adageId",
                "destination_venue_id",
                "destination_venue_name",
                "destination_venue_adageId",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    app.app_context().push()

    main()

    logger.info("Finished")
