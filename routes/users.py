from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from repository.user_queries import find_user_by_reset_password_token, find_user_by_email
from use_cases.update_user_informations import update_user_informations, AlterableUserInformations
from routes.serialization import as_dict
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.login_manager import stamp_session, discard_session
from utils.rest import expect_json_data, \
    login_or_api_key_required
from validation.routes.users import check_allowed_changes_for_user, check_valid_signin


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


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    data = request.json.keys()
    check_allowed_changes_for_user(data)

    user_informations = AlterableUserInformations(
        id= current_user.id,
        cultural_survey_id=request.json.get('culturalSurveyId'),
        cultural_survey_filled_date=request.json.get('culturalSurveyFilledDate'),
        department_code=request.json.get('departementCode'),
        email=request.json.get('email'),
        needs_to_fill_cultural_survey=request.json.get('needsToFillCulturalSurvey'),
        phone_number=request.json.get('phoneNumber'),
        postal_code=request.json.get('postalCode'),
        public_name=request.json.get('publicName'),
        has_seen_tutorials=request.json.get('hasSeenTutorials')
    )
    user = update_user_informations(user_informations)

    formattedUser = as_dict(user, includes=USER_INCLUDES)
    return jsonify(formattedUser), 200


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    user = get_user_with_credentials(identifier, password)
    login_user(user, remember=True)
    stamp_session(user)
    return '', 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Deconnecté"})
