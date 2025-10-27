"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=tcoudray-pass/BSR-delete-failing-venue_providers   -f NAMESPACE=delete_failing_allocine_venue_provider   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    user = db.session.query(users_models.User).filter_by(id=8195287).one()
    venue_providers = (
        db.session.query(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.id.in_([17460, 17639, 17394]))
        .all()
    )

    for venue_provider in venue_providers:
        logger.info("VenueProvider %s is going to deleted", venue_provider.id)
        providers_api.delete_venue_provider(venue_provider=venue_provider, author=user, send_email=False)


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
