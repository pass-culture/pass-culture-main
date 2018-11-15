import uuid
from uuid import UUID

from sqlalchemy import func, distinct

from models import User, UserSession, PcObject, UserOfferer, Offerer, RightsType
from models.db import db


def find_user_by_email(email):
    return User.query.filter_by(email=email).first()


def find_user_by_reset_password_token(token):
    return User.query.filter_by(resetPasswordToken=token).first()


def find_all_emails_of_user_offerers_admins(offerer_id):
    filter_validated_user_offerers_with_admin_rights = (UserOfferer.rights == RightsType.admin) & (
                UserOfferer.validationToken == None)
    return [result.email for result in
            User.query.join(UserOfferer).filter(filter_validated_user_offerers_with_admin_rights).join(Offerer).filter_by(
                id=offerer_id).all()]
