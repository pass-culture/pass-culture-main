from domain.beneficiary.beneficiary_licence import is_licence_token_valid
from flask import jsonify, request, current_app as app
from flask_login import current_user, login_required
from repository.user_queries import find_user_by_email
from routes.serialization import as_dict
from utils.includes import CURRENT_BENEFICIARY_INCLUDES
from validation.routes.beneficiaries import check_application_update_payload, \
    check_verify_licence_token_payload, parse_application_id
from workers.beneficiary_job import beneficiary_job


@app.route("/beneficiaries/current", methods=["GET"])
@login_required
def get_beneficiary_profile():
    user = current_user._get_current_object()
    return jsonify(as_dict(user, includes=CURRENT_BENEFICIARY_INCLUDES)), 200

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
