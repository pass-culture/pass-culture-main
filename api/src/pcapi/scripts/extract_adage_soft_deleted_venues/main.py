"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=extract_adage_soft_deleted_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import csv
import logging
import os
from dataclasses import asdict
from dataclasses import dataclass

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


@dataclass
class Result:
    soft_deleted_venue_id: int
    soft_deleted_venue_name: str
    adageId: str
    destination_venue_id: int | None
    destination_venue_name: str | None
    destination_venue_adageId: str | None
    comment: str | None


def main() -> None:
    venues = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.adageId.is_not(None),
            offerers_models.Venue.isSoftDeleted.is_(True),
        )
        .options(
            sa_orm.joinedload(offerers_models.Venue.managingOfferer).selectinload(offerers_models.Offerer.managedVenues)
        )
        .execution_options(include_deleted=True)
        .all()
    )

    logger.info("Found %s soft deleted venues with adageId", len(venues))

    results = []
    for venue in venues:
        offerer_venues_with_siret = [
            v
            for v in venue.managingOfferer.managedVenues
            if v.siret is not None and not v.isSoftDeleted and v.id != venue.id
        ]

        assert venue.adageId is not None
        venue_result = Result(
            soft_deleted_venue_id=venue.id,
            soft_deleted_venue_name=venue.name,
            adageId=venue.adageId,
            destination_venue_id=None,
            destination_venue_name=None,
            destination_venue_adageId=None,
            comment=None,
        )
        results.append(venue_result)

        # the offerer has one other venue with siret, this is the destination venue
        if len(offerer_venues_with_siret) == 1:
            [venue_with_siret] = offerer_venues_with_siret
            venue_result.destination_venue_id = venue_with_siret.id
            venue_result.destination_venue_name = venue_with_siret.name
            venue_result.destination_venue_adageId = venue_with_siret.adageId
            continue

        actions = (
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.actionType.in_(
                    (history_models.ActionType.VENUE_REGULARIZATION, history_models.ActionType.VENUE_SOFT_DELETED)
                ),
                history_models.ActionHistory.venueId == venue.id,
            )
            .all()
        )

        regul_actions = [
            action for action in actions if action.actionType == history_models.ActionType.VENUE_REGULARIZATION
        ]
        if regul_actions:
            if len(regul_actions) > 1:
                logger.warning("Venue %s: multiple regul action history rows", venue.id)
                continue

            [action] = regul_actions
            assert action.extraData is not None

            destination_venue_id = action.extraData["destination_venue_id"]
            venue_result.destination_venue_id = destination_venue_id

            destination_venue = (
                db.session.query(offerers_models.Venue)
                .filter(offerers_models.Venue.id == destination_venue_id)
                .one_or_none()
            )

            if destination_venue is None:
                logger.warning("destination_venue_id %s: did not find the corresponding venue", destination_venue_id)
                continue

            venue_result.destination_venue_name = destination_venue.name
            venue_result.destination_venue_adageId = destination_venue.adageId
            continue

        soft_deleted_actions = [
            action for action in actions if action.actionType == history_models.ActionType.VENUE_SOFT_DELETED
        ]
        if soft_deleted_actions:
            venue_result.comment = "\n".join([action.comment for action in soft_deleted_actions if action.comment])

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
                "comment",
            ],
        )
        writer.writeheader()
        writer.writerows((asdict(r) for r in results))


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    main()

    logger.info("Finished")
