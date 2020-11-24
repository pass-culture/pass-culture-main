from typing import Optional

from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_not_validated_user():
    query = UserSQLEntity.query.join(UserOfferer)
    query = query.filter(UserSQLEntity.validationToken != None)  # pylint: disable=singleton-comparison
    user = query.first()

    return {"user": get_pro_helper(user)}


def get_existing_pro_validated_user():
    query = UserSQLEntity.query.join(UserOfferer)
    query = query.filter(UserSQLEntity.validationToken == None)  # pylint: disable=singleton-comparison
    user = query.first()

    return {"user": get_pro_helper(user)}


def get_existing_pro_validated_user_without_offer() -> Optional[dict]:
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)  # pylint: disable=singleton-comparison
    users = query.all()

    for user in users:
        if not user.hasOffers:
            return {"user": get_pro_helper(user)}

    return None
