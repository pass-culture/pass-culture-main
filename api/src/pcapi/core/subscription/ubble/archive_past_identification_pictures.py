from datetime import datetime

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
import pcapi.core.subscription.ubble.api as ubble_api
from pcapi.core.subscription.ubble.exceptions import UbbleDownloadedFileEmpty
from pcapi.utils.requests import ExternalAPIException


DEFAULT_LIMIT = 1000
DEFAULT_ID_PICTURE_STORE_STATUS = None


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
    status: bool | None = DEFAULT_ID_PICTURE_STORE_STATUS,
    limit: int = DEFAULT_LIMIT,
) -> UbbleIdentificationPicturesArchiveResult:
    if start_date > end_date:
        raise ValueError('"start date" must be before "end date"')

    result = UbbleIdentificationPicturesArchiveResult()
    offset = 0

    while True:
        fraud_checks = get_fraud_check_to_archive(start_date, end_date, status, limit, offset)

        if not fraud_checks:
            break

        for fraud_check in fraud_checks:
            try:
                ubble_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)
                result.add_result(True)
            except (UbbleDownloadedFileEmpty, ExternalAPIException):
                result.add_result(False)
            except Exception:  # pylint: disable=broad-except
                # Catch all exception. Watch logs to find errors during archive
                result.add_result()

        # Offset and limit are used to window query result inside loop.
        # For the first request we use offset 0. Offset is updated at each iteration.
        offset += limit

    return result


def get_fraud_check_to_archive(
    start_date: datetime, end_date: datetime, status: bool | None, limit: int = DEFAULT_LIMIT, offset: int = 0
) -> list[fraud_models.BeneficiaryFraudCheck]:
    query = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.OK,
            fraud_models.BeneficiaryFraudCheck.dateCreated.between(start_date, end_date),
            fraud_models.BeneficiaryFraudCheck.idPicturesStored.is_(status),
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId.notlike(f"{subscription_api.DEPRECATED_UBBLE_PREFIX}%"),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.dateCreated.asc())
        .limit(limit)
        .offset(offset)
    )
    return query.all()
