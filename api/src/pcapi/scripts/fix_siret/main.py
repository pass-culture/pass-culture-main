"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bsr-fix-unconsisten-siret \
  -f NAMESPACE=fix_siret \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--siret", type=str, required=True)
    args = parser.parse_args()

    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=args.venue_id)
        .options(sa_orm.joinedload(offerers_models.Venue.managingOfferer))
        .one()
    )

    assert siren_utils.is_valid_siret(args.siret)
    assert args.siret[:9] == venue.managingOfferer.siren

    offerers_api.update_venue(venue, {"siret": args.siret}, {}, None)  # type: ignore[arg-type]

    logger.info("Finished")
