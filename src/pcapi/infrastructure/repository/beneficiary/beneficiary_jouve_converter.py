from datetime import datetime
from typing import Dict

from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImportSources


DEFAULT_JOUVE_SOURCE_ID = None


def to_domain(user_jouve_entity: Dict) -> BeneficiaryPreSubscription:
    return BeneficiaryPreSubscription(
        activity=user_jouve_entity["activity"],
        address=user_jouve_entity["address"],
        application_id=user_jouve_entity["id"],
        city=user_jouve_entity["city"],
        civility=_convert_civility(user_jouve_entity["gender"]),
        date_of_birth=_convert_date_of_birth(user_jouve_entity["birthDate"]),
        email=user_jouve_entity["email"],
        first_name=user_jouve_entity["firstName"],
        last_name=user_jouve_entity["lastName"],
        phone_number=user_jouve_entity["phoneNumber"],
        postal_code=user_jouve_entity["postalCode"],
        source=BeneficiaryImportSources.jouve.value,
        source_id=DEFAULT_JOUVE_SOURCE_ID,
    )


def _convert_date_of_birth(date: str) -> datetime:
    return datetime.strptime(date, "%m/%d/%Y")
    # return datetime.strptime(date, '%d/%m/%Y') #A corriger, Jouve devrait renvoyer ce format la


def _convert_civility(raw_civility: str) -> str:
    return "Mme" if raw_civility == "F" else "M."
