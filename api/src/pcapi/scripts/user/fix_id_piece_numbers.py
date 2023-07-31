from functools import wraps
import logging
import re
import time

from pcapi.core.fraud.api import format_id_piece_number
import pcapi.core.fraud.models as fraud_models
from pcapi.core.users.models import User
from pcapi.models import db


logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.DEBUG)


def timed(func):  # type: ignore[no-untyped-def]
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("%s ran in %ss", func.__name__, round(end - start, 2))
        return result

    return wrapper


def get_relevant_identity_fraud_check(user: User) -> fraud_models.BeneficiaryFraudCheck | None:
    fraud_checks = user.beneficiaryFraudChecks
    fraud_checks.sort(key=lambda fraud_check: fraud_check.dateCreated, reverse=True)
    identity_fraud_checks = [
        fraud_check for fraud_check in fraud_checks if fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES
    ]
    identity_fraud_checks.sort(key=lambda fraud_check: fraud_check.dateCreated, reverse=True)

    if not identity_fraud_checks:
        return None

    for status in (  # order matters here
        fraud_models.FraudCheckStatus.OK,
        fraud_models.FraudCheckStatus.PENDING,
        fraud_models.FraudCheckStatus.STARTED,
        fraud_models.FraudCheckStatus.SUSPICIOUS,
        fraud_models.FraudCheckStatus.KO,
    ):
        relevant_fraud_check = next(
            (fraud_check for fraud_check in identity_fraud_checks if fraud_check.status == status), None
        )
        if relevant_fraud_check:
            return relevant_fraud_check

    return None


@timed
def update_badly_formatted_id_piece_number(dry_run: bool = True) -> None:
    query = User.query.filter(User.idPieceNumber.regexp_match(r"[^A-Z0-9]"))
    total = query.count()
    print(f"Found {total} users to update")

    duplicates = []
    updated_users = []
    users = query.all()
    users.sort(key=lambda u: u.id)
    for user in users:
        id_piece_number = user.idPieceNumber.lower()
        if (
            id_piece_number.startswith("http")
            or id_piece_number.startswith("active_storage/")
            or id_piece_number.endswith(".jpeg")
            or id_piece_number.endswith(".jpg")
            or id_piece_number.endswith(".pdf")
        ):
            continue

        identity_fraud_check = get_relevant_identity_fraud_check(user)
        if identity_fraud_check and identity_fraud_check.type == fraud_models.FraudCheckType.DMS:
            if not identity_fraud_check.resultContent:
                continue
            content = fraud_models.DMSContent(**identity_fraud_check.resultContent)
            if content.procedure_number != 47480:
                # print(
                #     f"{user.id}: DMS ({identity_fraud_check.id}) - {id_piece_number = } {content.procedure_number = }"
                # )
                continue

        new_id_piece_number = format_id_piece_number(user.idPieceNumber)
        duplicated_user = User.query.filter(User.id != user.id, User.idPieceNumber == new_id_piece_number).one_or_none()
        if not duplicated_user:
            print(f"{user.id}: old {user.idPieceNumber} - new {new_id_piece_number}")
            user.idPieceNumber = new_id_piece_number
            updated_users.append(user)
        else:
            print(
                f"duplicated user found: {user.id} - {user.idPieceNumber} and {duplicated_user.id} - {duplicated_user.idPieceNumber}"
            )
            duplicates.append(duplicated_user.id)

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    print("Done")
    print(f"Updated {len(updated_users)} users")
    print(f"Found {len(duplicates)} duplicates")
    print([user.id for user in updated_users])
    print(duplicates)

    if dry_run:
        return

    for user in updated_users:
        assert re.match(r"^[A-ZÀ-Ü0-9]+$", user.idPieceNumber), f"Error: {user.id} - {user.idPieceNumber}"
