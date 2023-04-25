import random

from pcapi import settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from . import exceptions


def generate_user() -> users_models.User:
    if not settings.ENABLE_TEST_USER_GENERATION:
        raise exceptions.UserGenerationForbiddenException("Test user generation is disabled")
    random_umber = random.randint(0, 1000000)
    user = users_factories.UserFactory(email=f"user_{random_umber}@example.com", age=18)
    return user
