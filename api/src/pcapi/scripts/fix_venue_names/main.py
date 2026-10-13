"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=fix_venue_names \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.history.api import add_action
from pcapi.core.history.models import ActionType
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    venues = db.session.query(Venue).yield_per(1_000)

    count = 0
    for venue in venues:
        name_strip = venue.name.strip()

        if venue.name != name_strip:
            count += 1
            add_action(
                action_type=ActionType.INFO_MODIFIED,
                author=None,
                venue=venue,
                modified_info={"name": {"old_info": venue.name, "new_info": name_strip}},
                comment="PC-44070",
            )
            venue.name = name_strip

    logger.info("Fixed %s venues", count)
    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
