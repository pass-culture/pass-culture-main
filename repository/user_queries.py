from datetime import datetime, MINYEAR
from typing import List

from sqlalchemy import func, Column
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import Function

from models import User, UserOfferer, Offerer, RightsType
from models.db import db
from models.user import WalletBalance


def find_user_by_email(email: str) -> User:
    return User.query \
        .filter(func.lower(User.email) == email.strip().lower()) \
        .first()


def find_by_first_and_last_names_and_birth_date_and_email(first_name: str, last_name: str, birth_date: datetime, email: str) -> List[User]:
    return User.query \
        .filter(_matching(User.firstName, first_name)) \
        .filter(_matching(User.lastName, last_name)) \
        .filter(User.dateOfBirth == birth_date) \
        .filter(_matching(User.email, email)) \
        .all()


def find_by_validation_token(token: str) -> User:
    return User.query.filter_by(validationToken=token).first()


def find_user_by_reset_password_token(token: str) -> User:
    return User.query.filter_by(resetPasswordToken=token).first()


def find_all_emails_of_user_offerers_admins(offerer_id: int) -> List[str]:
    filter_validated_user_offerers_with_admin_rights = (UserOfferer.rights == RightsType.admin) & (
            UserOfferer.validationToken == None)
    return [result.email for result in
            User.query.join(UserOfferer).filter(filter_validated_user_offerers_with_admin_rights).join(
                Offerer).filter_by(
                id=offerer_id).all()]


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


def filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query):
    query = query.join(UserOfferer) \
        .join(Offerer) \
        .filter(
        (Offerer.validationToken == None) & \
        (UserOfferer.validationToken == None)
    )
    return query


def filter_users_with_at_least_one_validated_offerer_not_validated_user_offerer(query):
    query = query.join(UserOfferer) \
        .join(Offerer) \
        .filter(
        (Offerer.validationToken == None) & \
        (UserOfferer.validationToken != None)
    )
    return query


def filter_users_with_at_least_one_not_activated_offerer_not_validated_user_offerer(query):
    query = query.join(UserOfferer) \
        .join(Offerer) \
        .filter(
        (Offerer.validationToken != None) & \
        (UserOfferer.validationToken != None)
    )
    return query


def filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer(query):
    query = query.join(UserOfferer) \
        .join(Offerer) \
        .filter(
        (Offerer.validationToken != None) & \
        (UserOfferer.validationToken == None)
    )
    return query


def keep_only_webapp_users(query):
    query = query.filter(
        (~User.UserOfferers.any()) & \
        (User.isAdmin == False)
    )
    return query


def find_most_recent_beneficiary_creation_date():
    most_recent_beneficiary = User.query \
        .filter(User.canBookFreeOffers == True) \
        .filter(User.offerers == None) \
        .filter(User.demarcheSimplifieeApplicationId != None) \
        .order_by(User.dateCreated.desc()) \
        .first()

    if not most_recent_beneficiary:
        return datetime(MINYEAR, 1, 1)

    return most_recent_beneficiary.dateCreated


def _matching(column: Column, search_value: str) -> BinaryExpression:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = func.replace(value, '-', '')
    sanitized = func.replace(sanitized, ' ', '')
    sanitized = func.unaccent(sanitized)
    sanitized = func.lower(sanitized)
    return sanitized
