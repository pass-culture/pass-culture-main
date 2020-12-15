from pcapi import settings
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.utils.module_loading import import_string


def get_application_by_id(application_id: int) -> BeneficiaryPreSubscription:
    backend = import_string(settings.JOUVE_APPLICATION_BACKEND)
    return backend().get_application_by(application_id)
