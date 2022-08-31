import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user():  # type: ignore [no-untyped-def]
    user_offerer = offerers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    return {"user": get_pro_helper(user_offerer.user)}


def get_pro_validated_with_reset_password_token_user():  # type: ignore [no-untyped-def]
    user_offerer = offerers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    users_factories.PasswordResetTokenFactory(user=user_offerer.user)
    return {"user": get_pro_helper(user_offerer.user)}
