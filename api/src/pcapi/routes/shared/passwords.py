import logging

from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_webapp_recaptcha_token
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_email_to_pro
from pcapi.core.mails.transactional.users.reset_password import send_reset_password_email_to_user
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.api import update_password_and_external_user
from pcapi.core.users.models import TokenType
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain.password import check_password_strength
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.password_serialize import NewPasswordBodyModel
from pcapi.routes.serialization.password_serialize import ResetPasswordBodyModel
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@private_api.route("/users/reset-password", methods=["POST"])
@spectree_serialize(on_success_status=204)
def post_for_password_token(body: ResetPasswordBodyModel) -> None:
    try:
        check_webapp_recaptcha_token(
            body.token,
            original_action="resetPassword",
            minimal_score=settings.RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})
    user = find_user_by_email(body.email)

    if not user or not user.isActive:
        # Here we also return a 204 to prevent attacker from discovering which email exists in db
        return

    if user.is_beneficiary:
        send_email = send_reset_password_email_to_user
    else:
        send_email = send_reset_password_email_to_pro

    if not send_email(user):
        logger.warning("Could not send reset password email", extra={"user": user.id})


@private_api.route("/users/new-password", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400])
def post_new_password(body: NewPasswordBodyModel) -> None:
    token = body.token
    new_password = body.newPassword

    check_password_strength("newPassword", new_password)

    try:
        user = users_repo.get_user_with_valid_token(token, [TokenType.RESET_PASSWORD])
    except users_exceptions.InvalidToken:
        errors = ApiErrors()
        errors.add_error("token", "Votre lien de changement de mot de passe est invalide.")
        raise errors

    update_password_and_external_user(user, new_password)
