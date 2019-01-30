from typing import List

from sqlalchemy import func

from models import Offer, User, UserOfferer, Offerer, RightsType, Venue
from models.db import db
from models.user import WalletBalance


def find_user_by_email(email: str) -> User:
    return User.query \
        .filter(func.lower(User.email) == email.strip().lower()) \
        .first()


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
                    (Offerer.validationToken != None)  & \
                    (UserOfferer.validationToken != None)
                )
    return query

def filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer(query):
    query = query.join(UserOfferer) \
                 .join(Offerer) \
                 .filter(
                    (Offerer.validationToken != None)  & \
                    (UserOfferer.validationToken == None)
                )
    return query

def filter_users_with_at_least_one_offer(query):
    query = query.join(UserOfferer) \
                 .join(Offerer) \
                 .join(Venue) \
                 .filter(Venue.offers.any())
    return query

def filter_users_with_at_least_one_activated_offer(query):
    query = query.join(UserOfferer) \
                 .join(Offerer) \
                 .join(Venue) \
                 .filter(Venue.offers.any(Offer.isActive == True))
    return query

def filter_webapp_users(query):
    query = query.filter(
        (~User.UserOfferers.any()) &\
        (User.isAdmin == False)
    )
    return query

def filter_users_with_at_least_one_offer(query):
    query = query.join(UserOfferer) \
                 .join(Offerer) \
                 .join(Venue) \
                 .filter(Venue.offers.any())
    return query
