from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from domain.password import generate_reset_token, random_password
from models.user_sql_entity import UserSQLEntity
from scripts.beneficiary import THIRTY_DAYS_IN_HOURS


def to_model(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> UserSQLEntity:
    beneficiary = UserSQLEntity()
    beneficiary.activity = beneficiary_pre_subscription.activity
    beneficiary.canBookFreeOffers = True
    beneficiary.civility = beneficiary_pre_subscription.civility
    beneficiary.dateOfBirth = beneficiary_pre_subscription.date_of_birth
    beneficiary.departementCode = beneficiary_pre_subscription.department_code
    beneficiary.email = beneficiary_pre_subscription.email
    beneficiary.firstName = beneficiary_pre_subscription.first_name
    beneficiary.hasSeenTutorials = False
    beneficiary.isAdmin = False
    beneficiary.lastName = beneficiary_pre_subscription.last_name
    beneficiary.password = random_password()
    beneficiary.phoneNumber = beneficiary_pre_subscription.phone_number
    beneficiary.postalCode = beneficiary_pre_subscription.postal_code
    beneficiary.publicName = beneficiary_pre_subscription.public_name
    generate_reset_token(beneficiary, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    return beneficiary
