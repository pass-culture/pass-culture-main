from pcapi.core import token as token_utils
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users import constants
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user() -> dict:
    user_offerer = offerers_factories.UserOffererFactory(user__validationToken=None)
    return {"user": get_pro_helper(user_offerer.user)}


def get_pro_validated_with_reset_password_token_user() -> dict:
    user_offerer = offerers_factories.UserOffererFactory(user__validationToken=None)
    token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD,
        constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
        user_offerer.user.id,
    )
    return {"user": get_pro_helper(user_offerer.user)}
