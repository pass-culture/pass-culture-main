"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

Assumed path to the script (copy-paste in github actions): 
https://github.com/pass-culture/pass-culture-main/blob/PC-35311-cancelled-dms-script/api/src/pcapi/scripts/uncancel_ok_dms_checks/main.py
"""

import argparse
from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import db


logger = logging.getLogger(__name__)


def uncancel_ok_dms_checks(not_dry: bool, last_user_id: int = 0) -> None:
    logger.info("starting uncancel_ok_dms_checks")
    while True:
        users = _get_users_with_cancelled_ok_dms_checks(last_user_id)
        if not users:
            break

        for user in users:
            _uncancel_dms_check(user)

        last_user_id = users[-1].id


def _get_users_with_cancelled_ok_dms_checks(last_user_id: int) -> list[User]:
    twenty_one_years_ago = datetime.utcnow() - relativedelta(years=21)
    return (
        User.query.filter(
            User.id > last_user_id,
            User.validatedBirthDate > twenty_one_years_ago,
            User.roles.any(UserRole.UNDERAGE_BENEFICIARY),
            BeneficiaryFraudCheck.query.filter(
                BeneficiaryFraudCheck.userId == User.id,
                BeneficiaryFraudCheck.type == FraudCheckType.DMS,
                BeneficiaryFraudCheck.eligibilityType != EligibilityType.AGE18,
                BeneficiaryFraudCheck.status == FraudCheckStatus.CANCELED,
                BeneficiaryFraudCheck.resultContent["state"].astext == "accepte",
            ).exists(),
        )
        .options(selectinload(User.beneficiaryFraudChecks))
        .order_by(User.id)
        .limit(50)
        .all()
    )


def _uncancel_dms_check(user: User) -> None:
    dms_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == FraudCheckType.DMS
        and fraud_check.eligibilityType != EligibilityType.AGE18
        and fraud_check.status == FraudCheckStatus.CANCELED
        and fraud_check.resultContent["state"] == "accepte"
    ]
    dms_fraud_checks.sort(key=lambda fraud_check: fraud_check.dateCreated, reverse=True)

    if not dms_fraud_checks:
        return

    fraud_check_to_uncancel = dms_fraud_checks[0]
    logger.info("uncancelling fraud check %s for user %s", fraud_check_to_uncancel.id, user.id)

    fraud_check_to_uncancel.status = FraudCheckStatus.OK

    action_log = ActionHistory(
        actionType=ActionType.COMMENT,
        user=user,
        authorUserId=6721024,
        comment=f"(PC-35311) Résurrection de la vérification d'identité DMS {fraud_check_to_uncancel.id}",
    )
    db.session.add(action_log)


if __name__ == "__main__":
    app.app_context().push()
    db.session.execute(text("set session statement_timeout = '500s'"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--last-user-id", type=int, default=0)
    args = parser.parse_args()

    uncancel_ok_dms_checks(not_dry=args.not_dry, last_user_id=args.last_user_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
