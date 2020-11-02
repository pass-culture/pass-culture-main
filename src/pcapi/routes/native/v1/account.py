from typing import Tuple
from flask import current_app as app
from pcapi.domain.password import generate_reset_token
from pcapi.domain.user_emails import send_reset_password_email_to_user
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.native.v1.serialization.account import PasswordResetRequestModel
from pcapi.repository import repository
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.mailing import MailServiceException, send_raw_email

from . import blueprint


@blueprint.native_v1.route("/password_reset", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)  # type: ignore
def send_reset_password_email(body: PasswordResetRequestModel) -> Tuple[str, int]:
    user = find_user_by_email(body.email)

    if not user:
        return "", 204

    generate_reset_token(user)
    repository.save(user)

    try:
        send_reset_password_email_to_user(user, send_raw_email)
    except MailServiceException as mail_service_exception:
        app.logger.error("[send_reset_password_email] Mail service failure", mail_service_exception)
        return "", 500

    return "", 204
