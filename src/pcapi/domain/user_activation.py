from typing import Optional

import pcapi.core.fraud.models as fraud_models
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.password import random_hashed_password
from pcapi.models.beneficiary_import_status import ImportStatus


IMPORT_STATUS_MODIFICATION_RULE = (
    "Seuls les dossiers au statut DUPLICATE peuvent être modifiés (aux statuts REJECTED ou RETRY uniquement)"
)


def create_beneficiary_from_application(
    application_detail: fraud_models.DMSContent, user: Optional[User] = None
) -> User:
    if not user:
        beneficiary = User()
        beneficiary.password = random_hashed_password()
        beneficiary.email = sanitize_email(application_detail.email)
        beneficiary.dateOfBirth = application_detail.birth_date
    else:
        beneficiary = user

    beneficiary.lastName = application_detail.last_name
    beneficiary.firstName = application_detail.first_name
    beneficiary.publicName = "%s %s" % (application_detail.first_name, application_detail.last_name)
    beneficiary.departementCode = application_detail.department
    beneficiary.postalCode = application_detail.postal_code
    beneficiary.address = application_detail.address
    beneficiary.civility = application_detail.civility
    beneficiary.activity = application_detail.activity
    beneficiary.remove_admin_role()
    beneficiary.hasSeenTutorials = False
    beneficiary.idPieceNumber = application_detail.id_piece_number

    if not beneficiary.phoneNumber:
        beneficiary.phoneNumber = application_detail.phone

    return beneficiary


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status in (ImportStatus.REJECTED, ImportStatus.RETRY):
            return True
    return False
