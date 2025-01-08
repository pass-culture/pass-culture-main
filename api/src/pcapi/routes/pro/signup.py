from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
from pcapi.core.subscription.phone_validation import exceptions as phone_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import users as users_serialize
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/v2/users/signup/pro", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def signup_pro_V2(body: users_serialize.ProUserCreationBodyV2Model) -> None:
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
        users_api.create_pro_user_V2(body)
    except phone_exceptions.InvalidPhoneNumber:
        raise ApiErrors(errors={"phoneNumber": ["Le numéro de téléphone est invalide"]})
    except users_exceptions.UserAlreadyExistsException:
        raise ApiErrors(errors={"email": ["l'email existe déjà"]})
