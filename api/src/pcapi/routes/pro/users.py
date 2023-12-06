import logging

import flask
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
from pcapi.core import token as token_utils
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.users import api as users_api
from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.api import update_user_password
from pcapi.core.users.email import repository as email_repository
from pcapi.domain.password import check_password_validity
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import users as users_serializers
from pcapi.routes.shared.cookies_consent import CookieConsentRequest
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.login_manager import discard_session
from pcapi.utils.login_manager import stamp_session
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_private_api.route("/users/tuto-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_user_tuto_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_tuto_as_seen(user)


@blueprint.pro_private_api.route("/users/rgs-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_pro_user_rgs_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_rgs_as_seen(user)


@blueprint.pro_private_api.route("/users/current", methods=["GET"])
@login_required
@spectree_serialize(response_model=users_serializers.SharedCurrentUserResponseModel, api=blueprint.pro_private_schema)
def get_profile() -> users_serializers.SharedCurrentUserResponseModel:
    user = current_user._get_current_object()  # get underlying User object from proxy
    return users_serializers.SharedCurrentUserResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/identity", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=users_serializers.UserIdentityResponseModel, api=blueprint.pro_private_schema)
def patch_user_identity(body: users_serializers.UserIdentityBodyModel) -> users_serializers.UserIdentityResponseModel:
    user = current_user._get_current_object()
    if not user.has_pro_role and not user.has_admin_role:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error(
            "firstName", "Vos modifications ne peuvent pas être acceptées tant que votre compte n’a pas été validé"
        )
        raise errors
    attributes = body.dict()
    users_api.update_user_info(user, author=current_user, **attributes).log_update(save=True)
    return users_serializers.UserIdentityResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/phone", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=users_serializers.UserPhoneResponseModel, api=blueprint.pro_private_schema)
def patch_user_phone(body: users_serializers.UserPhoneBodyModel) -> users_serializers.UserPhoneResponseModel:
    user = current_user._get_current_object()
    if not user.has_pro_role and not user.has_admin_role:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error(
            "phoneNumber", "Vos modifications ne peuvent pas être acceptées tant que votre compte n’a pas été validé"
        )
        raise errors
    attributes = body.dict()
    users_api.update_user_info(user, author=current_user, **attributes).log_update(save=True)
    return users_serializers.UserPhoneResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/validate_email", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def patch_validate_email(body: users_serializers.ChangeProEmailBody) -> None:
    errors = ApiErrors()
    errors.status_code = 400
    try:
        token = token_utils.Token.load_and_check(body.token, token_utils.TokenType.EMAIL_CHANGE_VALIDATION)
        token.expire()
        users_api.change_pro_user_email(
            current_email=token.data["current_email"], new_email=token.data["new_email"], user_id=token.user_id
        )
    except (users_exceptions.InvalidToken, users_exceptions.UserDoesNotExist) as exc:
        errors.add_error("global", "Token invalide")
        raise errors from exc
    except users_exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses.
        pass


@blueprint.pro_private_api.route("/users/email", methods=["POST"])
@login_required
@ip_rate_limiter()
@spectree_serialize(api=blueprint.pro_private_schema, on_success_status=204)
def post_user_email(body: users_serializers.UserResetEmailBodyModel) -> None:
    errors = ApiErrors()
    errors.status_code = 400
    user = current_user._get_current_object()
    if not user.has_pro_role and not user.has_admin_role:
        errors.add_error(
            "email", "Vos modifications ne peuvent pas être acceptées tant que votre compte n’a pas été validé "
        )
        raise errors
    try:
        email_api.request_email_update_from_pro(user, body.email, body.password)
    except users_exceptions.EmailUpdateTokenExists as exc:
        errors.add_error("email", "Une demande de modification d'adresse email est déjà en cours")
        raise errors from exc
    except users_exceptions.EmailUpdateInvalidPassword as exc:
        errors.add_error("password", "Votre mot de passe est incorrect")
        raise errors from exc
    except users_exceptions.InvalidEmailError as exc:
        errors.add_error("email", "Votre adresse email est invalide")
        raise errors from exc
    except users_exceptions.EmailUpdateLimitReached as exc:
        errors.add_error("email", "Trop de tentatives, réessayez dans 24 heures")
        raise errors from exc
    except users_exceptions.EmailExistsError as exc:
        errors.add_error("email", "Un compte lié à cet email existe déjà")
        raise errors from exc


@blueprint.pro_private_api.route("/users/email_pending_validation", methods=["GET"])
@login_required
@spectree_serialize(response_model=users_serializers.UserEmailValidationResponseModel, api=blueprint.pro_private_schema)
def get_user_email_pending_validation() -> users_serializers.UserEmailValidationResponseModel:
    user = current_user._get_current_object()
    pending_validation = email_repository.get_latest_pending_email_validation(user)
    return users_serializers.UserEmailValidationResponseModel.from_orm(pending_validation)


@blueprint.pro_private_api.route("/users/token/<token>", methods=["GET"])
@spectree_serialize(on_error_statuses=[404], on_success_status=204, api=blueprint.pro_private_schema)
def check_activation_token_exists(token: str) -> None:
    # TODO (yacine-pc) 04-10-23 check if this route is needed, remove it else
    try:
        token_utils.Token.load_and_check(token, token_utils.TokenType.RESET_PASSWORD)
    except users_exceptions.InvalidToken:
        flask.abort(404)


@blueprint.pro_private_api.route("/users/password", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def post_change_password(body: users_serializers.ChangePasswordBodyModel) -> None:
    errors = ApiErrors()
    errors.status_code = 400
    user = current_user._get_current_object()
    if not user.has_pro_role and not user.has_admin_role:
        errors.add_error(
            "oldPassword", "Vos modifications ne peuvent pas être acceptées tant que votre compte n’a pas été validé"
        )
        raise errors
    new_password = body.newPassword
    new_confirmation_password = body.newConfirmationPassword
    old_password = body.oldPassword
    check_password_validity(new_password, new_confirmation_password, old_password, user)
    update_user_password(user, new_password)
    transactional_mails.send_reset_password_email_to_connected_pro(user)


@blueprint.pro_private_api.route("/users/signin", methods=["POST"])
@spectree_serialize(response_model=users_serializers.SharedLoginUserResponseModel, api=blueprint.pro_private_schema)
@ip_rate_limiter()
@email_rate_limiter()
def signin(body: users_serializers.LoginUserBodyModel) -> users_serializers.SharedLoginUserResponseModel:
    try:
        check_web_recaptcha_token(
            body.captchaToken,
            original_action="loginUser",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})

    errors = ApiErrors()
    errors.status_code = 401
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc

    login_user(user)
    stamp_session(user)

    return users_serializers.SharedLoginUserResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/signout", methods=["GET"])
@login_required
@spectree_serialize(api=blueprint.pro_private_schema, on_success_status=204)
def signout() -> None:
    discard_session()
    logout_user()


@blueprint.pro_private_api.route("/users/pro_flags", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def post_pro_flags(body: users_serializers.ProFlagsQueryModel) -> None:
    users_api.save_flags(user=current_user, flags=body.dict())


@blueprint.pro_private_api.route("/users/cookies", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def cookies_consent(body: CookieConsentRequest) -> None:
    logger.info(
        "Cookies consent",
        extra={"analyticsSource": "app-pro", **body.dict()},
        technical_message_id="cookies_consent",
    )
