"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=index_caledonian_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core import search
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    if not FeatureToggle.WIP_ENABLE_CALEDONIAN_OFFERS_BOOKABLE.is_active():
        raise Exception("Can't reindex because WIP_ENABLE_CALEDONIAN_OFFERS_BOOKABLE is not active")

    venue_ids = (
        db.session.query(sa.func.array_agg(offerers_models.Venue.id))
        .join(offerers_models.Venue.managingOfferer)
        .filter(offerers_models.Offerer.is_caledonian)
        .scalar()
    )

    logger.info("Reindex venue ids: %s", venue_ids)

    if args.not_dry:
        search.async_index_venue_ids(venue_ids, search.IndexationReason.OFFERER_ACTIVATION)
        search.async_index_offers_of_venue_ids(venue_ids, search.IndexationReason.OFFERER_ACTIVATION)
        logger.info("Finished")
    else:
        logger.info("Finished dry run")
