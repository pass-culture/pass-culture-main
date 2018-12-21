from typing import List

from sqlalchemy import func

from models import User, UserOfferer, Offerer, RightsType
from models.db import db
from models.user import WalletBalances


def find_user_by_email(email):
    return User.query.filter_by(email=email).first()


def find_user_by_reset_password_token(token):
    return User.query.filter_by(resetPasswordToken=token).first()


def find_all_emails_of_user_offerers_admins(offerer_id):
    filter_validated_user_offerers_with_admin_rights = (UserOfferer.rights == RightsType.admin) & (
            UserOfferer.validationToken == None)
    return [result.email for result in
            User.query.join(UserOfferer).filter(filter_validated_user_offerers_with_admin_rights).join(
                Offerer).filter_by(
                id=offerer_id).all()]


def get_all_users_wallet_balances() -> List[WalletBalances]:
    wallet_balances = db.session.query(User.id,
                                       func.get_wallet_balance(User.id, False),
                                       func.get_wallet_balance(User.id, True)
                                       ) \
        .filter(User.deposits != None) \
        .order_by(User.id) \
        .all()

    instantiate_wallet_balances = lambda u: WalletBalances(u[0], u[1], u[2])
    return list(map(instantiate_wallet_balances, wallet_balances))
