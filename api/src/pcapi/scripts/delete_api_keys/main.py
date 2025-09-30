"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-drop-api-keys/api/src/pcapi/scripts/delete_api_keys/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offerers.models import ApiKey
from pcapi.models import db


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    db.session.query(ApiKey).filter(ApiKey.providerId.is_(None)).delete()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
