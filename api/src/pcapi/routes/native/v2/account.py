from pcapi.core import token as token_utils
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_api
from pcapi.models import api_errors
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.api_errors import account as account_errors
from pcapi.routes.native.v1.serialization import account as v1_serializers
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import account as serializers


@blueprint.native_route("/profile/update_email", version="v2", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def update_user_email(user: users_models.User) -> None:
    try:
        email_api.request_email_update(user)
    except exceptions.EmailUpdateTokenExists:
        raise account_errors.EmailUpdatePendingError()
    except exceptions.EmailUpdateLimitReached:
        raise account_errors.EmailUpdateLimitError()


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
    except exceptions.InvalidToken:
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Aucune demande de changement d'email en cours"},
            status_code=401,
        )

    new_mail_selection_token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_CHANGE_NEW_EMAIL_SELECTION,
        constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user_id=user.id,
    ).encoded_token
    return serializers.EmailChangeConfirmationResponse(
        access_token=api.create_user_access_token(user),
        refresh_token=api.create_user_refresh_token(user, body.device_info),
        new_email_selection_token=new_mail_selection_token,
    )
