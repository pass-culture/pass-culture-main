"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=ogeber/pc-38534-remove-acceslibre-for-venues-closed-to-public   -f NAMESPACE=remove_acceslibre_when_closed_to_public   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offerers.models import AccessibilityProvider
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    count = (
        db.session.query(AccessibilityProvider)
        .join(Venue, AccessibilityProvider.venueId == Venue.id)
        .filter(Venue.isOpenToPublic.is_(False))
        .delete()
    )
    logger.info("Remove %s accessibility providers", count)


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
