"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-38002-investiguer-les-plantages-des-synchro-allocine-en-production/api/src/pcapi/scripts/investigate_allocin_crashes/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.providers import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(dry_run: bool) -> None:
    provider_id = 22  # AllocineStocks
    venue_providers = (
        db.session.query(models.VenueProvider)
        .filter_by(providerId=provider_id, isActive=True)
        .order_by(models.VenueProvider.id)
        .all()
    )
    for venue_provider in venue_providers:
        print("venue_provider.id: %s" % venue_provider.id)
        print("venue_provider.venueId: %s" % venue_provider.venueId)
    print("Finished listing %s venue providers" % len(venue_providers))


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    dry_run = not args.not_dry

    main(dry_run=dry_run)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
