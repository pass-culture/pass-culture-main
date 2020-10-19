from flask import request

from pcapi.flask_app import private_api, \
    public_api
from pcapi.validation.routes.bank_informations import check_demarches_simplifiees_webhook_payload, \
    check_demarches_simplifiees_webhook_token
from pcapi.workers.bank_information_job import bank_information_job


@public_api.route('/bank_informations/venue/application_update', methods=['POST'])
def update_venue_demarches_simplifiees_application():
    check_demarches_simplifiees_webhook_token(request.args.get("token"))
    check_demarches_simplifiees_webhook_payload(request)
    application_id = request.form['dossier_id']
    bank_information_job.delay(application_id, 'venue')
    return '', 202


@public_api.route('/bank_informations/offerer/application_update', methods=['POST'])
def update_offerer_demarches_simplifiees_application():
    check_demarches_simplifiees_webhook_token(request.args.get("token"))
    check_demarches_simplifiees_webhook_payload(request)
    application_id = request.form['dossier_id']
    bank_information_job.delay(application_id, 'offerer')
    return '', 202
