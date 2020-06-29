from typing import List
from datetime import datetime

from domain.beneficiary.beneficiary_pre_subscription import BeneficiaryPreSubscription
from models import Offerer, UserSQLEntity
from repository.user_queries import find_by_civility, find_user_by_email

class CantRegisterBeneficiary(Exception):
    pass

def get_beneficiary_duplicates(first_name: str, last_name: str, date_of_birth: datetime) -> List[UserSQLEntity]:
    return find_by_civility(first_name=first_name,
                            last_name=last_name,
                            date_of_birth=date_of_birth)

def _check_email_is_not_taken(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    email = beneficiary_pre_subscription.email

    if find_user_by_email(email):
        raise CantRegisterBeneficiary(f"Email {email} is already taken.")

def _check_not_a_duplicate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    duplicates = get_beneficiary_duplicates(first_name=beneficiary_pre_subscription.first_name,
                                              last_name=beneficiary_pre_subscription.last_name,
                                              date_of_birth=beneficiary_pre_subscription.date_of_birth)

    if duplicates:
        raise CantRegisterBeneficiary(f"User with id {duplicates[0].id} is a duplicate.")


def validate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    _check_email_is_not_taken(beneficiary_pre_subscription)
    _check_not_a_duplicate(beneficiary_pre_subscription)
