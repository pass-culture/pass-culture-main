import logging

from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_webapp_recaptcha_token
from pcapi.core.mails.transactional import users as user_emails
from pcapi.core.users import repository as users_repo
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import TokenType
from pcapi.domain.password import check_password_strength
from pcapi.domain.password import check_password_validity
from pcapi.domain.password import validate_change_password_request
from pcapi.domain.password import validate_new_password_request
from pcapi.domain.user_emails import send_reset_password_email_to_pro
from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.password_serialize import ResetPasswordBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.rest import expect_json_data


logger = logging.getLogger(__name__)


# @debt api-migration
@private_api.route("/users/current/change-password", methods=["POST"])
@login_required
@expect_json_data
def post_change_password():
    user = current_user._get_current_object()  # get underlying User object from proxy
    json = request.get_json()
    validate_change_password_request(json)
    new_password = json["newPassword"]
    new_confirmation_password = json["newConfirmationPassword"]
    old_password = json["oldPassword"]
    check_password_validity(new_password, new_confirmation_password, old_password, user)
    user.setPassword(new_password)
    repository.save(user)
    return "", 204


# @debt api-migration
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

    if user.isBeneficiary:
        send_email = user_emails.send_reset_password_email_to_user
    else:
        send_email = send_reset_password_email_to_pro

    try:
        send_email(user)
    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send reset password email", extra={"user": user.id, "exc": str(mail_service_exception)}
        )


# @debt api-migration
@private_api.route("/users/new-password", methods=["POST"])
@expect_json_data
def post_new_password():
    validate_new_password_request(request)
    token = request.get_json()["token"]
    new_password = request.get_json()["newPassword"]

    check_password_strength("newPassword", new_password)

    user = users_repo.get_user_with_valid_token(token, [TokenType.RESET_PASSWORD])

    if not user:
        errors = ApiErrors()
        errors.add_error("token", "Votre lien de changement de mot de passe est invalide.")
        raise errors

    user.setPassword(new_password)
    if not user.isEmailValidated:
        user.isEmailValidated = True
        update_external_user(user)

    repository.save(user)

    return "", 204
