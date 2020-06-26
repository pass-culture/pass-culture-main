from datetime import datetime
from typing import Dict

from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from models import BeneficiaryImportSources


DEFAULT_JOUVE_SOURCE_ID = None

def to_domain(user_jouve_entity: Dict) -> BeneficiaryPreSubscription:
    return BeneficiaryPreSubscription(
        activity=user_jouve_entity['mtd_statut'],
        application_id=user_jouve_entity['mtd_jeuneID'],
        civility=_convert_civility(user_jouve_entity['mtd_sexe']),
        date_of_birth=_convert_date_of_birth(user_jouve_entity['mtd_datNaiss']),
        email=user_jouve_entity['mtd_mail'],
        first_name=user_jouve_entity['mtd_prenom'],
        last_name=user_jouve_entity['mtd_nom'],
        phone_number=user_jouve_entity['mtd_tel'],
        postal_code=user_jouve_entity['mtd_codPos'],
        source=BeneficiaryImportSources.jouve.value,
        source_id=DEFAULT_JOUVE_SOURCE_ID
    )


def _convert_date_of_birth(date: str) -> datetime:
    return datetime.strptime(date, '%d/%m/%Y')


def _convert_civility(raw_civility: str) -> str:
    return 'Mme' if raw_civility == 'F' else 'M.'
