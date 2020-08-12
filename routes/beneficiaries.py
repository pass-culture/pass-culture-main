from flask import jsonify, request, current_app as app
from flask_login import current_user, login_required, login_user

from domain.beneficiary.beneficiary_licence import is_licence_token_valid
from routes.serialization import as_dict
from use_cases.update_user_informations import update_user_informations, AlterableUserInformations
from utils.credentials import get_user_with_credentials
from utils.includes import BENEFICIARY_INCLUDES
from utils.login_manager import stamp_session
from utils.rest import expect_json_data, login_or_api_key_required
from validation.routes.beneficiaries import check_application_update_payload, \
    check_verify_licence_token_payload, parse_application_id
from validation.routes.users import check_allowed_changes_for_user, check_valid_signin
from workers.beneficiary_job import beneficiary_job


@app.route("/beneficiaries/current", methods=["GET"])
@login_required
def get_beneficiary_profile():
    user = current_user._get_current_object()
    return jsonify(as_dict(user, includes=BENEFICIARY_INCLUDES)), 200


@app.route('/beneficiaries/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_beneficiary():
    data = request.json.keys()
    check_allowed_changes_for_user(data)

    user_informations = AlterableUserInformations(
        id=current_user.id,
        cultural_survey_id=request.json.get('culturalSurveyId'),
        cultural_survey_filled_date=request.json.get('culturalSurveyFilledDate'),
        department_code=request.json.get('departementCode'),
        email=request.json.get('email'),
        last_connection_date=request.json.get('lastConnectionDate'),
        needs_to_fill_cultural_survey=request.json.get('needsToFillCulturalSurvey'),
        phone_number=request.json.get('phoneNumber'),
        postal_code=request.json.get('postalCode'),
        public_name=request.json.get('publicName'),
        has_seen_tutorials=request.json.get('hasSeenTutorials')
    )
    user = update_user_informations(user_informations)

    formattedUser = as_dict(user, includes=BENEFICIARY_INCLUDES)
    return jsonify(formattedUser), 200


@app.route("/beneficiaries/signin", methods=["POST"])
def signin_beneficiary():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    user = get_user_with_credentials(identifier, password)
    login_user(user, remember=True)
    stamp_session(user)
    return jsonify(), 200


@app.route('/beneficiaries/licence_verify', methods=['POST'])
def verify_id_check_licence_token():
    check_verify_licence_token_payload(request)

    licence_token = request.json.get('token')
    licence_token_is_valid = is_licence_token_valid(licence_token)

    if not licence_token_is_valid:
        return '', 422

    return '', 200


@app.route('/beneficiaries/application_update', methods=['POST'])
def id_check_application_update():
    check_application_update_payload(request)

    raw_application_id = request.json.get('id')
    application_id = parse_application_id(raw_application_id)

    beneficiary_job.delay(application_id)

    return '', 200
