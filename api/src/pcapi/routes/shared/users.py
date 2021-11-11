from flask import jsonify
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import TokenType
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import users as serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.login_manager import discard_session
from pcapi.utils.login_manager import stamp_session
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter


@private_api.route("/users/current", methods=["GET"])
@login_required
@spectree_serialize(response_model=serializers.SharedCurrentUserResponseModel)
def get_profile():
    user = current_user._get_current_object()  # get underlying User object from proxy
    return serializers.SharedCurrentUserResponseModel.from_orm(user)


# @debt api-migration
@private_api.route("/users/token/<token>", methods=["GET"])
def check_activation_token_exists(token):
    user = users_repo.get_user_with_valid_token(token, [TokenType.RESET_PASSWORD], use_token=False)
    if user is None:
        return jsonify(), 404

    return jsonify(), 200


@private_api.route("/users/signin", methods=["POST"])
@spectree_serialize(response_model=serializers.SharedLoginUserResponseModel)
@ip_rate_limiter()
@email_rate_limiter()
def signin(body: serializers.LoginUserBodyModel) -> serializers.SharedLoginUserResponseModel:
    errors = ApiErrors()
    errors.status_code = 401
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc

    login_user(user)
    stamp_session(user)

    return serializers.SharedLoginUserResponseModel.from_orm(user)


@private_api.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Déconnecté"})
