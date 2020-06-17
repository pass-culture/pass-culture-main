from flask import current_app as app, request

from validation.routes.beneficiaries import check_verify_licence_token_payload, check_licence_token_is_valid


@app.route('/beneficiaries/licence_verify', methods=['POST'])
def verify_id_check_licence_token():
    check_verify_licence_token_payload(request)

    licence_token = request.json.get('token')
    licence_token_is_valid = check_licence_token_is_valid(licence_token)

    if not licence_token_is_valid:
        return '', 422

    return '', 200
