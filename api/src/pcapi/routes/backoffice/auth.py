from pcapi.core.auth.api import authenticate_with_permissions
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import AuthTokenQuery
from .serialization import AuthTokenResponseModel


@blueprint.backoffice_blueprint.route("auth/token", methods=["GET"])
@spectree_serialize(
    response_model=AuthTokenResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_auth_token(query: AuthTokenQuery) -> AuthTokenResponseModel:
    token = authenticate_with_permissions(query.token)
    return AuthTokenResponseModel(token=token)
