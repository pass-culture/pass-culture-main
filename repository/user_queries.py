from datetime import MINYEAR, datetime
from typing import List

from sqlalchemy import Column, func
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import Function

from models import BeneficiaryImport, BeneficiaryImportStatus, Booking, \
    EventType, ImportStatus, Offer, Offerer, RightsType, Stock, \
    ThingType, User, UserOfferer
from models.db import db
from models.user import WalletBalance


def count_all_activated_users() -> int:
    return User.query \
        .filter_by(canBookFreeOffers=True) \
        .count()


def count_all_activated_users_by_departement(department_code: str) -> int:
    return User.query \
        .filter_by(canBookFreeOffers=True) \
        .filter_by(departementCode=department_code) \
        .count()


def count_users_by_email(email: str) -> int:
    return User.query \
        .filter_by(email=email) \
        .count()


def _query_user_having_booked() -> Query:
    return User.query.join(Booking) \
        .join(Stock) \
        .join(Offer) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .distinct(User.id)


def count_users_having_booked() -> int:
    return _query_user_having_booked().count()


def count_users_having_booked_by_departement_code(departement_code: str) -> int:
    return _query_user_having_booked() \
        .filter(User.departementCode == departement_code) \
        .count()


def find_user_by_email(email: str) -> User:
    return User.query \
        .filter(func.lower(User.email) == email.strip().lower()) \
        .first()


def find_by_civility(first_name: str, last_name: str, birth_date: datetime) -> List[User]:
    civility_predicate = (_matching(User.firstName, first_name)) & (_matching(User.lastName, last_name)) & (
        User.dateOfBirth == birth_date)

    return User.query \
        .filter(civility_predicate) \
        .all()


def find_by_validation_token(token: str) -> User:
    return User.query \
        .filter_by(validationToken=token) \
        .first()


def find_user_by_reset_password_token(token: str) -> User:
    return User.query \
        .filter_by(resetPasswordToken=token) \
        .first()


def find_all_emails_of_user_offerers_admins(offerer_id: int) -> List[str]:
    filter_validated_user_offerers_with_admin_rights = (UserOfferer.rights == RightsType.admin) & (
        UserOfferer.validationToken == None)
    admins = User.query \
        .join(UserOfferer) \
        .filter(filter_validated_user_offerers_with_admin_rights) \
        .join(Offerer) \
        .filter_by(id=offerer_id) \
        .all()

    return [result.email for result in admins]


def get_all_users_wallet_balances() -> List[WalletBalance]:
    wallet_balances = db.session.query(
        User.id,
        func.get_wallet_balance(User.id, False),
        func.get_wallet_balance(User.id, True)
    ) \
        .filter(User.deposits != None) \
        .order_by(User.id) \
        .all()

    instantiate_result_set = lambda u: WalletBalance(u[0], u[1], u[2])
    return list(map(instantiate_result_set, wallet_balances))


def filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query: Query) -> Query:
    return query \
        .join(UserOfferer) \
        .join(Offerer) \
        .filter(
            (Offerer.validationToken == None) & \
            (UserOfferer.validationToken == None)
        )


def filter_users_with_at_least_one_validated_offerer_not_validated_user_offerer(query: Query) -> Query:
    return query \
        .join(UserOfferer) \
        .join(Offerer) \
        .filter(
            (Offerer.validationToken == None) & \
            (UserOfferer.validationToken != None)
        )


def filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer(query: Query) -> Query:
    return query \
        .join(UserOfferer) \
        .join(Offerer) \
        .filter(
            (Offerer.validationToken != None) & \
            (UserOfferer.validationToken == None)
        )


def keep_only_webapp_users(query: Query) -> Query:
    return query.filter(
        (~User.UserOfferers.any()) & \
        (User.isAdmin == False)
    )


def find_most_recent_beneficiary_creation_date_by_procedure_id(demarche_simplifiee_procedure_id: int) -> datetime:
    most_recent_creation = BeneficiaryImportStatus.query \
        .join(BeneficiaryImport) \
        .filter(BeneficiaryImport.demarcheSimplifieeProcedureId == demarche_simplifiee_procedure_id) \
        .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED) \
        .order_by(BeneficiaryImportStatus.date.desc()) \
        .first()

    if not most_recent_creation:
        return datetime(MINYEAR, 1, 1)

    return most_recent_creation.date


def _matching(column: Column, search_value: str) -> BinaryExpression:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = func.replace(value, '-', '')
    sanitized = func.replace(sanitized, ' ', '')
    sanitized = func.unaccent(sanitized)
    sanitized = func.lower(sanitized)
    return sanitized


def find_user_by_id(user_id: int) -> User:
    return User.query.get(user_id)
