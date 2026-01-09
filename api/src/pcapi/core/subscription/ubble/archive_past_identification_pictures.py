import logging
from datetime import datetime

import pcapi.core.subscription.ubble.api as ubble_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble.exceptions import UbbleDownloadedFileEmpty
from pcapi.models import db
from pcapi.utils.requests import ExternalAPIException


DEFAULT_LIMIT = 1000

logger = logging.getLogger()


class UbbleIdentificationPicturesArchiveResult:
    def __init__(self, pictures_archived: int = 0, pictures_not_archived: int = 0):
        self.pictures_archived: int = pictures_archived
        self.pictures_not_archived: int = pictures_not_archived
        self.errors = 0
        self.total = 0

    def add_result(self, result: bool | None = None) -> int:
        if result is True:
            self.pictures_archived += 1
        elif result is False:
            self.pictures_not_archived += 1
        else:
            self.errors += 1
        self.total += 1
        return self.total

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UbbleIdentificationPicturesArchiveResult):
            return False

        return (
            self.pictures_archived == other.pictures_archived
            and self.pictures_not_archived == other.pictures_not_archived
            and self.errors == other.errors
        )


def archive_past_identification_pictures(
    start_date: datetime,
    end_date: datetime,
    picture_storage_status: bool | None = None,
    limit: int = DEFAULT_LIMIT,
) -> UbbleIdentificationPicturesArchiveResult:
    if start_date > end_date:
        raise ValueError('"start date" must be before "end date"')

    result = UbbleIdentificationPicturesArchiveResult()
    offset = 0

    while True:
        fraud_checks = get_fraud_check_to_archive(start_date, end_date, picture_storage_status, limit, offset)

        if not fraud_checks:
            break

        for fraud_check in fraud_checks:
            try:
                ubble_api.archive_id_pictures_with_recovery(fraud_check)
                result.add_result(True)
            except (UbbleDownloadedFileEmpty, ExternalAPIException):
                result.add_result(False)
            except Exception:
                # Catch all exception. Watch logs to find errors during archive
                logger.exception("Error in archive_past_identification_pictures")
                result.add_result()

        # Offset and limit are used to window query result inside loop.
        # For the first request we use offset 0. Offset is updated at each iteration.
        offset += limit

    return result


def get_fraud_check_to_archive(
    start_date: datetime,
    end_date: datetime,
    picture_storage_status: bool | None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[subscription_models.BeneficiaryFraudCheck]:
    query = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.OK,
            subscription_models.BeneficiaryFraudCheck.dateCreated.between(start_date, end_date),
            subscription_models.BeneficiaryFraudCheck.idPicturesStored.is_(picture_storage_status),
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.UBBLE,
            subscription_models.BeneficiaryFraudCheck.thirdPartyId.not_like(
                f"{subscription_api.DEPRECATED_UBBLE_PREFIX}%"
            ),
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.dateCreated.asc())
        .limit(limit)
        .offset(offset)
    )
    return query.all()
