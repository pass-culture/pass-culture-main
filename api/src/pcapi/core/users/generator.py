import dataclasses

from pcapi import settings
import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from . import exceptions


@dataclasses.dataclass
class GenerateUserData:
    age: int
    id_provider: str
    is_beneficiary: bool
    step: subscription_models.SubscriptionStep | None = None


def generate_user(user_data: GenerateUserData) -> users_models.User:
    if not settings.ENABLE_TEST_USER_GENERATION:
        raise exceptions.UserGenerationForbiddenException("Test user generation is disabled")

    factory = users_factories.BaseUserFactory
    match user_data.step:
        case subscription_models.SubscriptionStep.EMAIL_VALIDATION:
            factory = users_factories.EmailValidatedUserFactory
        case subscription_models.SubscriptionStep.PHONE_VALIDATION:
            factory = users_factories.PhoneValidatedUserFactory
        case subscription_models.SubscriptionStep.PROFILE_COMPLETION:
            factory = users_factories.ProfileCompletedUserFactory
        case subscription_models.SubscriptionStep.IDENTITY_CHECK:
            factory = users_factories.IdentityValidatedUserFactory
        case subscription_models.SubscriptionStep.HONOR_STATEMENT:
            factory = users_factories.HonorStatementValidatedUserFactory

    if user_data.is_beneficiary:
        factory = users_factories.BeneficiaryFactory

    id_provider = fraud_models.FraudCheckType[user_data.id_provider]
    return factory(age=user_data.age, beneficiaryFraudChecks__type=id_provider)
