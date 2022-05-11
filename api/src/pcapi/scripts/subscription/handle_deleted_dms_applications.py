import datetime
import typing

from sqlalchemy import Integer
from typing_extensions import TypeGuard

from pcapi.core.fraud import models as fraud_models


def is_dms_content(obj: typing.Any) -> TypeGuard[fraud_models.DMSContent]:
    return isinstance(obj, fraud_models.DMSContent)


def get_latest_deleted_application_datetime(procedure_id: int) -> typing.Optional[datetime.datetime]:
    fraud_check: typing.Optional[fraud_models.BeneficiaryFraudCheck] = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.CANCELED,
            fraud_models.BeneficiaryFraudCheck.resultContent.isnot(None),
            fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(Integer) == procedure_id,
            fraud_models.BeneficiaryFraudCheck.resultContent.has_key("deletion_datetime"),  # type: ignore [attr-defined]
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.resultContent["deletion_datetime"].desc())
        .first()
    )
    if fraud_check:
        content = fraud_check.source_data()
        if is_dms_content(content):
            return content.deletion_datetime

        raise ValueError(f"fraud_check.source_data() is not a DMSContent. Fraud check: {fraud_check.id}")
    return None

