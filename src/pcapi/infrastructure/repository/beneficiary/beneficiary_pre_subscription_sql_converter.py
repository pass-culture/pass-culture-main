from typing import Optional

from pcapi.core.users import api as users_api
from pcapi.core.users.api import fulfill_account_password
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImport
from pcapi.models import ImportStatus


def to_model(beneficiary_pre_subscription: BeneficiaryPreSubscription, user: Optional[User] = None) -> User:
    if not user:
        beneficiary = User()
        beneficiary.email = sanitize_email(beneficiary_pre_subscription.email)
        fulfill_account_password(beneficiary)
    else:
        beneficiary = user

    beneficiary.dateOfBirth = beneficiary_pre_subscription.date_of_birth or beneficiary.dateOfBirth
    beneficiary.activity = beneficiary_pre_subscription.activity
    beneficiary.address = beneficiary_pre_subscription.address
    beneficiary.city = beneficiary_pre_subscription.city
    beneficiary.civility = beneficiary_pre_subscription.civility
    beneficiary.departementCode = beneficiary_pre_subscription.department_code
    beneficiary.firstName = beneficiary_pre_subscription.first_name
    beneficiary.hasSeenTutorials = False
    beneficiary.isAdmin = False
    beneficiary.lastName = beneficiary_pre_subscription.last_name
    beneficiary.phoneNumber = beneficiary_pre_subscription.phone_number
    beneficiary.postalCode = beneficiary_pre_subscription.postal_code
    beneficiary.publicName = beneficiary_pre_subscription.public_name

    users_api.attach_beneficiary_import_details(beneficiary, beneficiary_pre_subscription)
    if not users_api.steps_to_become_beneficiary(beneficiary):
        beneficiary = users_api.activate_beneficiary(beneficiary, beneficiary_pre_subscription.deposit_source)

    return beneficiary


def to_rejected_model(
    beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str, user: Optional[User]
) -> BeneficiaryImport:
    beneficiary_import = BeneficiaryImport()

    beneficiary_import.applicationId = beneficiary_pre_subscription.application_id
    beneficiary_import.sourceId = beneficiary_pre_subscription.source_id
    beneficiary_import.source = beneficiary_pre_subscription.source
    beneficiary_import.setStatus(status=ImportStatus.REJECTED, detail=detail)

    if user:
        user.beneficiaryImports.append(beneficiary_import)

    return beneficiary_import
