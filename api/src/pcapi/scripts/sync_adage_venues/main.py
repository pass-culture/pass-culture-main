"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39518-sync-adage-venues-downtime \
  -f NAMESPACE=sync_adage_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational.api import adage
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    # Adage API was unavailable from 2025-12-24 to 2026-01-02
    since_date = datetime.datetime(year=2025, month=12, day=23)
    adage_cultural_partners = adage.get_cultural_partners(since_date=since_date)
    logger.info(
        "Found %s adage partners modified since %s", len(adage_cultural_partners.partners), since_date.isoformat()
    )

    with atomic():
        # synchronize_adage_ids_on_venues has an atomic block, it will be converted to SAVEPOINT as we add an atomic level here
        adage.synchronize_adage_ids_on_venues(adage_cultural_partners)

        if not_dry:
            logger.info("Finished, committing")
        else:
            logger.info("Finished dry run, rollback")
            mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
