"""users routes"""

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from domain.expenses import get_expenses
from domain.password import validate_reset_request, check_reset_token_validity, validate_new_password_request, \
    check_password_strength, check_new_password_validity, generate_reset_token, validate_change_password_request
from domain.user_emails import send_reset_password_email
from models import ApiErrors, PcObject
from repository.user_queries import find_user_by_email, find_user_by_reset_password_token
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.login_manager import stamp_session, discard_session
from utils.mailing import \
    MailServiceException
from utils.rest import expect_json_data, \
    login_or_api_key_required
from validation.users import check_allowed_changes_for_user, check_valid_signin


def is_pro_signup(json_user):
    return 'siren' in json_user


@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = current_user._asdict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user)


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    data = request.json.keys()
    check_allowed_changes_for_user(data)
    current_user.populateFromDict(request.json)
    PcObject.check_and_save(current_user)
    user = current_user._asdict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user), 200


@app.route('/users/current/change-password', methods=['POST'])
@login_required
@expect_json_data
def post_change_password():
    json = request.get_json()
    validate_change_password_request(json)
    new_password = request.get_json()['newPassword']
    old_password = json.get('oldPassword')
    check_password_strength('newPassword', new_password)
    check_new_password_validity(current_user, old_password, new_password)
    current_user.setPassword(new_password)
    PcObject.check_and_save(current_user)
    return '', 204


@app.route("/users/reset-password", methods=['POST'])
@expect_json_data
def post_for_password_token():
    validate_reset_request(request)
    email = request.get_json()['email']
    user = find_user_by_email(email)

    if not user:
        return '', 204

    generate_reset_token(user)
    PcObject.check_and_save(user)
    app_origin_url = request.headers.get('origin')

    try:
        send_reset_password_email(user, app.mailjet_client.send.create, app_origin_url)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return '', 204


@app.route("/users/new-password", methods=['POST'])
@expect_json_data
def post_new_password():
    validate_new_password_request(request)
    token = request.get_json()['token']
    new_password = request.get_json()['newPassword']
    user = find_user_by_reset_password_token(token)

    if not user:
        errors = ApiErrors()
        errors.addError('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    check_reset_token_validity(user)
    check_password_strength('newPassword', new_password)
    user.setPassword(new_password)
    PcObject.check_and_save(user)
    return '', 204


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    user = get_user_with_credentials(identifier, password)
    login_user(user, remember=True)
    stamp_session(user)
    user_dict = user._asdict(include=USER_INCLUDES)
    user_dict['expenses'] = get_expenses(user.userBookings)
    return jsonify(user_dict), 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Deconnecté"})
