from flask import current_app as app, request

from validation.routes.beneficiaries import check_verify_licence_token_payload, \
    check_licence_token_is_valid, check_application_update_payload, parse_application_id


@app.route('/beneficiaries/licence_verify', methods=['POST'])
def verify_id_check_licence_token():
    check_verify_licence_token_payload(request)

    licence_token = request.json.get('token')
    licence_token_is_valid = check_licence_token_is_valid(licence_token)

    if not licence_token_is_valid:
        return '', 422

    return '', 200

@app.route('/beneficiaries/application_update', methods=['POST'])
def id_check_application_update():
    check_application_update_payload(request)

    raw_application_id = request.json.get('id')
    application_id = parse_application_id(raw_application_id)

    return '', 200
