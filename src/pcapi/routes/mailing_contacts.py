from flask import request

from pcapi.flask_app import private_api
from pcapi.utils.rest import expect_json_data
from pcapi.validation.routes.mailing_contacts import validate_save_mailing_contact_request
from pcapi.workers.mailing_contacts_job import mailing_contacts_job


@private_api.route('/mailing-contacts', methods=['POST'])
@expect_json_data
def save_mailing_contact():
    json = request.get_json()
    validate_save_mailing_contact_request(json)
    contact_email = json["email"]
    contact_date_of_birth = json["dateOfBirth"]
    contact_department_code = json["departmentCode"]
    mailing_contacts_job.delay(contact_email, contact_date_of_birth, contact_department_code)
    return '', 201
