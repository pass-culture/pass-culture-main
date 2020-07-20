from flask import current_app as app, request
from utils.rest import expect_json_data
from validation.routes.mailing_contacts import validate_save_mailing_contact_request
from infrastructure.container import add_contact_in_eligibility_list


@app.route('/mailing_contacts', methods=['POST'])
@expect_json_data
def save_mailing_contact():
    json = request.get_json()
    validate_save_mailing_contact_request(json)
    contact_email = json["email"]
    contact_date_of_birth = json["date_of_birth"]
    contact_department_code = json["department_code"]
    add_contact_in_eligibility_list.execute(contact_email, contact_date_of_birth, contact_department_code)
    return '', 200
