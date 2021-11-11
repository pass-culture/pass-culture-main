from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    return {"user": get_pro_helper(user_offerer.user)}


def get_pro_validated_with_reset_password_token_user():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    users_factories.ResetPasswordToken(user=user_offerer.user)
    return {"user": get_pro_helper(user_offerer.user)}
