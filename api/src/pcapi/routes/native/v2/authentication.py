from pcapi.connectors import api_recaptcha
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.v2.serialization import authentication
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


@blueprint.native_route("/signin", version="v2", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponseV2,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
def signin(body: authentication.SigninRequestV2) -> authentication.SigninResponseV2:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise ApiErrors({"token": "Le token est invalide"}, 401)
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    if user.account_state.is_deleted or user.account_state == user_models.AccountState.ANONYMIZED:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]})

    users_api.save_device_info_and_notify_user(user, body.device_info)

    users_api.update_last_connection_date(user)
    tokens = create_user_jwt_tokens(
        user=user,
        device_info=body.device_info,
    )
    return authentication.SigninResponseV2(
        access_token=tokens.access,
        refresh_token=tokens.refresh,
        account_state=user.account_state,
    )
