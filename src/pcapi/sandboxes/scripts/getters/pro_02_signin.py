from typing import Optional

from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_not_validated_user():
    query = User.query.join(UserOfferer)
    user = query.filter(User.validationToken != None).first()  # pylint: disable=singleton-comparison

    return {"user": get_pro_helper(user)}


def get_existing_pro_validated_user():
    query = User.query.join(UserOfferer)
    user = query.filter(User.validationToken == None).first()  # pylint: disable=singleton-comparison

    return {"user": get_pro_helper(user)}


def get_existing_pro_validated_user_without_offer() -> Optional[dict]:
    users = User.query.filter(User.validationToken == None).all()  # pylint: disable=singleton-comparison

    for user in users:
        if not user.hasOffers:
            return {"user": get_pro_helper(user)}

    return None
