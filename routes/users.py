"""users routes"""

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from domain.expenses import get_expenses
from models import PcObject
from repository.user_queries import find_user_by_reset_password_token
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.login_manager import stamp_session, discard_session
from utils.rest import expect_json_data, \
    login_or_api_key_required
from validation.users import check_allowed_changes_for_user, check_valid_signin


@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = current_user.as_dict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user)


@app.route("/users/token/<token>", methods=["GET"])
def check_activation_token_exists(token):
    user = find_user_by_reset_password_token(token)

    if user is None:
        return jsonify(), 404

    return jsonify(), 200


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    data = request.json.keys()
    check_allowed_changes_for_user(data)
    current_user.populateFromDict(request.json)
    PcObject.check_and_save(current_user)
    user = current_user.as_dict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user), 200


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    user = get_user_with_credentials(identifier, password)
    login_user(user, remember=True)
    stamp_session(user)
    user_dict = user.as_dict(include=USER_INCLUDES)
    user_dict['expenses'] = get_expenses(user.userBookings)
    return jsonify(user_dict), 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Deconnecté"})
