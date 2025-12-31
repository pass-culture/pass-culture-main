from datetime import datetime

from flask_login import current_user

from pcapi.core import token as token_utils
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import repository as email_repository
from pcapi.core.users.email import update as email_api
from pcapi.models import api_errors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.api_errors import account as account_errors
from pcapi.routes.native.v1.serialization import account as v1_serializers
from pcapi.routes.native.v1.serialization import authentication as authentication_serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import account as serializers


@blueprint.native_route("/profile/email_update/status", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.EmailUpdateStatusResponse)
@authenticated_and_active_user_required
def get_email_update_status() -> serializers.EmailUpdateStatusResponse:
    latest_email_update_event = email_repository.get_email_update_latest_event(current_user)
    if not latest_email_update_event:
        raise api_errors.ResourceNotFoundError

    new_email_selection_token: token_utils.Token | None = None
    reset_password_token: token_utils.Token | None = None
    if latest_email_update_event.eventType == users_models.EmailHistoryEventTypeEnum.CONFIRMATION:
        new_email_selection_token = token_utils.Token.get_token(
            token_utils.TokenType.EMAIL_CHANGE_NEW_EMAIL_SELECTION, current_user.id
        )
        if current_user.password is None:
            reset_password_token = token_utils.Token.get_token(token_utils.TokenType.RESET_PASSWORD, current_user.id)

    has_recently_reset_password = token_utils.Token.token_exists(
        token_utils.TokenType.RECENTLY_RESET_PASSWORD, current_user.id
    )

    return serializers.EmailUpdateStatusResponse(
        new_email=latest_email_update_event.newEmail,
        expired=(email_api.get_active_token_expiration(current_user) or datetime.min) < date_utils.get_naive_utc_now(),
        status=latest_email_update_event.eventType,
        token=new_email_selection_token.encoded_token if new_email_selection_token else None,
        reset_password_token=reset_password_token.encoded_token if reset_password_token else None,
        has_recently_reset_password=has_recently_reset_password,
    )


@blueprint.native_route("/profile/update_email", version="v2", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def update_user_email() -> None:
    try:
        email_api.request_email_update(current_user)
    except exceptions.EmailUpdateTokenExists as e:
        raise account_errors.EmailUpdatePendingError() from e
    except exceptions.EmailUpdateLimitReached as e:
        raise account_errors.EmailUpdateLimitError() from e


@blueprint.native_route("/profile/email_update/confirm", version="v2", methods=["POST"])
@spectree_serialize(
    on_success_status=200, api=blueprint.api, response_model=serializers.EmailChangeConfirmationResponse
)
@atomic()
def confirm_email_update(
    body: v1_serializers.ChangeBeneficiaryEmailBody,
) -> serializers.EmailChangeConfirmationResponse:
    try:
        user = email_api.confirm_email_update_request(body.token)
    except exceptions.InvalidToken as e:
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Aucune demande de changement d'email en cours"},
            status_code=401,
        ) from e

    reset_password_token = None
    if user.password is None:
        reset_password_token = api.create_reset_password_token(user).encoded_token

    new_email_selection_token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_CHANGE_NEW_EMAIL_SELECTION,
        constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user_id=user.id,
    ).encoded_token
    return serializers.EmailChangeConfirmationResponse(
        access_token=api.create_user_access_token(user),
        refresh_token=api.create_user_refresh_token(user, body.device_info),
        new_email_selection_token=new_email_selection_token,
        reset_password_token=reset_password_token,
    )


@blueprint.native_route("/profile/email_update/new_password", version="v2", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@atomic()
def select_new_password(body: authentication_serializers.ResetPasswordRequest) -> None:
    user = api.reset_password_with_token(body.new_password, body.reset_password_token)
    api.create_recently_reset_password_token(user)


@blueprint.native_route("/profile/email_update/new_email", version="v2", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def select_new_email(body: serializers.NewEmailSelectionRequest) -> None:
    if current_user.password is None:
        raise api_errors.ApiErrors(
            {"code": "PASSWORD_NEEDED", "message": "Un mot de passe doit être défini pour changer d'email"},
            status_code=403,
        )
    try:
        email_api.confirm_new_email_selection_and_send_mail(current_user, body.token, body.new_email)
    except exceptions.InvalidToken as e:
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Aucune demande de changement d'email en cours"},
            status_code=401,
        ) from e
    except exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses through user enumeration attacks.
        pass
