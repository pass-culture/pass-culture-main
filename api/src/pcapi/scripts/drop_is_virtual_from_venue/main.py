"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41636-api-post-regul-clean-virtual-8-b-8-supprimer-virtuel-des-models \
  -f NAMESPACE=drop_is_virtual_from_venue \
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


def main(lock_timeout: int, retry: int) -> None:
    if not lock_timeout:
        print("timeout is mandatory")
        sys.exit(1)

    retry = retry or 1

    lock_timeout_statment = f"SET SESSION lock_timeout='{lock_timeout}s'"
    db.session.execute(sa.text(lock_timeout_statment))
    for i in range(retry):
        print(f"try {i}/{retry}")
        try:
            db.session.execute(sa.text('ALTER TABLE "venue" DROP COLUMN IF EXISTS "isVirtual"'))
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            print("success")
            db.session.commit()
            break
    else:
        print("failure")

    db.session.execute(
        sa.text("SET SESSION lock_timeout=:lock_timeout"),
        {"lock_timeout": settings.DATABASE_STATEMENT_TIMEOUT},
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--retry", type=int)
    parser.add_argument("--lock-timeout", type=int, default=5, help="lock timeout in seconds")
    args = parser.parse_args()

    main(lock_timeout=args.lock_timeout, retry=args.retry)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
