from flask import current_app as app, request

from validation.routes.beneficiaries import check_licence_token_webhook_payload


@app.route('/beneficiaries/licence_verify', methods=['POST'])
def verify_id_check_licence_token():
    check_licence_token_webhook_payload(request)

    licence_token = request.json.get('token')
    if licence_token != 'authorized-token':
        return '', 422

    return '', 200
