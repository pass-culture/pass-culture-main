from flask import current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
)

from pcapi.core.users import api as user_api
from pcapi.core.users import exceptions as user_exceptions
from pcapi.domain.password import generate_reset_token
from pcapi.domain.user_emails import send_reset_password_email_to_user
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.native.v1.serialization.authentication import PasswordResetRequestRequest
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.mailing import MailServiceException, send_raw_email

from . import blueprint
from .serialization import authentication


@blueprint.native_v1.route("/signin", methods=["POST"])
@spectree_serialize(response_model=authentication.SigninResponse, on_success_status=200, api=blueprint.api)  # type: ignore
def signin(body: authentication.SigninRequest) -> authentication.SigninResponse:
    try:
        user_api.get_user_with_credentials(body.identifier, body.password)
    except user_exceptions.CredentialsException as exc:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error("general", "Identifiant ou Mot de passe incorrect")
        raise errors from exc
    # TODO: Should we fill the token with some less trivial data ?
    return authentication.SigninResponse(
        access_token=create_access_token(identity=body.identifier),
        refresh_token=create_refresh_token(identity=body.identifier),
    )


@blueprint.native_v1.route("/refresh_access_token", methods=["POST"])
@jwt_refresh_token_required
@spectree_serialize(response_model=authentication.RefreshResponse, api=blueprint.api)  # type: ignore
def refresh() -> authentication.RefreshResponse:
    current_user = get_jwt_identity()
    return authentication.RefreshResponse(access_token=create_access_token(identity=current_user))


@blueprint.native_v1.route("/password_reset_request", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[503])  # type: ignore
def password_reset_request(body: PasswordResetRequestRequest) -> None:
    user = find_user_by_email(body.email)

    if not user:
        return

    generate_reset_token(user)
    repository.save(user)

    is_email_sent = send_reset_password_email_to_user(user, send_raw_email)

    if not is_email_sent:
        app.logger.error(
            'Email service failure when user request password reset with %s', user.email
        )
        errors = ApiErrors({'error': "L'email n'a pas pu être envoyé"})
        errors.status_code = 400
        raise errors


# TODO: temporary resource to test JWT authentication on a resource
@blueprint.native_v1.route("/protected", methods=["GET"])
@jwt_required
def protected() -> any:
    # Access the identity of the current user with get_jwt_identity
    from flask import jsonify

    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
