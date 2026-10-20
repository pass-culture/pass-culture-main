"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-44078-recover-qf \
  -f NAMESPACE=recover_qf_bonuses \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import any_
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch.trigger_events import track_has_received_bonus
from pcapi.core.finance.deposit_api import recredit_bonus_credit
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import Recredit
from pcapi.core.mails.transactional import send_bonus_granted_email
from pcapi.core.subscription.bonus.api import does_names_match
from pcapi.core.subscription.bonus.constants import QUOTIENT_FAMILIAL_THRESHOLD
from pcapi.core.subscription.bonus.fraud_check_api import count_manual_attempts
from pcapi.core.subscription.bonus.fraud_check_api import delete_bonus_fraud_checks
from pcapi.core.subscription.bonus.schemas import BonusCreditHouseholder
from pcapi.core.subscription.bonus.schemas import BonusCreditPerson
from pcapi.core.subscription.bonus.schemas import QuotientFamilialBonusCreditContent
from pcapi.core.subscription.bonus.schemas import QuotientFamilialContent
from pcapi.core.subscription.bonus.statistics_api import record_bonus_attempt
from pcapi.core.subscription.models import BeneficiaryFraudCheck
from pcapi.core.subscription.models import FraudCheckStatus
from pcapi.core.subscription.models import FraudCheckType
from pcapi.core.subscription.models import FraudReasonCode
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

PAGE_SIZE = 500


def recover_qf_bonus_checks(
    from_fraud_check_id: int, apply: bool, page_size: int = PAGE_SIZE, max_page: int | None = None
) -> None:
    ko_qf_stmt = (
        select(BeneficiaryFraudCheck)
        .where(
            BeneficiaryFraudCheck.type == FraudCheckType.QF_BONUS_CREDIT,
            BeneficiaryFraudCheck.status == FraudCheckStatus.KO,
            any_(BeneficiaryFraudCheck.reasonCodes) == FraudReasonCode.NOT_IN_TAX_HOUSEHOLD,
        )
        .options(joinedload(BeneficiaryFraudCheck.user).selectinload(User.deposits).selectinload(Deposit.recredits))
    )

    current_page = 0
    total_reset = 0
    while True:
        current_page += 1
        with atomic():
            keyset_paginated_stmt = (
                ko_qf_stmt.where(BeneficiaryFraudCheck.id > from_fraud_check_id)
                .order_by(BeneficiaryFraudCheck.id)
                .limit(page_size)
            )
            fraud_checks = db.session.scalars(keyset_paginated_stmt).unique().all()

            if not fraud_checks:
                break

            from_fraud_check_id = fraud_checks[-1].id
            for fraud_check in fraud_checks:
                has_restarted_fraud_check = maybe_restart_fraud_check(fraud_check, apply)

                if has_restarted_fraud_check:
                    total_reset += 1

            logger.info("Recovered up to fraud check %s", from_fraud_check_id)

            if apply:
                logger.info("Commiting")
            else:
                logger.info("Rolling back")
                mark_transaction_as_invalid()

        if max_page is not None and current_page >= max_page:
            logger.info("Exiting after reaching page %s", current_page)
            break

    logger.info("%s QF bonus fraud checks were reset to STARTED", total_reset)


def maybe_restart_fraud_check(fraud_check: BeneficiaryFraudCheck, apply_side_effects: bool) -> bool:
    source_data = fraud_check.source_data()
    if not isinstance(source_data, QuotientFamilialBonusCreditContent):
        raise TypeError(f"QuotientFamilialBonusCreditContent was expected while {type(source_data)} was given")

    user = fraud_check.user
    if not _is_user_part_of_tax_household(user, source_data):
        return False

    if _has_eligible_quotient_familial(source_data.quotient_familial):
        given_recredit, attempts_count = _grant_bonus(fraud_check)

        if given_recredit and apply_side_effects:
            granted_after_attempts = attempts_count
            track_has_received_bonus(user.id)
            send_bonus_granted_email(user)

            update_external_user(user)

            record_bonus_attempt(FraudCheckType.QF_BONUS_CREDIT, fraud_check.reasonCodes or [], granted_after_attempts)

    fraud_check.status = FraudCheckStatus.STARTED
    fraud_check.reasonCodes = None

    logger.info("Reset fraud check %s to STARTED", fraud_check.id)
    return True


def _is_user_part_of_tax_household(user: User, source_data: QuotientFamilialBonusCreditContent) -> bool:
    for child in source_data.children or []:
        if _does_user_match_person(user, child):
            return True

    for householder in source_data.householders or []:
        if _does_user_match_person(user, householder):
            return True

    return False


def _does_user_match_person(user: User, person: BonusCreditPerson | BonusCreditHouseholder) -> bool:
    has_first_name_match = does_names_match(user.firstName, " ".join(person.first_names))
    has_last_name_match = does_names_match(user.lastName, person.last_name) or does_names_match(
        user.lastName, person.common_name
    )
    has_birth_day_match = user.validatedBirthDate == person.birth_date
    has_gender_match = user.gender == person.gender

    return has_first_name_match and has_last_name_match and has_birth_day_match and has_gender_match


def _has_eligible_quotient_familial(quotient_familial: QuotientFamilialContent | None = None) -> bool:
    if quotient_familial is None:
        return False

    return quotient_familial.value <= QUOTIENT_FAMILIAL_THRESHOLD


def _grant_bonus(
    fraud_check: BeneficiaryFraudCheck,
) -> tuple[Recredit | None, int | None]:
    user = fraud_check.user

    if not fraud_check.resultContent:
        fraud_check.resultContent = {}

    given_recredit = recredit_bonus_credit(user)
    attempts_count: int | None = None

    if given_recredit:
        attempts_count = count_manual_attempts(user)
        delete_bonus_fraud_checks(user)

    return given_recredit, attempts_count


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--from-fraud-check-id", type=int, default=31000000)
    parser.add_argument("--page-size", type=int)
    parser.add_argument("--max-page", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    recover_qf_bonus_checks(args.from_fraud_check_id, args.apply, args.page_size or PAGE_SIZE, args.max_page)

    logger.info("Finished")
