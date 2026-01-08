"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39450-rattrapage-des-erp-venues-autre-ou-offre-numerique-avec-offres \
  -f NAMESPACE=migrate_erp_other_or_digital_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.schemas as offerers_schemas
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(
    activity: offerers_models.Activity | None, venue_ids: list[int] | None, fill_with_activity_other: bool = False
) -> None:
    if activity and venue_ids:
        updated_venues_count = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id.in_(venue_ids))
            .update({"activity": activity}, synchronize_session=False)
        )
        logger.info(
            "migrate_erp_other_or_digital_venues: updated %s venues activity from NULL/DIGITAL to %s",
            updated_venues_count,
            activity.name,
            extra={"venue_ids": venue_ids},
        )
        return

    if fill_with_activity_other:
        updated_venues_count = (
            db.session.query(offerers_models.Venue)
            .filter(
                offerers_models.Venue.isOpenToPublic == True,
                sa.or_(
                    offerers_models.Venue.activity.is_(None),
                    offerers_models.Venue.activity == offerers_models.Activity.NOT_ASSIGNED,
                ),
                offerers_models.Venue.venueTypeCode.in_(
                    [offerers_schemas.VenueTypeCode.OTHER, offerers_schemas.VenueTypeCode.DIGITAL]
                ),
            )
            .update({"activity": offerers_models.Activity.OTHER.name}, synchronize_session=False)
        )
        logger.info(
            "migrate_erp_other_or_digital_venues: updated %s venues activity from NULL/DIGITAL to OTHER",
            updated_venues_count,
        )
        return
    logger.warning(
        "Missing activity / venue_ids or fill_with_activity_other",
        extra={
            "activity": activity,
            "venue_ids": venue_ids,
            "fill_with_activity_other": fill_with_activity_other,
        },
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-ids", nargs="*", type=int, help="venue ids to set")
    parser.add_argument("--activity", type=str, help="activity to set")
    parser.add_argument("--set-remaining-venues-to-other", action="store_true")
    args = parser.parse_args()

    main(
        activity=offerers_models.Activity[args.activity] if args.activity else None,
        venue_ids=args.venue_ids,
        fill_with_activity_other=args.set_remaining_venues_to_other,
    )

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
