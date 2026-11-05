"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-44465-clear-invalid-websites \
  -f NAMESPACE=clear_invalid_websites \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(venue_ids: list[int]) -> None:
    venues = (
        db.session.query(offerers_models.Venue)
        .options(sa_orm.joinedload(offerers_models.Venue.contact))
        .filter(offerers_models.Venue.id.in_(venue_ids))
        .all()
    )

    for venue in venues:
        assert venue.contact is not None
        contact_data = offerers_schemas.VenueContactModel(
            email=venue.contact.email,
            website=None,  # clear
            phone_number=venue.contact.phone_number,
            social_medias=venue.contact.social_medias,
        )

        # update_venue saves changes and adds a row in action_history
        offerers_api.update_venue(venue, {}, {}, author=None, contact_data=contact_data)  # type: ignore[arg-type]


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--venue-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    main(args.venue_ids)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
