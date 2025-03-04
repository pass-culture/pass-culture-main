import argparse
import logging
import time

from sqlalchemy.dialects import postgresql

from pcapi.app import app
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.subscription import api as subscription_api
import pcapi.core.subscription.ubble.api as ubble_api
from pcapi.core.subscription.ubble.archive_past_identification_pictures import UbbleIdentificationPicturesArchiveResult
from pcapi.core.subscription.ubble.exceptions import UbbleDownloadedFileEmpty
from pcapi.utils.requests import ExternalAPIException


logger = logging.getLogger(__name__)

app.app_context().push()


def archive_corrupted_identification_pictures(
    start_id: int, end_id: int, batch_size: int, dry_run: bool = True
) -> UbbleIdentificationPicturesArchiveResult:
    # Function body adapted from `archive_past_identification_pictures`
    result = UbbleIdentificationPicturesArchiveResult()
    current_id = start_id

    while current_id < end_id:
        query = BeneficiaryFraudCheck.query.filter(
            BeneficiaryFraudCheck.id.between(current_id, current_id + batch_size),
            BeneficiaryFraudCheck.status == FraudCheckStatus.OK,
            BeneficiaryFraudCheck.idPicturesStored.is_(True),
            BeneficiaryFraudCheck.type == FraudCheckType.UBBLE,
            BeneficiaryFraudCheck.thirdPartyId.not_like(f"{subscription_api.DEPRECATED_UBBLE_PREFIX}%"),
        ).order_by(BeneficiaryFraudCheck.id.asc())

        before = time.time()
        fraud_checks = query.all()
        after = time.time()

        logger.info(f"Query executed in {after - before:.2f}s")

        for fraud_check in fraud_checks:
            try:
                if not dry_run:
                    ubble_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

                result.add_result(True)
            except (UbbleDownloadedFileEmpty, ExternalAPIException):
                result.add_result(False)
            except Exception:  # pylint: disable=broad-except
                logger.exception("Error in archive_past_identification_pictures")
                result.add_result()

        current_id += batch_size

    return result


if __name__ == "__main__":

    """
    Potentially corruped id pictures are those that were archived between
    the deployment of the upgrade of boto3 to 1.36, which is not supported by our
    cold storage, and the deployment of the downgrade back to 1.35.
    This period is from 2025-02-01 to 2025-02-25.
    `BeneficiaryFraudCheck` has no index on `dateCreated` then the retrieval
    is too slow.
    We'll use precomputed `id` range instead:

    +----------+---------+-------------------------+-----------------+------------+
    | id       | userId  | dateCreated             | type            | status     |
    |----------+---------+-------------------------+-----------------+------------|
    ...
    | 24789246 | 7642952 | 2025-01-31 23:59:59.738 | UBBLE           | OK         |
    | 24789247 | 6170172 | 2025-02-01 00:00:45.683 | UBBLE           | OK         |
    ...
    ...
    | 25119331 | 3825663 | 2025-02-25 23:57:27.459 | UBBLE           | OK         |
    | 25119353 | 2788153 | 2025-02-26 00:00:23.508 | UBBLE           | OK         |
    ...
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--start-id", default=24789246, type=int)  # value for prod env
    parser.add_argument("--end-id", default=25119353, type=int)  # value for prod env
    parser.add_argument("--batch-size", default=1_000, type=int)
    args = parser.parse_args()

    result = archive_corrupted_identification_pictures(
        start_id=args.start_id, end_id=args.end_id, batch_size=args.batch_size
    )
    logger.info("Done :")
    logger.info(f"Total records : ....................... {result.total}")
    logger.info(f"archive successful : .................. {result.pictures_archived}")
    logger.info(f"not archived (see logs for details) : . {result.pictures_not_archived}")
    logger.info(f"errors (see logs for details) : ....... {result.errors}")
