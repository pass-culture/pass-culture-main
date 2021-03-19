from datetime import MINYEAR
from datetime import datetime
from typing import List

from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import Function

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.core.users.utils import format_email
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus
from pcapi.models import UserOfferer
from pcapi.models.db import db
from pcapi.models.wallet_balance import WalletBalance


def count_users_by_email(email: str) -> int:
    return User.query.filter_by(email=email).count()


def find_user_by_email(email: str) -> User:
    return User.query.filter(func.lower(User.email) == format_email(email)).first()


def find_beneficiary_users_by_email_provider(email_provider: str) -> List[User]:
    formatted_email_provider = "%{}%".format(email_provider)
    return User.query.filter(User.isBeneficiary.is_(True)).filter(User.email.like(formatted_email_provider)).all()


def find_by_civility(first_name: str, last_name: str, date_of_birth: datetime) -> List[User]:
    civility_predicate = (
        (_matching(User.firstName, first_name))
        & (_matching(User.lastName, last_name))
        & (User.dateOfBirth == date_of_birth)
    )

    return User.query.filter(civility_predicate).all()


def find_by_validation_token(token: str) -> User:
    return User.query.filter_by(validationToken=token).first()


def find_user_by_reset_password_token(token: str) -> User:
    return User.query.filter_by(resetPasswordToken=token).first()


def get_all_users_wallet_balances() -> List[WalletBalance]:
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


def filter_users_with_at_least_one_validated_offerer_not_validated_user_offerer(query: Query) -> Query:
    return (
        query.join(UserOfferer)
        .join(Offerer)
        .filter((Offerer.validationToken.is_(None)) & (not_(UserOfferer.validationToken.is_(None))))
    )


def filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer(query: Query) -> Query:
    return (
        query.join(UserOfferer)
        .join(Offerer)
        .filter((not_(Offerer.validationToken.is_(None))) & (UserOfferer.validationToken.is_(None)))
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


def _matching(column: Column, search_value: str) -> BinaryExpression:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = func.replace(value, "-", "")
    sanitized = func.replace(sanitized, " ", "")
    sanitized = func.unaccent(sanitized)
    sanitized = func.lower(sanitized)
    return sanitized


def find_user_by_id(user_id: int) -> User:
    return User.query.get(user_id)
