from dataclasses import asdict
import logging

from flask import jsonify
from flask import request

from pcapi import settings
from pcapi.connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from pcapi.connectors.google_spreadsheet import get_ttl_hash
from pcapi.core.payments import api as payments_api
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import NotificationSubscriptions
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.flask_app import private_api
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict
from pcapi.utils.feature import feature_required
from pcapi.utils.includes import BENEFICIARY_INCLUDES


logger = logging.getLogger(__name__)
from pcapi.validation.routes.users import check_valid_signup_webapp


# @debt api-migration
@private_api.route("/users/signup/webapp", methods=["POST"])
@feature_required(FeatureToggle.WEBAPP_SIGNUP)
def signup_webapp():
    objects_to_save = []
    check_valid_signup_webapp(request)

    new_user = User(from_dict=request.json)
    new_user.email = sanitize_email(new_user.email)
    new_user.notificationSubscriptions = asdict(
        NotificationSubscriptions(marketing_email=bool(request.json.get("contact_ok")))
    )

    if settings.IS_INTEGRATION:
        objects_to_save.append(payments_api.create_deposit(new_user, "test"))
    else:
        authorized_emails, departement_codes = get_authorized_emails_and_dept_codes(ttl_hash=get_ttl_hash())
        departement_code = _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes)
        new_user.departementCode = departement_code

    new_user.remove_admin_role()
    new_user.remove_beneficiary_role()
    new_user.isEmailValidated = True
    new_user.needsToFillCulturalSurvey = False
    new_user.hasSeenTutorials = True
    objects_to_save.append(new_user)

    repository.save(*objects_to_save)

    update_external_user(new_user)

    return jsonify(as_dict(new_user, includes=BENEFICIARY_INCLUDES)), 201


def _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes):
    email_index = _get_email_index_in_spreadsheet_or_error(authorized_emails)
    departement_code = departement_codes[email_index]
    if departement_code.strip() == "":
        logger.exception("[ERROR] Missing departement code in users spreadsheet for %s", request.json["email"])

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
