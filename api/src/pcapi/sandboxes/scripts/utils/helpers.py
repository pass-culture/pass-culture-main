from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.users import models as users_models
from pcapi.core.users import exceptions as users_exceptions
from pcapi.routes.serialization import as_dict


def get_email(first_name: str, last_name: str, domain: str) -> str:
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


# helper to serialize pro users
def get_pro_helper(user: users_models.User) -> dict:
    resetPasswodToken = _get_reset_password_token(user)
    if not resetPasswodToken:
        raise users_exceptions.InvalidToken("No reset password token found")
    return dict(
        as_dict(user, includes=USER_INCLUDES),
        **{
            "resetPasswordToken": resetPasswodToken.encoded_token,
            "password": settings.TEST_DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def _get_reset_password_token(user: users_models.User) -> token_utils.Token | None:
    return token_utils.Token.get_token(token_utils.TokenType.RESET_PASSWORD, user.id)
