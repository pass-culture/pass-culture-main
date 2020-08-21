from datetime import datetime
from typing import List

from domain.beneficiary_pre_subscription.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import \
    BeneficiaryIsADuplicate, BeneficiaryIsNotEligible
from models import UserSQLEntity
from repository.user_queries import find_by_civility, find_user_by_email


ELIGIBLE_DEPARTMENTS = [
    '08',
    '22',
    '25',
    '29',
    '34',
    '35',
    '56',
    '58',
    '67',
    '71',
    '84',
    '93',
    '94',
    '973',
]


def _is_postal_code_eligible(code: str) -> bool:
    for department in ELIGIBLE_DEPARTMENTS:
        if code.startswith(department):
            return True

    return False


def get_beneficiary_duplicates(first_name: str, last_name: str, date_of_birth: datetime) -> List[UserSQLEntity]:
    return find_by_civility(first_name=first_name,
                            last_name=last_name,
                            date_of_birth=date_of_birth)


def _check_email_is_not_taken(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    email = beneficiary_pre_subscription.email

    if find_user_by_email(email):
        raise BeneficiaryIsADuplicate(f"Email {email} is already taken.")


def _check_department_is_eligible(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    postal_code = beneficiary_pre_subscription.postal_code

    if not _is_postal_code_eligible(postal_code):
        raise BeneficiaryIsNotEligible(
            f"Postal code {postal_code} is not eligible.")


def _check_not_a_duplicate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    duplicates = get_beneficiary_duplicates(first_name=beneficiary_pre_subscription.first_name,
                                            last_name=beneficiary_pre_subscription.last_name,
                                            date_of_birth=beneficiary_pre_subscription.date_of_birth)

    if duplicates:
        raise BeneficiaryIsADuplicate(
            f"User with id {duplicates[0].id} is a duplicate.")


def validate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    _check_department_is_eligible(beneficiary_pre_subscription)
    _check_email_is_not_taken(beneficiary_pre_subscription)
    _check_not_a_duplicate(beneficiary_pre_subscription)
