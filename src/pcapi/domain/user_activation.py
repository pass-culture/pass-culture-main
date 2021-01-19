from typing import Optional

from pcapi.core.payments import api as payments_api
from pcapi.core.users.models import User
from pcapi.domain.password import generate_reset_token
from pcapi.domain.password import random_password
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.scripts.beneficiary import THIRTY_DAYS_IN_HOURS


IMPORT_STATUS_MODIFICATION_RULE = (
    "Seuls les dossiers au statut DUPLICATE peuvent être modifiés (aux statuts REJECTED ou RETRY uniquement)"
)


def create_beneficiary_from_application(application_detail: dict, user: Optional[User] = None) -> User:
    if not user:
        beneficiary = User()
        beneficiary.password = random_password()
        beneficiary.email = application_detail["email"]
        beneficiary.dateOfBirth = application_detail["birth_date"]
    else:
        beneficiary = user

    beneficiary.lastName = application_detail["last_name"]
    beneficiary.firstName = application_detail["first_name"]
    beneficiary.publicName = "%s %s" % (application_detail["first_name"], application_detail["last_name"])
    beneficiary.phoneNumber = application_detail["phone"]
    beneficiary.departementCode = application_detail["department"]
    beneficiary.postalCode = application_detail["postal_code"]
    beneficiary.civility = application_detail["civility"]
    beneficiary.activity = application_detail["activity"]
    beneficiary.isAdmin = False
    beneficiary.hasSeenTutorials = False
    generate_reset_token(beneficiary, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    beneficiary.isBeneficiary = True
    application_id = application_detail["application_id"]
    deposit = payments_api.create_deposit(beneficiary, f"démarches simplifiées dossier [{application_id}]")
    beneficiary.deposits = [deposit]

    return beneficiary


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status in (ImportStatus.REJECTED, ImportStatus.RETRY):
            return True
    return False
