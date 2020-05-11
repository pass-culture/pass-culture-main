from flask import current_app as app, request

from validation.routes.bank_informations import check_refferer_type, check_demarches_simplifiees_webhook_token
from workers.bank_information_job import bank_information_job


@app.route('/bank_informations/<refferer_type>/application_update', methods=['POST'])
def post_update_demarches_simplifiees_application(refferer_type: str):
    check_demarches_simplifiees_webhook_token(request.args.get("token"))
    check_refferer_type(refferer_type)
    try:
        application_id = request.form['dossier_id']
    except:
        return '', 400

    bank_information_job.delay(application_id, refferer_type)
    return '', 202
