"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=xordoquy/BSR_test_ci_timeout \
  -f NAMESPACE=test_ci_timeout \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import time

from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    for i in range(1, 45):
        time.sleep(60)
        logger.info("Waited %s minutes" % i)


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
