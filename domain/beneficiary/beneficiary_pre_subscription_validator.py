from domain.beneficiary.beneficiary_pre_subscription import BeneficiaryPreSubscription
from repository.user_queries import find_by_civility, find_user_by_email

class CantRegisterBeneficiary(Exception):
    pass

def check_email_is_not_taken(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    email = beneficiary_pre_subscription.email

    if find_user_by_email(email):
        raise CantRegisterBeneficiary(f"Email {email} is already taken")


def check_not_a_dupplicate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    dupplicates = find_by_civility(first_name=beneficiary_pre_subscription.first_name,
                                   last_name=beneficiary_pre_subscription.last_name,
                                   birth_date=beneficiary_pre_subscription.date_of_birth)

    if dupplicates:
        raise CantRegisterBeneficiary(f"User with id {dupplicates[0].id} is a dupplicate")
