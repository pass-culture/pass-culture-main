import flask
from flask import abort
from flask import jsonify
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import TokenType
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import users as users_serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.login_manager import discard_session
from pcapi.utils.login_manager import stamp_session
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter

from . import blueprint


@blueprint.pro_private_api.route("/users/tuto-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_user_tuto_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_tuto_as_seen(user)


@blueprint.pro_private_api.route("/users/rgs-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_pro_user_rgs_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_rgs_as_seen(user)


@blueprint.pro_private_api.route("/users/current", methods=["GET"])
@login_required
@spectree_serialize(response_model=users_serializers.SharedCurrentUserResponseModel, api=blueprint.pro_private_schema)
def get_profile() -> users_serializers.SharedCurrentUserResponseModel:
    user = current_user._get_current_object()  # get underlying User object from proxy
    return users_serializers.SharedCurrentUserResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/current", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=users_serializers.PatchProUserResponseModel, api=blueprint.pro_private_schema)
def patch_profile(body: users_serializers.PatchProUserBodyModel) -> users_serializers.PatchProUserResponseModel:
    user = current_user._get_current_object()  # get underlying User object from proxy
    # This route should ony be used by "pro" users because it allows
    # to update different infos from `/beneficiaries/current`.
    if not user.has_pro_role and not user.has_admin_role:
        abort(400)
    attributes = body.dict()
    users_api.update_user_info(user, **attributes)
    return users_serializers.PatchProUserResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/identity", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=users_serializers.UserIdentityResponseModel, api=blueprint.pro_private_schema)
def patch_user_identity(body: users_serializers.UserIdentityBodyModel) -> users_serializers.UserIdentityResponseModel:
    user = current_user._get_current_object()
    if not user.has_pro_role and not user.has_admin_role:
        abort(400)
    attributes = body.dict()
    users_api.update_user_info(user, **attributes)
    return users_serializers.UserIdentityResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/token/<token>", methods=["GET"])
@spectree_serialize(on_error_statuses=[404], on_success_status=204, api=blueprint.pro_private_schema)
def check_activation_token_exists(token: str) -> None:
    user = users_repo.get_user_with_valid_token(token, [TokenType.RESET_PASSWORD], use_token=False)
    if user is None:
        flask.abort(404)


@blueprint.pro_private_api.route("/users/signin", methods=["POST"])
@spectree_serialize(response_model=users_serializers.SharedLoginUserResponseModel, api=blueprint.pro_private_schema)
@ip_rate_limiter()
@email_rate_limiter()
def signin(body: users_serializers.LoginUserBodyModel) -> users_serializers.SharedLoginUserResponseModel:
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

    return users_serializers.SharedLoginUserResponseModel.from_orm(user)


@blueprint.pro_private_api.route("/users/signout", methods=["GET"])
@login_required
def signout():  # type: ignore [no-untyped-def]
    discard_session()
    logout_user()
    return jsonify({"global": "Déconnecté"})
