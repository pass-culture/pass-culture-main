from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user():
    query = User.query.filter((User.validationToken == None) & (User.resetPasswordToken == None))
    query = query.join(UserOfferer)
    user = query.first()

    return {"user": get_pro_helper(user)}


def get_pro_validated_with_reset_password_token_user():
    query = User.query.filter((User.validationToken == None) & (User.resetPasswordToken != None))
    query = query.join(UserOfferer)
    user = query.first()

    return {"user": get_pro_helper(user)}
