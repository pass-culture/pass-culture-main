"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35614/script-fix-non-beneficiary-roles/api/src/pcapi/scripts/fix_non_beneficiary_roles/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(user_ids: list[int]) -> None:
    users = db.session.query(users_models.User).filter(users_models.User.id.in_(user_ids)).all()
    for user in users:
        user.roles = []
        db.session.add(user)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--user-id", nargs="+", type=int)
    args = parser.parse_args()

    main(user_ids=args.user_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
