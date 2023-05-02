import dataclasses

from pcapi import settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from . import exceptions


@dataclasses.dataclass
class GenerateUserData:
    age: int
    is_email_validated: bool
    is_beneficiary: bool


def generate_user(user_data: GenerateUserData) -> users_models.User:
    if not settings.ENABLE_TEST_USER_GENERATION:
        raise exceptions.UserGenerationForbiddenException("Test user generation is disabled")

    if user_data.is_beneficiary:
        return users_factories.BeneficiaryFactory(age=user_data.age)

    return users_factories.BaseUserFactory(age=user_data.age, isEmailValidated=user_data.is_email_validated)
