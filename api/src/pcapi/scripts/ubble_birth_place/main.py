"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36914-fetch-ubble-v2-birth-place/api/src/pcapi/scripts/ubble_birth_place/main.py

"""

import argparse
import logging
from time import sleep
from time import time
from typing import Generator

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.models import db
from pcapi.utils.repository import transaction
from pcapi.utils.requests import ExternalAPIException


logger = logging.getLogger(__name__)

MIN_UBBLE_V2_OK_FRAUD_CHECK_ID = 24_596_998

MAX_UBBLE_CALL_PER_SECOND = 2
TRANSACTION_EXECUTION_TIME_IN_SECONDS = 30
BATCH_SIZE = min(TRANSACTION_EXECUTION_TIME_IN_SECONDS * MAX_UBBLE_CALL_PER_SECOND, 50_000)


def import_ubble_v2_birth_place(
    not_dry: bool, from_id: int = 1, to_id: int | None = None, batch_size: int = BATCH_SIZE
) -> None:
    for ubble_fraud_checks in _get_ok_ubble_fraud_checks_pages(from_id, to_id, batch_size):
        with transaction():
            for fraud_check in ubble_fraud_checks:
                try:
                    _resync_ubble_fraud_check(fraud_check)
                except ExternalAPIException:
                    logger.error(
                        "failed to resync fraud check %s, ubble identification %s, user %s",
                        fraud_check.id,
                        fraud_check.thirdPartyId,
                        fraud_check.user.id,
                    )
                    continue

                _update_user_birth_place(fraud_check)

            if not not_dry:
                logger.info("Finished dry run page, rollback")
                db.session.rollback()

        logger.info("Updated Ubble fraud checks up to id %s")


def _get_ok_ubble_fraud_checks_pages(
    from_id: int, to_id: int | None, batch_size: int
) -> Generator[list[BeneficiaryFraudCheck], None, None]:
    ubble_fraud_check_query = (
        select(BeneficiaryFraudCheck)
        .where(
            BeneficiaryFraudCheck.status == FraudCheckStatus.OK,
            BeneficiaryFraudCheck.type == FraudCheckType.UBBLE,
            BeneficiaryFraudCheck.thirdPartyId.like("idv_%"),
        )
        .options(joinedload(BeneficiaryFraudCheck.user))
    )
    has_next_page = True
    was_max_id_reached = False
    while has_next_page and not was_max_id_reached:
        start = time()
        keyset_paginated_query = (
            ubble_fraud_check_query.where(BeneficiaryFraudCheck.id >= from_id)
            .order_by(BeneficiaryFraudCheck.id)
            .limit(batch_size)
        )
        ubble_fraud_checks = db.session.scalars(keyset_paginated_query).all()
        end = time()

        last_id = ubble_fraud_checks[-1].id if ubble_fraud_checks else None
        logger.info("Fetched Ubble fraud checks from id %s to %s in %d seconds", from_id, last_id, end - start)

        yield ubble_fraud_checks

        has_next_page = bool(ubble_fraud_checks)
        if has_next_page:
            from_id = ubble_fraud_checks[-1].id + 1
        was_max_id_reached = to_id is not None and from_id > to_id


def _resync_ubble_fraud_check(fraud_check: BeneficiaryFraudCheck) -> None:
    sleep(1 / MAX_UBBLE_CALL_PER_SECOND)

    ubble_content = ubble.get_identity_verification(fraud_check.thirdPartyId)

    if not fraud_check.resultContent:
        fraud_check.resultContent = {}
    fraud_check.resultContent.update(**ubble_content.dict(exclude_none=True))


def _update_user_birth_place(fraud_check: BeneficiaryFraudCheck) -> None:
    user = fraud_check.user
    user.birthPlace = fraud_check.source_data().get_birth_place()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--from-id", type=int)
    parser.add_argument("--to-id", type=int)
    args = parser.parse_args()

    from_id = args.from_id or MIN_UBBLE_V2_OK_FRAUD_CHECK_ID
    import_ubble_v2_birth_place(not_dry=args.not_dry, from_id=from_id, to_id=args.to_id)
