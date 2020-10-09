from flask import current_app as app, jsonify, request, make_response, Response as FlaskResponse
from flask_login import current_user, login_required, logout_user, login_user
from spectree import Response

from pcapi.repository.user_queries import find_user_by_reset_password_token, find_user_by_email
from pcapi.use_cases.update_user_informations import update_user_informations, AlterableUserInformations
from pcapi.routes.serialization import as_dict
from pcapi.utils.credentials import get_user_with_credentials
from pcapi.utils.includes import USER_INCLUDES
from pcapi.utils.login_manager import stamp_session, discard_session
from pcapi.utils.rest import expect_json_data, \
    login_or_api_key_required
from pcapi.validation.routes.users import check_allowed_changes_for_user, check_valid_signin
from pcapi.validation.routes.users import check_allowed_changes_for_user, check_valid_signin
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import humanize
from pcapi.routes.serialization.users import PatchUserBodyModel, PatchUserResponseModel
from pcapi.utils.date import format_into_utc_date

@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = find_user_by_email(current_user.email)
    return jsonify(as_dict(user, includes=USER_INCLUDES)), 200


@app.route("/users/token/<token>", methods=["GET"])
def check_activation_token_exists(token):
    user = find_user_by_reset_password_token(token)

    if user is None:
        return jsonify(), 404

    return jsonify(), 200


@app.route("/users/current", methods=["PATCH"])
@login_or_api_key_required
@expect_json_data
@spectree_serialize(response_model=PatchUserResponseModel)
def patch_profile(body: PatchUserBodyModel) -> PatchUserResponseModel:
    user_informations = AlterableUserInformations(id=current_user.id, **body.dict())
    user = update_user_informations(user_informations)
    response_user_model = PatchUserResponseModel.from_orm(user)
    response_user_model.id = humanize(current_user.id)
    response_user_model.dateCreated = format_into_utc_date(current_user.dateCreated)
    return response_user_model


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    user = get_user_with_credentials(identifier, password)
    login_user(user, remember=True)
    stamp_session(user)
    return jsonify(as_dict(user, includes=USER_INCLUDES)), 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Déconnecté"})
