from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity
)

from pcapi.core.users import api as user_api
from pcapi.core.users import exceptions as user_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

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
        errors.add_error('general', 'Identifiant ou Mot de passe incorrect')
        raise errors from exc
    # TODO: Should we fill the token with some less trivial data ?
    return authentication.SigninResponse(
        access_token=create_access_token(identity=body.identifier),
        refresh_token=create_refresh_token(identity=body.identifier),
    )


# TODO: temporary resource to test JWT authentication on a resource
@blueprint.native_v1.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    from flask import jsonify
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
