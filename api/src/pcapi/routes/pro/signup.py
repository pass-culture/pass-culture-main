from pcapi.core.subscription.phone_validation import exceptions as phone_exceptions
from pcapi.core.users.api import create_pro_user_and_offerer
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/users/signup/pro", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def signup_pro(body: ProUserCreationBodyModel) -> None:
    try:
        create_pro_user_and_offerer(body)
    except phone_exceptions.InvalidPhoneNumber:
        raise ApiErrors(errors={"phoneNumber": ["Le numéro de téléphone est invalide"]})
