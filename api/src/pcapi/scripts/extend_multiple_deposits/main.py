"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42835-extend-95-deposits \
  -f NAMESPACE=extend_multiple_deposits \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import datetime
import logging
import os

from dateutil.relativedelta import relativedelta

import pcapi.core.offers.api  # circular imports or smth  # noqa: F401
from pcapi.core.external.attributes import api as attributes_api
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main(user_ids: list[int]) -> list[users_models.User]:
    users = db.session.query(users_models.User).filter(users_models.User.id.in_(user_ids)).all()
    logger.info("%s deposits to extend", len(users))
    new_date = datetime.date.today() + relativedelta(months=3)
    for user in users:
        # Copy of users_api.extend_deposit_validity, edited for history comment
        deposit = user.deposit

        # should be ensured by caller, but helps mypy:
        assert deposit is not None
        assert deposit.expirationDate is not None

        # Expire at the end of the day, local time for the beneficiary
        new_expiration_datetime = date_utils.local_datetime_to_default_timezone(
            datetime.datetime.combine(new_date, datetime.time.max),
            date_utils.get_department_timezone(user.departementCode),
        ).replace(tzinfo=None)

        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            user=user,
            modified_info={"deposit.expirationDate": {"old_info": deposit.expirationDate.date(), "new_info": new_date}},
            comment="PC-42835 : Crédit étendu de 3 mois après annulation du festival",
        )
        deposit.expirationDate = new_expiration_datetime
        db.session.add(deposit)
        db.session.flush()

    return users


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{namespace_dir}/users.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
        users = main([int(row["id"]) for row in rows])

    if args.apply:
        logger.info("Finished")
        db.session.commit()
        for user in users:
            attributes_api.update_external_user(user)
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
