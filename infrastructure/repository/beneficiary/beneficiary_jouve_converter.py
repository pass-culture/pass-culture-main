from typing import Dict

from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription


def to_domain(user_jouve_entity: Dict) -> BeneficiaryPreSubscription:
    return BeneficiaryPreSubscription(
        address=user_jouve_entity['mtd_adrResid'],
        birth_date=user_jouve_entity['mtd_datNaiss'],
        city=user_jouve_entity['mtd_comResid'],
        department_code=user_jouve_entity['mtd_codPos'],
        email=user_jouve_entity['mtd_mail'],
        first_name=user_jouve_entity['mtd_prenom'],
        gender=user_jouve_entity['mtd_sexe'],
        last_name=user_jouve_entity['mtd_nom'],
        phone_number=user_jouve_entity['mtd_tel'],
        status=user_jouve_entity['mtd_statut'],
    )
