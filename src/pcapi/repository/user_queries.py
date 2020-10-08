from datetime import MINYEAR, datetime
from typing import List

from sqlalchemy import Column, func
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import Function

from pcapi.models import BeneficiaryImport, BeneficiaryImportStatus, BookingSQLEntity, \
    EventType, ImportStatus, OfferSQLEntity, Offerer, RightsType, StockSQLEntity, \
    ThingType, UserSQLEntity, UserOfferer, BeneficiaryImportSources
from pcapi.models.db import db
from pcapi.models.user_sql_entity import WalletBalance


def count_all_activated_users() -> int:
    return UserSQLEntity.query \
        .filter_by(canBookFreeOffers=True) \
        .count()


def count_all_activated_users_by_departement(department_code: str) -> int:
    return UserSQLEntity.query \
        .filter_by(canBookFreeOffers=True) \
        .filter_by(departementCode=department_code) \
        .count()


def count_users_by_email(email: str) -> int:
    return UserSQLEntity.query \
        .filter_by(email=email) \
        .count()


def _query_user_having_booked() -> Query:
    return UserSQLEntity.query.join(BookingSQLEntity) \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .filter(OfferSQLEntity.type != str(ThingType.ACTIVATION)) \
        .filter(OfferSQLEntity.type != str(EventType.ACTIVATION)) \
        .distinct(UserSQLEntity.id)


def count_users_having_booked() -> int:
    return _query_user_having_booked().count()


def count_users_having_booked_by_departement_code(departement_code: str) -> int:
    return _query_user_having_booked() \
        .filter(UserSQLEntity.departementCode == departement_code) \
        .count()


def find_user_by_email(email: str) -> UserSQLEntity:
    return UserSQLEntity.query \
        .filter(func.lower(UserSQLEntity.email) == email.strip().lower()) \
        .first()


def find_by_civility(first_name: str, last_name: str, date_of_birth: datetime) -> List[UserSQLEntity]:
    civility_predicate = (_matching(UserSQLEntity.firstName, first_name)) & (_matching(UserSQLEntity.lastName, last_name)) & (
        UserSQLEntity.dateOfBirth == date_of_birth)

    return UserSQLEntity.query \
        .filter(civility_predicate) \
        .all()


def find_by_validation_token(token: str) -> UserSQLEntity:
    return UserSQLEntity.query \
        .filter_by(validationToken=token) \
        .first()


def find_user_by_reset_password_token(token: str) -> UserSQLEntity:
    return UserSQLEntity.query \
        .filter_by(resetPasswordToken=token) \
        .first()


def find_all_emails_of_user_offerers_admins(offerer_id: int) -> List[str]:
    filter_validated_user_offerers_with_admin_rights = (UserOfferer.rights == RightsType.admin) & (
        UserOfferer.validationToken == None)
    admins = UserSQLEntity.query \
        .join(UserOfferer) \
        .filter(filter_validated_user_offerers_with_admin_rights) \
        .join(Offerer) \
        .filter_by(id=offerer_id) \
        .all()

    return [result.email for result in admins]


def get_all_users_wallet_balances() -> List[WalletBalance]:
    wallet_balances = db.session.query(
        UserSQLEntity.id,
        func.get_wallet_balance(UserSQLEntity.id, False),
        func.get_wallet_balance(UserSQLEntity.id, True)
    ) \
        .filter(UserSQLEntity.deposits != None) \
        .order_by(UserSQLEntity.id) \
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
        (~UserSQLEntity.UserOfferers.any()) & \
        (UserSQLEntity.isAdmin == False)
    )


def find_most_recent_beneficiary_creation_date_for_source(source: BeneficiaryImportSources, source_id: int) -> datetime:
    most_recent_creation = BeneficiaryImportStatus.query \
        .join(BeneficiaryImport) \
        .filter(BeneficiaryImport.source == source.value) \
        .filter(BeneficiaryImport.sourceId == source_id) \
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


def find_user_by_id(user_id: int) -> UserSQLEntity:
    return UserSQLEntity.query.get(user_id)
