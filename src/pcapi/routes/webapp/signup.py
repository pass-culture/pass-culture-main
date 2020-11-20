from flask import current_app as app
from flask import jsonify
from flask import request

from pcapi.connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from pcapi.flask_app import private_api
from pcapi.models import ApiErrors
from pcapi.models import Deposit
from pcapi.models import UserSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict
from pcapi.utils.config import IS_INTEGRATION
from pcapi.utils.feature import feature_required
from pcapi.utils.includes import BENEFICIARY_INCLUDES
from pcapi.utils.logger import logger
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.mailing import subscribe_newsletter
from pcapi.validation.routes.users import check_valid_signup_webapp


@private_api.route("/users/signup/webapp", methods=["POST"])
@feature_required(FeatureToggle.WEBAPP_SIGNUP)
def signup_webapp():
    objects_to_save = []
    check_valid_signup_webapp(request)

    new_user = UserSQLEntity(from_dict=request.json)

    if IS_INTEGRATION:
        new_user.departementCode = "00"
        objects_to_save.append(_create_initial_deposit(new_user))
    else:
        authorized_emails, departement_codes = get_authorized_emails_and_dept_codes()
        departement_code = _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes)
        new_user.departementCode = departement_code

    new_user.canBookFreeOffers = False
    new_user.isAdmin = False
    objects_to_save.append(new_user)

    repository.save(*objects_to_save)

    if request.json.get("contact_ok"):
        try:
            subscribe_newsletter(new_user)
        except MailServiceException as e:
            app.logger.exception("Mail service failure", e)

    return jsonify(as_dict(new_user, includes=BENEFICIARY_INCLUDES)), 201


def _create_initial_deposit(new_user):
    deposit = Deposit()
    deposit.amount = 499.99
    deposit.user = new_user
    deposit.source = "test"
    return deposit


def _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes):
    email_index = _get_email_index_in_spreadsheet_or_error(authorized_emails)
    departement_code = departement_codes[email_index]
    if departement_code.strip() == "":
        logger.exception("[ERROR] Missing departement code in users spreadsheet for " + request.json["email"])

        e = ApiErrors()
        e.add_error("email", "Adresse non autorisée pour l'expérimentation")
        raise e
    return departement_code


def _get_email_index_in_spreadsheet_or_error(authorized_emails):
    try:
        email_index = authorized_emails.index(request.json["email"])
    except ValueError:
        e = ApiErrors()
        e.add_error("email", "Adresse non autorisée pour l'expérimentation")
        raise e
    return email_index
