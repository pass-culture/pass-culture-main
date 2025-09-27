"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37998-script-for-cnav/api/src/pcapi/scripts/beneficiary_information/main.py

"""

import argparse
import csv
import logging
import os
from typing import Sequence

from sqlalchemy import select
from sqlalchemy import text

from pcapi.app import app
from pcapi.core.fraud.common.models import IdentityCheckContent
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import DMSContent
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import UbbleContent
from pcapi.models import db


logger = logging.getLogger(__name__)

MIN_FRAUD_CHECK_ID = 26600000  # created in 2025-09-11 in production database
MAX_NUMBER_OF_BENEFICIARIES = 100

UBBLE_CSV_FILE_NAME = "PC-37998-beneficiary-information-ubble.csv"
DMS_CSV_FILE_NAME = "PC-37998-beneficiary-information-dms.csv"
CSV_HEADERS = ["first_name", "last_name", "birth_date", "birth_place", "gender"]


def export_ubble_beneficiary_information(min_fraud_check_id: int = MIN_FRAUD_CHECK_ID) -> None:
    ok_ubble_fraud_checks = _get_ok_fraud_check(min_fraud_check_id, FraudCheckType.UBBLE)
    csv_rows = [_format_fraud_check_to_csv_row(fraud_check) for fraud_check in ok_ubble_fraud_checks]

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/{UBBLE_CSV_FILE_NAME}", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(CSV_HEADERS)
        writer.writerows(csv_rows)


def export_dms_beneficiary_information(min_fraud_check_id: int = MIN_FRAUD_CHECK_ID) -> None:
    ok_dms_fraud_checks = _get_ok_fraud_check(min_fraud_check_id, FraudCheckType.DMS)
    csv_rows = [_format_fraud_check_to_csv_row(fraud_check) for fraud_check in ok_dms_fraud_checks]

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/{DMS_CSV_FILE_NAME}", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(CSV_HEADERS)
        writer.writerows(csv_rows)


def _get_ok_fraud_check(min_fraud_check_id: int, id_provider: FraudCheckType) -> Sequence[BeneficiaryFraudCheck]:
    ok_fraud_check_query = (
        select(BeneficiaryFraudCheck)
        .filter(
            BeneficiaryFraudCheck.id > min_fraud_check_id,
            BeneficiaryFraudCheck.type == id_provider,
            BeneficiaryFraudCheck.status == FraudCheckStatus.OK,
            BeneficiaryFraudCheck.resultContent["birth_place"].is_not(None),
        )
        .limit(MAX_NUMBER_OF_BENEFICIARIES)
    )
    return db.session.scalars(ok_fraud_check_query).all()


def _format_fraud_check_to_csv_row(fraud_check: BeneficiaryFraudCheck) -> tuple[str, str, str, str, str]:
    id_check_content = fraud_check.source_data()
    assert isinstance(id_check_content, IdentityCheckContent)

    first_name = id_check_content.first_name
    last_name = id_check_content.last_name
    birth_date = id_check_content.birth_date
    birth_place = id_check_content.birth_place

    if isinstance(id_check_content, UbbleContent):
        gender = id_check_content.gender
    elif isinstance(id_check_content, DMSContent):
        gender = id_check_content.civility
    else:
        raise ValueError(f"Unhandled {fraud_check = } with {fraud_check.type =}")

    assert first_name is not None, f"{fraud_check = } should not have a None first_name"
    assert last_name is not None, f"{fraud_check = } should not have a None last_name"
    assert birth_date is not None, f"{fraud_check = } should not have a None birth_date"
    assert birth_place is not None, f"{fraud_check = } should not have a None birth_place"
    assert gender is not None, f"{fraud_check = } should not have a None gender"

    return (first_name, last_name, birth_date.isoformat(), birth_place, gender.name)


if __name__ == "__main__":
    app.app_context().push()

    db.session.execute(text("set session statement_timeout = '300s'"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--min-fraud-check-id", type=int, default=MIN_FRAUD_CHECK_ID)
    args = parser.parse_args()

    export_ubble_beneficiary_information(min_fraud_check_id=args.min_fraud_check_id)
    # export_dms_beneficiary_information(min_fraud_check_id=args.min_fraud_check_id)
