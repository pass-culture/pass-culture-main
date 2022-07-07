from datetime import datetime

from pcapi.core.fraud import models
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
import pcapi.core.subscription.ubble.api as ubble_api


DEFAULT_LIMIT = 1000
DEFAULT_ID_PICTURE_STORE_STATUS = None


# FIXME (jsdupuis 2022-03-03): delete this module when the images of past identifications have been archived
class UbbleIdentificationPicturesArchiveResult:
    def __init__(self, pictures_archived: int = 0, pictures_not_archived: int = 0):
        self.pictures_archived: int = pictures_archived
        self.pictures_not_archived: int = pictures_not_archived
        self.errors: int = 0
        self.total: int = 0

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
    limit: int = DEFAULT_LIMIT,
    status: bool | None = DEFAULT_ID_PICTURE_STORE_STATUS,
) -> UbbleIdentificationPicturesArchiveResult:
    if start_date > end_date:
        raise ValueError('"start date" must be before "end date"')

    result = UbbleIdentificationPicturesArchiveResult()
    offset = 0

    while True:
        fraud_checks = get_fraud_check_to_archive(start_date, end_date, status, limit, offset)

        current_count = len(fraud_checks)
        if current_count == 0:
            break

        for fraud_check in fraud_checks:
            try:
                archived_result = ubble_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)  # type: ignore [arg-type]
                result.add_result(archived_result)
            except Exception:  # pylint: disable=broad-except
                # Catch all exception. Watch logs to find errors during archive
                result.add_result()

        # Offset and limit are used to window query result inside loop.
        # For the first request we use offset 0. Offset is updated at each iteration.
        offset += limit

    return result


def get_fraud_check_to_archive(
    start_date: datetime, end_date: datetime, status: bool | None, limit: int = DEFAULT_LIMIT, offset: int = 0
) -> list[BeneficiaryFraudCheck]:
    query = (
        models.BeneficiaryFraudCheck.query.filter(
            BeneficiaryFraudCheck.status == FraudCheckStatus.OK,
            BeneficiaryFraudCheck.dateCreated.between(start_date, end_date),
            BeneficiaryFraudCheck.idPicturesStored.is_(status),
            BeneficiaryFraudCheck.type == FraudCheckType.UBBLE,
        )
        .order_by(BeneficiaryFraudCheck.dateCreated.asc())
        .limit(limit)
        .offset(offset)
    )
    return query.all()
