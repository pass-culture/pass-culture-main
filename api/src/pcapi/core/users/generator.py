import dataclasses
import datetime
import enum

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.users import constants as users_constants

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

    if user_data.transition_17_18:
        user_data.age = 18

    Factory = _get_user_factory(user_data)
    return Factory.create(
        age=user_data.age,
        beneficiaryFraudChecks__type=user_data.id_provider.value,
        beneficiaryFraudChecks__dateCreated=user_data.date_created,
        dateCreated=user_data.date_created,
    )


def _get_user_factory(user_data: GenerateUserData) -> type[users_factories.BaseUserFactory]:
    if user_data.transition_17_18:
        return users_factories.Transition1718Factory

    Factory = users_factories.BaseUserFactory
    if user_data.age in users_constants.ELIGIBILITY_FREE_RANGE:
        match user_data.step:
            case GeneratedSubscriptionStep.EMAIL_VALIDATION:
                Factory = users_factories.EmailValidatedUserFactory
            case GeneratedSubscriptionStep.PROFILE_COMPLETION:
                Factory = users_factories.FreeBeneficiaryFactory
            case GeneratedSubscriptionStep.BENEFICIARY:
                Factory = users_factories.FreeBeneficiaryFactory
            case _:
                generation_exception = exceptions.InvalidSubscriptionStepException()
                generation_exception.add_error(
                    "step",
                    "Only EMAIL_VALIDATION, PROFILE_COMPLETION and BENEFICIARY are allowed steps for 15-16 users",
                )
                raise generation_exception
        return Factory

    match user_data.step:
        case GeneratedSubscriptionStep.EMAIL_VALIDATION:
            Factory = users_factories.EmailValidatedUserFactory
        case GeneratedSubscriptionStep.PHONE_VALIDATION:
            Factory = users_factories.PhoneValidatedUserFactory
        case GeneratedSubscriptionStep.PROFILE_COMPLETION:
            Factory = users_factories.ProfileCompletedUserFactory
        case GeneratedSubscriptionStep.IDENTITY_CHECK:
            Factory = users_factories.IdentityValidatedUserFactory
        case GeneratedSubscriptionStep.HONOR_STATEMENT:
            Factory = users_factories.HonorStatementValidatedUserFactory
        case GeneratedSubscriptionStep.BENEFICIARY:
            Factory = users_factories.BeneficiaryFactory

    return Factory
