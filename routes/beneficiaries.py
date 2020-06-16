from flask import current_app as app, request


@app.route('/beneficiaries/licence_verify', methods=['POST'])
def verify_id_check_licence_token():
    licence_token = request.args.get("token")

    if licence_token != "authorized-token":
        return '', 422

    return '', 200
