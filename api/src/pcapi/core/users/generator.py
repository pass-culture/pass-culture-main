import dataclasses
import datetime
import enum

from pcapi import settings
import pcapi.core.fraud.models as fraud_models
from pcapi.core.users import constants as users_constants
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from . import exceptions


class GeneratedIdProvider(enum.Enum):
    DMS = fraud_models.FraudCheckType.DMS
    EDUCONNECT = fraud_models.FraudCheckType.EDUCONNECT
    UBBLE = fraud_models.FraudCheckType.UBBLE


class GeneratedSubscriptionStep(enum.Enum):
    EMAIL_VALIDATION = "email-validation"
    PHONE_VALIDATION = "phone-validation"
    PROFILE_COMPLETION = "profile-completion"
    IDENTITY_CHECK = "identity-check"
    MAINTENANCE = "maintenance"
    HONOR_STATEMENT = "honor-statement"
    BENEFICIARY = "beneficiary"


@dataclasses.dataclass
class GenerateUserData:
    age: int = users_constants.ELIGIBILITY_AGE_18
    id_provider: GeneratedIdProvider = GeneratedIdProvider.UBBLE
    step: GeneratedSubscriptionStep = GeneratedSubscriptionStep.EMAIL_VALIDATION
    transition_17_18: bool = False
    date_created: datetime.datetime = datetime.datetime.utcnow()


def generate_user(user_data: GenerateUserData) -> users_models.User:
    if not settings.ENABLE_TEST_USER_GENERATION:
        generation_exception = exceptions.UserGenerationForbiddenException()
        generation_exception.add_error(
            "settings",
            "Test user generation is disabled",
        )
        raise generation_exception

    factory = users_factories.BaseUserFactory
    match user_data.step:
        case GeneratedSubscriptionStep.EMAIL_VALIDATION:
            factory = users_factories.EmailValidatedUserFactory
        case GeneratedSubscriptionStep.PHONE_VALIDATION:
            factory = users_factories.PhoneValidatedUserFactory
        case GeneratedSubscriptionStep.PROFILE_COMPLETION:
            factory = users_factories.ProfileCompletedUserFactory
        case GeneratedSubscriptionStep.IDENTITY_CHECK:
            factory = users_factories.IdentityValidatedUserFactory
        case GeneratedSubscriptionStep.HONOR_STATEMENT:
            factory = users_factories.HonorStatementValidatedUserFactory
        case GeneratedSubscriptionStep.BENEFICIARY:
            factory = users_factories.BeneficiaryFactory

    if user_data.transition_17_18:
        user_data.age = 18
        factory = users_factories.Transition1718Factory

    id_provider = user_data.id_provider.value
    return factory.create(
        age=user_data.age,
        beneficiaryFraudChecks__type=id_provider,
        beneficiaryFraudChecks__dateCreated=user_data.date_created,
        dateCreated=user_data.date_created,
    )
