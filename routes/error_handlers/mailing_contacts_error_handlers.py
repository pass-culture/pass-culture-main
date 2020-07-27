from typing import Tuple

from flask import current_app as app, jsonify, Response

from domain.beneficiary_contact.beneficiary_contact_exceptions import AddNewBeneficiaryContactException


@app.errorhandler(AddNewBeneficiaryContactException)
def handle_add_contact_in_eligibility_list(exception: AddNewBeneficiaryContactException) -> Tuple[Response, int]:
    return jsonify(exception.errors), 400
