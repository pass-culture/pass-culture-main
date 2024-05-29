import logging

from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.token as token_utils
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.api import update_password_and_external_user
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain.password import check_password_strength
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization.password_serialize import NewPasswordBodyModel
from pcapi.routes.serialization.password_serialize import ResetPasswordBodyModel
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@private_api.route("/users/reset-password", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def reset_password(body: ResetPasswordBodyModel) -> None:
    try:
        check_web_recaptcha_token(
            body.token,
            original_action="resetPassword",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})
    user = find_user_by_email(body.email)

    if not user or not user.isActive:
        # Here we also return a 204 to prevent attacker from discovering which email exists in db
        return

    token = users_api.create_reset_password_token(user)
    if user.is_beneficiary:
        transactional_mails.send_reset_password_email_to_user(token)
    else:
        transactional_mails.send_reset_password_email_to_pro(token)


@private_api.route("/users/new-password", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def post_new_password(body: NewPasswordBodyModel) -> None:
    token_value = body.token
    new_password = body.newPassword

    check_password_strength("newPassword", new_password)
    try:
        token = token_utils.Token.load_and_check(token_value, token_utils.TokenType.RESET_PASSWORD)
        token.expire()
        user = users_models.User.query.filter_by(id=token.user_id).one()
    except users_exceptions.InvalidToken:
        errors = ApiErrors()
        errors.add_error("token", "Votre lien de changement de mot de passe est invalide.")
        raise errors

    update_password_and_external_user(user, new_password)
