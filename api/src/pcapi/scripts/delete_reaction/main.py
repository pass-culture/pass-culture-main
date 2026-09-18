"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43735-reaction \
  -f NAMESPACE=delete_reaction \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.reactions import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    reactions = (
        db.session.query(models.Reaction)
        .filter(
            models.Reaction.offerId.is_(None),
            models.Reaction.productId.is_(None),
        )
        .all()
    )

    logger.info(
        "Found %s reactions, ids=%s",
        len(reactions),
        ",".join(str(r.id) for r in reactions),
    )

    for reaction in reactions:
        db.session.delete(reaction)


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
