from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

from pcapi.utils.credentials import get_user_with_credentials
from pcapi.utils.login_manager import stamp_session
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import authentication


@blueprint.native_v1.route("/signin", methods=["POST"])
@spectree_serialize(response_model=authentication.SigninResponseModel, on_success_status=200, api=blueprint.api)  # type: ignore
def signin(body: authentication.SigninRequestModel) -> authentication.SigninResponseModel:
    user = get_user_with_credentials(body.identifier, body.password)
    access_token = create_access_token(identity=body.identifier)
    return authentication.SigninResponseModel(access_token=access_token)


# TODO: temporary resource to test JWT authentication on a resource
@blueprint.native_v1.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    from flask import jsonify
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
