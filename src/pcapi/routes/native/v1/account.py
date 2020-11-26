from flask import current_app as app
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.models.api_errors import ApiErrors
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import account


@blueprint.native_v1.route("/me", methods=["GET"])
@spectree_serialize(
    response_model=account.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@jwt_required
def get_user_profile() -> account.UserProfileResponse:
    identifier = get_jwt_identity()
    user = UserSQLEntity.query.filter_by(email=identifier).first()

    if user is None:
        app.logger.error("Authenticated user with email %s not found", identifier)
        raise ApiErrors({"email": ["Utilisateur introuvable"]})

    return account.UserProfileResponse(
        first_name=user.firstName if user.firstName != VOID_FIRST_NAME else None, email=user.email
    )
