from datetime import MINYEAR
from datetime import datetime
from datetime import timedelta
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import Function

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus
from pcapi.models import UserOfferer
from pcapi.models.db import db
from pcapi.models.wallet_balance import WalletBalance


def count_users_by_email(email: str) -> int:
    # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
    # all emails have been sanitized in the database.
    return User.query.filter(func.lower(User.email) == sanitize_email(email)).count()


def find_user_by_email(email: str) -> User:
    # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
    # all emails have been sanitized in the database.
    return User.query.filter(func.lower(User.email) == sanitize_email(email)).one_or_none()


def find_beneficiary_users_by_email_provider(email_provider: str) -> list[User]:
    formatted_email_provider = f"%@{email_provider}"
    return (
        User.query.filter_by(isBeneficiary=True, isActive=True)
        .filter(func.lower(User.email).like(func.lower(formatted_email_provider)))
        .all()
    )


def find_pro_users_by_email_provider(email_provider: str) -> list[User]:
    formatted_email_provider = f"%@{email_provider}"
    return (
        User.query.filter_by(isBeneficiary=False, isActive=True)
        .join(UserOfferer)
        .filter(User.offerers.any())
        .filter(func.lower(User.email).like(func.lower(formatted_email_provider)))
        .all()
    )


def beneficiary_by_civility_query(
    first_name: str,
    last_name: str,
    date_of_birth: datetime = None,
    interval: timedelta = None,
    exclude_email: Optional[str] = None,
) -> Query:
    civility_predicate = (
        (matching(User.firstName, first_name)) & (matching(User.lastName, last_name)) & (User.isBeneficiary == True)
    )
    if interval:
        civility_predicate = civility_predicate & (User.dateCreated >= (datetime.now() - interval))
    if date_of_birth:
        civility_predicate = civility_predicate & (User.dateOfBirth == date_of_birth)
    if exclude_email:
        civility_predicate = civility_predicate & (User.email != exclude_email)

    return User.query.filter(civility_predicate)


def find_beneficiary_by_civility(first_name: str, last_name: str, date_of_birth: datetime) -> list[User]:
    return beneficiary_by_civility_query(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth).all()


def find_by_validation_token(token: str) -> User:
    return User.query.filter_by(validationToken=token).one_or_none()


def get_all_users_wallet_balances() -> list[WalletBalance]:
    """Return wallet balances.

    WARNING: it ignores the expiration date of the deposits.
    """
    wallet_balances = (
        db.session.query(
            User.id,
            func.get_wallet_balance(User.id, False),
            func.get_wallet_balance(User.id, True),
        )
        .filter(User.deposits != None)
        .order_by(User.id)
        .all()
    )

    return [
        WalletBalance(user_id, current_balance, real_balance)
        for user_id, current_balance, real_balance in wallet_balances
    ]


def filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query: Query) -> Query:
    return (
        query.join(UserOfferer)
        .join(Offerer)
        .filter((Offerer.validationToken.is_(None)) & (UserOfferer.validationToken.is_(None)))
    )


def keep_only_webapp_users(query: Query) -> Query:
    return query.filter((~User.UserOfferers.any()) & (User.isAdmin.is_(False)))


def find_most_recent_beneficiary_creation_date_for_source(source: BeneficiaryImportSources, source_id: int) -> datetime:
    most_recent_creation = (
        BeneficiaryImportStatus.query.join(BeneficiaryImport)
        .filter(BeneficiaryImport.source == source.value)
        .filter(BeneficiaryImport.sourceId == source_id)
        .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        .order_by(BeneficiaryImportStatus.date.desc())
        .first()
    )

    if not most_recent_creation:
        return datetime(MINYEAR, 1, 1)

    return most_recent_creation.date


def matching(column: Column, search_value: str) -> BinaryExpression:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = func.replace(value, "-", "")
    sanitized = func.replace(sanitized, " ", "")
    sanitized = func.unaccent(sanitized)
    sanitized = func.lower(sanitized)
    return sanitized
