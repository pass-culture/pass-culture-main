import dataclasses
import datetime
import decimal
import enum
import typing

import time_machine

import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.core.users.utils as users_utils
from pcapi import settings
from pcapi.core.users import constants as users_constants
from pcapi.utils import date as date_utils

from . import exceptions


class GeneratedIdProvider(enum.Enum):
    DMS = subscription_models.FraudCheckType.DMS
    EDUCONNECT = subscription_models.FraudCheckType.EDUCONNECT
    UBBLE = subscription_models.FraudCheckType.UBBLE


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
    age: int | None = None
    birth_date: datetime.date | None = None
    credit: decimal.Decimal | None = None
    id_provider: GeneratedIdProvider = GeneratedIdProvider.UBBLE
    step: GeneratedSubscriptionStep = GeneratedSubscriptionStep.EMAIL_VALIDATION
    date_created: datetime.datetime | None = None
    postal_code: str | None = None

    def get_age(self) -> int:
        if self.birth_date is not None:
            return users_utils.get_age_at_date(self.birth_date, datetime.datetime.now(tz=None))
        if self.age is not None:
            return self.age
        return 18

    def get_date_created(self) -> datetime.datetime:
        return date_utils.get_naive_utc_now() if self.date_created is None else self.date_created

    def get_activity(self) -> users_models.ActivityEnum:
        age = self.get_age()
        if age < 18:  # 15, 16, 17
            return users_models.ActivityEnum.HIGH_SCHOOL_STUDENT
        elif age < 20:  # 18, 19
            return users_models.ActivityEnum.STUDENT
        return users_models.ActivityEnum.APPRENTICE_STUDENT  # 20


def generate_user(user_data: GenerateUserData) -> users_models.User:
    if not settings.ENABLE_TEST_USER_GENERATION:
        generation_exception = exceptions.UserGenerationForbiddenException()
        generation_exception.add_error(
            "settings",
            "Test user generation is disabled",
        )
        raise generation_exception

    with time_machine.travel(user_data.get_date_created()):
        factory_kwargs: dict[str, typing.Any] = {}
        Factory = _get_user_factory(user_data)

        # ensure that postal code is set only for ProfileCompletedUserFactory or a factory that is a descendant of it
        if users_factories.ProfileCompletedUserFactory in Factory.mro() and user_data.postal_code:
            factory_kwargs["postalCode"] = user_data.postal_code
        if user_data.credit is not None:
            factory_kwargs["deposit__amount"] = user_data.credit
        if user_data.birth_date is not None:
            factory_kwargs["dateOfBirth"] = user_data.birth_date
        return Factory.create(
            age=user_data.get_age(),
            beneficiaryFraudChecks__type=user_data.id_provider.value,
            activity=user_data.get_activity().value,
            **factory_kwargs,
        )


def _get_user_factory(user_data: GenerateUserData) -> type[users_factories.BaseUserFactory]:
    Factory = users_factories.BaseUserFactory
    if user_data.get_age() in users_constants.ELIGIBILITY_FREE_RANGE:
        match user_data.step:
            case GeneratedSubscriptionStep.EMAIL_VALIDATION:
                Factory = users_factories.EmailValidatedUserFactory
            case GeneratedSubscriptionStep.PROFILE_COMPLETION:
                Factory = users_factories.ProfileCompletedUserFactory
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
