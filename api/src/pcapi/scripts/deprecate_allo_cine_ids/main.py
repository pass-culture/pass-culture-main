"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41854-api-message-derreur-lors-de-la-synchro-avec-allocine \
  -f NAMESPACE=deprecate_allo_cine_ids \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(old_venue_id: int, new_venue_id: int, allocine_internal_id: str) -> None:
    allocine_venue_provider = (
        db.session.query(providers_models.AllocineVenueProvider)
        .filter(
            providers_models.AllocineVenueProvider.venueId == old_venue_id,
            providers_models.AllocineVenueProvider.internalId == allocine_internal_id,
        )
        .one()
    )
    allocine_theater = (
        db.session.query(providers_models.AllocineTheater)
        .filter(
            providers_models.AllocineTheater.internalId == allocine_internal_id,
        )
        .one()
    )
    new_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == new_venue_id).one()
    logger.info(
        "Replacing AllocineVenueProvider.venueId from %i to %i for internalId %s",
        old_venue_id,
        new_venue_id,
        allocine_internal_id,
    )
    allocine_venue_provider.venueId = new_venue_id
    logger.info(
        "Replacing AllocineTheater.siret from %s to %s for internalId %s",
        allocine_theater.siret,
        new_venue.siret,
        allocine_internal_id,
    )
    allocine_theater.siret = new_venue.siret


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--old-venue-id", type=int, required=True)
    parser.add_argument("--new-venue-id", type=int, required=True)
    parser.add_argument("--allocine-internal-id", required=True)
    args = parser.parse_args()

    with atomic():
        main(
            old_venue_id=args.old_venue_id,
            new_venue_id=args.new_venue_id,
            allocine_internal_id=args.allocine_internal_id,
        )
        if args.apply:
            logger.info("Finished")
        else:
            mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")
