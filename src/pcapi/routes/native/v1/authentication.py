from flask_login import login_user

from pcapi.utils.credentials import get_user_with_credentials
from pcapi.utils.login_manager import stamp_session
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import authentication


@blueprint.native_v1.route("/signin", methods=["POST"])
@spectree_serialize(response_model=authentication.SigninResponseModel, on_success_status=200, api=blueprint.api)  # type: ignore
def signin(body: authentication.SigninRequestModel) -> authentication.SigninResponseModel:
    user = get_user_with_credentials(body.identifier, body.password)
    login_user(user, remember=True)
    stamp_session(user)

    return authentication.SigninResponseModel()
