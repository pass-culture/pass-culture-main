import logging
from functools import partial

import flask
import sqlalchemy.orm as sa_orm
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug import Response

from pcapi import settings
from pcapi.connectors import harvestr
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
from pcapi.core import token as token_utils
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.subscription.phone_validation import exceptions as phone_exceptions
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import api as users_api
from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import gdpr_api
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.api import update_password_and_external_user
from pcapi.core.users.api import update_user_password
from pcapi.core.users.email import repository as email_repository
from pcapi.core.users.gdpr_api import anonymize_pro_user
from pcapi.core.users.password_utils import check_password_strength
from pcapi.core.users.password_utils import check_password_validity
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.api_errors import UnauthorizedError
from pcapi.models.feature import FeatureToggle
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import users as users_serializers
from pcapi.routes.serialization.password_serialize import CheckTokenBodyModel
from pcapi.routes.serialization.password_serialize import NewPasswordBodyModel
from pcapi.routes.serialization.password_serialize import ResetPasswordBodyModel
from pcapi.routes.shared.cookies_consent import CookieConsentRequest
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/users/signup", methods=["POST"])
@atomic()
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def signup_pro(body: users_serializers.ProUserCreationBodyV2Model) -> None:
    try:
        check_web_recaptcha_token(
            body.token,
            settings.RECAPTCHA_SECRET,
            original_action="signup",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})

    try:
        pro_user = users_api.create_pro_user(body)
        users_api.create_and_send_signup_email_confirmation(pro_user)
    except phone_exceptions.InvalidPhoneNumber:
        raise ApiErrors(errors={"phoneNumber": ["Le numéro de téléphone est invalide"]})
    except phone_exceptions.RequiredPhoneNumber:
        raise ApiErrors(errors={"phoneNumber": ["Le numéro de téléphone est requis"]})
    except users_exceptions.UserAlreadyExistsException:
        raise ApiErrors(errors={"email": ["l'email existe déjà"]})


@private_api.route("/users/validate_signup/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def validate_user(token: str) -> None:
    try:
        user_id = token_utils.validate_passwordless_token(token)["sub"]
        user = get_or_404(users_models.User, user_id)
        users_api.validate_pro_user_email(user)
    except (users_exceptions.InvalidToken, users_exceptions.ExpiredToken):
        raise ResourceNotFoundError(errors={"global": "Le lien est invalide ou a expiré. Veuillez recommencer."})
    logout_user()
    login_user(user)
    users_api.update_last_connection_date(user)


@private_api.route("/users/tuto-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_user_tuto_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_tuto_as_seen(user)


@private_api.route("/users/rgs-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_pro_user_rgs_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_rgs_as_seen(user)


@private_api.route("/users/current", methods=["GET"])
@login_required
@spectree_serialize(response_model=users_serializers.SharedCurrentUserResponseModel, api=blueprint.pro_private_schema)
def get_profile() -> users_serializers.SharedCurrentUserResponseModel:
    user = current_user._get_current_object()  # get underlying User object from proxy
    return users_serializers.SharedCurrentUserResponseModel.instantiate_model(
        user,
        is_impersonated=flask.session.get("internal_admin_email") is not None,
    )


@private_api.route("/users/identity", methods=["PATCH"])
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
    attributes = body.model_dump()
    users_api.update_user_info(user, author=current_user, **attributes)
    return users_serializers.UserIdentityResponseModel.model_validate(user)


@private_api.route("/users/phone", methods=["PATCH"])
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
    attributes = body.model_dump()
    users_api.update_user_info(user, author=current_user, **attributes)
    return users_serializers.UserPhoneResponseModel.from_orm(user)


@private_api.route("/users/validate_email", methods=["PATCH"])
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


@private_api.route("/users/email", methods=["POST"])
@login_required
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


@private_api.route("/users/email_pending_validation", methods=["GET"])
@login_required
@spectree_serialize(response_model=users_serializers.UserEmailValidationResponseModel, api=blueprint.pro_private_schema)
def get_user_email_pending_validation() -> users_serializers.UserEmailValidationResponseModel:
    user = current_user._get_current_object()
    pending_validation = email_repository.get_latest_pending_email_validation(user)
    return users_serializers.UserEmailValidationResponseModel.model_validate(pending_validation or {})


@private_api.route("/users/password", methods=["POST"])
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
    new_password = body.new_password
    new_confirmation_password = body.new_confirmation_password
    old_password = body.old_password
    check_password_validity(new_password, new_confirmation_password, old_password, user)
    update_user_password(user, new_password)
    transactional_mails.send_reset_password_email_to_connected_pro(user)


@private_api.route("/users/signin", methods=["POST"])
@spectree_serialize(response_model=users_serializers.SharedLoginUserResponseModel, api=blueprint.pro_private_schema)
def signin(body: users_serializers.LoginUserBodyModel) -> users_serializers.SharedLoginUserResponseModel:
    if not body.captcha_token:
        raise ApiErrors({"captchaToken": "Ce champ est obligatoire"})
    try:
        check_web_recaptcha_token(
            body.captcha_token,
            settings.RECAPTCHA_SECRET,
            original_action="loginUser",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"captchaToken": "The given token is invalid"})

    errors = UnauthorizedError()
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc

    if user.has_admin_role:
        errors.add_error("identifier", "Vous ne pouvez pas vous connecter avec un compte ADMIN.")
        raise errors

    logout_user()
    login_user(user)
    users_api.update_last_connection_date(user)

    return users_serializers.SharedLoginUserResponseModel.model_validate(user)


@private_api.route("/users/signout", methods=["GET"])
@login_required
@spectree_serialize(api=blueprint.pro_private_schema, on_success_status=204)
def signout() -> None:
    logout_user()


@private_api.route("/users/anonymize", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, on_error_statuses=[400, 404], api=blueprint.pro_private_schema)
@atomic()
def anonymize() -> None:
    if not FeatureToggle.WIP_PRO_AUTONOMOUS_ANONYMIZATION.is_active():
        raise ResourceNotFoundError(errors={"global": "Cette fonctionnalité n'est pas disponible"})

    user = current_user._get_current_object()

    if not gdpr_api.can_anonymise_pro_user(user):
        raise ForbiddenError(errors={"global": ["Le compte ne peut pas être anonymisé de manière autonome"]})

    anonymized = anonymize_pro_user(
        user=user, author=user, action_history_comment="Demande d’anonymisation depuis l’espace partenaire"
    )
    if anonymized:
        on_commit(
            partial(
                logger.info,
                "User has been anonymized",
                extra={"user_id": user.id},
                technical_message_id="user.anonymized",
            )
        )
        transactional_mails.send_anonymization_confirmation_email_to_pro(user.email)
    else:
        raise ApiErrors(errors={"global": ["Une erreur est survenue lors de l'anonymisation du compte"]})


@private_api.route("/users/anonymize/eligibility", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=users_serializers.ProAnonymizationEligibilityResponseModel, api=blueprint.pro_private_schema
)
def get_pro_anonymization_eligibility() -> users_serializers.ProAnonymizationEligibilityResponseModel:
    user = current_user._get_current_object()

    return users_serializers.ProAnonymizationEligibilityResponseModel(
        is_only_pro=gdpr_api.is_only_pro(user),
        has_suspended_offerer=gdpr_api.has_suspended_offerer(user),
        is_sole_user_with_ongoing_activities=gdpr_api.is_sole_user_with_ongoing_activities(user),
    )


@private_api.route("/users/cookies", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def cookies_consent(body: CookieConsentRequest) -> None:
    logger.info(
        "Cookies consent",
        extra={"analyticsSource": "app-pro", **body.dict()},
        technical_message_id="cookies_consent",
    )


@private_api.route("/users/connect-as/<token>", methods=["GET"])
@spectree_serialize(api=blueprint.pro_private_schema, raw_response=True, json_format=False)
def connect_as(token: str) -> Response:
    # This route is not used by PRO but it is used by the Backoffice
    try:
        secure_token = SecureToken(token=token)
    except users_exceptions.InvalidToken:
        raise ForbiddenError(
            errors={
                "global": "Le token est invalide",
            },
        )

    token_data = ConnectAsInternalModel(**secure_token.data)
    user = db.session.query(users_models.User).filter(users_models.User.id == token_data.user_id).one_or_none()

    if not user:
        raise ApiErrors(
            errors={
                "user": "L'utilisateur demandé n'existe pas",
            },
            status_code=404,
        )

    if not user.isActive:
        raise ForbiddenError(
            errors={
                "user": "L'utilisateur est inactif",
            },
        )

    if user.has_admin_role:
        raise ForbiddenError(
            errors={
                "user": "L'utilisateur est un admin",
            },
        )

    if user.has_anonymized_role:
        raise ForbiddenError(
            errors={
                "user": "L'utilisateur est anonyme",
            },
        )

    if not (user.has_non_attached_pro_role or user.has_pro_role):
        raise ForbiddenError(
            errors={
                "user": "L'utilisateur n'est pas un pro",
            },
        )

    history_api.add_action(history_models.ActionType.CONNECT_AS_USER, author=current_user, user=user)
    logout_user()
    login_user(user)
    flask.session["internal_admin_email"] = token_data.internal_admin_email
    flask.session["internal_admin_id"] = token_data.internal_admin_id
    return flask.redirect(token_data.redirect_link, code=302)


@private_api.route("/users/log-user-review", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def submit_user_review(body: users_serializers.SubmitReviewRequestModel) -> None:
    if not FeatureToggle.ENABLE_PRO_FEEDBACK.is_active():
        raise ApiErrors(errors={"global": "service not available"}, status_code=503)

    check_user_has_access_to_offerer(current_user, body.offerer_id)

    if body.user_comment:
        harvestr.create_message(
            title=f"Retour - {body.page_title}",
            content=body.user_comment,
            requester=harvestr.HaverstrRequester(
                name=current_user.full_name,
                externalUid=str(current_user.id),
                email=current_user.email,
            ),
            labels=["AC", f"location: {body.location}"],
        )

    logger.info(
        "User submitting review",
        extra={
            "offerer_id": body.offerer_id,
            "user_satisfaction": body.user_satisfaction,
            "user_comment": body.user_comment,
            "source_page": body.location,
        },
        technical_message_id="user_review",
    )


@private_api.route("/users/reset-password", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def reset_password(body: ResetPasswordBodyModel) -> None:
    try:
        check_web_recaptcha_token(
            body.token,
            settings.RECAPTCHA_SECRET,
            original_action="resetPassword",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})
    user = users_repo.find_user_by_email(body.email)

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
        user = (
            db.session.query(users_models.User)
            .options(sa_orm.selectinload(users_models.User.deposits).selectinload(finance_models.Deposit.recredits))
            .filter_by(id=token.user_id)
            .one()
        )
    except users_exceptions.InvalidToken:
        errors = ApiErrors()
        errors.add_error("token", "Votre lien de changement de mot de passe est invalide.")
        raise errors

    update_password_and_external_user(user, new_password)


@private_api.route("/users/check-token", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.pro_private_schema)
def post_check_token(body: CheckTokenBodyModel) -> None:
    token_value = body.token

    try:
        token_utils.Token.load_and_check(token_value, token_utils.TokenType.RESET_PASSWORD)

    except users_exceptions.InvalidToken:
        errors = ApiErrors()
        errors.add_error("token", "Votre lien de changement de mot de passe est invalide.")
        raise errors
