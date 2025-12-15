"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=drop \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import sys

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


COLUMNS = (
    "latitude",
    "departementCode",
    "longitude",
)


def main(timeout: int, retry: int) -> None:
    if not timeout:
        print("timeout is mandatory")
        sys.exit(1)

    retry = retry or 1

    db.session.execute(sa.text(f"SET SESSION statement_timeout={timeout}"))
    for i in range(retry):
        print(f"try {i}/{retry}")
        try:
            for column in COLUMNS:
                db.session.execute(sa.text('ALTER TABLE "venue" DROP COLUMN "%s" ' % column))
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            print("success")
            db.session.commit()
            break
    else:
        print("failure")

    db.session.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--retry", type=int)
    args = parser.parse_args()

    main(args.timeout, args.retry)

    logger.info("Finished")
    db.session.commit()
