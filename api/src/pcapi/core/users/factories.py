import base64
import random
import re
import string
import typing
import uuid
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

import factory
import time_machine
from dateutil.relativedelta import relativedelta
from factory import LazyAttribute
from factory import LazyFunction

import pcapi.core.finance.models as finance_models
import pcapi.core.users.constants as users_constants
from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.connectors.dms import models as dms_models
from pcapi.core.factories import BaseFactory
from pcapi.core.finance.conf import RECREDIT_TYPE_AGE_MAPPING
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.utils import crypto
from pcapi.utils import date as date_utils
from pcapi.utils import regions

from . import models


# This file is experiencing a renaissance. It's a good thing.
# Below are the factories that have been deemed correct.
# You will find the legacy ones at the bottom of the file, waiting to be improved or ruthlessly deleted.


class BaseUserFactory(BaseFactory):
    """
    Generates a user as if it were created by the account creation form.
    The user was asked for
    - email
    - password
    - date of birth
    """

    class Meta:
        model = models.User

    class Params:
        age = 40

    dateCreated = LazyFunction(date_utils.get_naive_utc_now)
    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine((o.dateCreated - relativedelta(years=o.age)).date(), time.min)
    )
    comment = LazyAttribute(lambda o: str(o.__dict__))
    isEmailValidated = False

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)

        if "email" not in kwargs:
            kwargs["email"] = f"{uuid.uuid4()}@to_override.com"
        instance = super()._create(model_class, *args, **kwargs)
        instance.setClearTextPassword(password)
        cls.set_custom_attributes(instance, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)

        if "email" not in kwargs:
            kwargs["email"] = f"{uuid.uuid4()}@to_override.com"
        instance = super()._build(model_class, *args, **kwargs)
        instance.setClearTextPassword(password)
        cls.set_custom_attributes(instance, **kwargs)
        return instance

    @classmethod
    def set_custom_attributes(cls, obj: models.User, **kwargs: typing.Any) -> None:
        if obj.email.endswith("@to_override.com"):
            clean_first_name = re.sub(r"\W+", "", obj.firstName or "")
            clean_last_name = re.sub(r"\W+", "", obj.lastName or "")
            if clean_first_name and clean_last_name:
                obj.email = f"{clean_first_name}.{clean_last_name}.{obj.id}@passculture.gen".lower()
            else:
                obj.email = f"user.{obj.id}@passculture.gen"

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        return []

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return BaseUserFactory.beneficiary_fraud_checks(obj, **kwargs)


class EmailValidatedUserFactory(BaseUserFactory):
    """
    On top of the base user form, the user went through
    - email validation
    """

    isEmailValidated = True


class PhoneValidatedUserFactory(EmailValidatedUserFactory):
    """
    On top of the base user form, the user went through
    - email validation
    - phone number validation (if user is at least 18yo)
    """

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        import pcapi.core.subscription.factories as subscription_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        if obj.age == users_constants.ELIGIBILITY_AGE_18:
            if not obj.phoneNumber:
                obj.phoneNumber = f"+336{obj.id:08}"
            obj.phoneValidationStatus = models.PhoneValidationStatusType.VALIDATED
            fraud_checks.append(
                subscription_factories.PhoneValidationFraudCheckFactory.create(
                    user=obj, dateCreated=kwargs.get("dateCreated", date_utils.get_naive_utc_now())
                )
            )
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return PhoneValidatedUserFactory.beneficiary_fraud_checks(obj, **kwargs)


class ProfileCompletedUserFactory(PhoneValidatedUserFactory):
    """
    On top of the base user form, the user went through
    - email validation
    - phone number validation
    - profile completion
    """

    hasSeenProTutorials = True
    hasSeenProRgs = True

    address: str | factory.declarations.BaseDeclaration = factory.Faker("street_address", locale="fr_FR")
    city: str | factory.declarations.BaseDeclaration = factory.Faker("city", locale="fr_FR")
    # locale is set to "en_UK" not to have accents, 'ç' or other french fantaisies
    # An easy way to generate email from names without any conversion
    firstName = factory.Faker("first_name", locale="en_UK")
    lastName = factory.Faker("last_name", locale="en_UK")
    postalCode: str | factory.declarations.BaseDeclaration = factory.LazyAttribute(
        lambda o: f"{random.randint(10, 959) * 100:05}"
    )
    departementCode: str | factory.declarations.BaseDeclaration = factory.LazyAttribute(
        lambda o: regions.get_department_code_from_city_code(o.postalCode) if o.postalCode else None
    )

    @classmethod
    def set_custom_attributes(cls, obj: models.User, **kwargs: typing.Any) -> None:
        super().set_custom_attributes(obj)
        if obj.address:
            obj.address = obj.address.replace(",", "")

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        import pcapi.core.subscription.factories as subscription_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        profile_completion_kwargs: dict = {"dateCreated": kwargs.get("dateCreated", date_utils.get_naive_utc_now())}
        if "eligibilityType" in kwargs:
            profile_completion_kwargs["eligibilityType"] = kwargs["eligibilityType"]
        fraud_checks.append(
            subscription_factories.ProfileCompletionFraudCheckFactory.create(
                user=obj,
                resultContent__address=obj.address,
                resultContent__city=obj.city,
                resultContent__firstName=obj.firstName,
                resultContent__lastName=obj.lastName,
                resultContent__postalCode=obj.postalCode,
                **profile_completion_kwargs,
            )
        )
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return ProfileCompletedUserFactory.beneficiary_fraud_checks(obj, **kwargs)


class IdentityValidatedUserFactory(ProfileCompletedUserFactory):
    """
    On top of the base user form, the user went through
    - email validation
    - phone number validation
    - profile completion
    - identity validation
    """

    validatedBirthDate = LazyAttribute(lambda o: o.dateCreated - relativedelta(years=o.age))

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        import pcapi.core.subscription.factories as subscription_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        if not kwargs.get("type"):
            kwargs["type"] = subscription_models.FraudCheckType.UBBLE
        identity_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj, status=subscription_models.FraudCheckStatus.OK, **kwargs
        )
        fraud_checks.append(identity_fraud_check)
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return IdentityValidatedUserFactory.beneficiary_fraud_checks(obj, **kwargs)

    @factory.post_generation
    def id_piece_number(
        obj: models.User,
        create: bool,
        extracted: str | None,
        **kwargs: typing.Any,
    ) -> None:
        if not create or not extracted:
            obj.idPieceNumber = f"{obj.id:012}"

        if extracted:
            obj.idPieceNumber = extracted


class HonorStatementValidatedUserFactory(IdentityValidatedUserFactory):
    """
    On top of the base user form, the user went through
    - email validation
    - phone number validation
    - profile completion
    - identity validation
    - honor statement
    """

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        import pcapi.core.subscription.factories as subscription_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        fraud_checks.append(
            subscription_factories.HonorStatementFraudCheckFactory.create(
                user=obj, dateCreated=kwargs.get("dateCreated", date_utils.get_naive_utc_now())
            )
        )
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return HonorStatementValidatedUserFactory.beneficiary_fraud_checks(obj, **kwargs)


class BeneficiaryFactory(HonorStatementValidatedUserFactory):
    """
    Generates a beneficiary as if it had finished the deposit activation process.
    On top of the base user form, the user went through
    - email validation
    - phone number validation
    - profile completion
    - identity validation
    - honor statement
    - deposit activation
    """

    class Params:
        age = 18

    # Deposit activation : see below with deposit function
    roles: list[models.UserRole] | factory.LazyAttribute = factory.LazyAttribute(
        lambda o: (
            [models.UserRole.UNDERAGE_BENEFICIARY]
            if o.age in users_constants.ELIGIBILITY_UNDERAGE_RANGE
            else [models.UserRole.BENEFICIARY]
        )
    )

    @factory.post_generation
    def deposit(
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory.create(user=obj, **kwargs)


class CaledonianBeneficiaryFactory(BeneficiaryFactory):
    address = factory.Sequence("{} place des Cocotiers".format)
    city = "Nouméa"
    postalCode = "98800"
    departementCode = "988"
    phoneNumber = factory.Sequence(lambda n: f"+68777{n % 10000:04}")


class Transition1718Factory(BeneficiaryFactory):
    roles = [models.UserRole.UNDERAGE_BENEFICIARY]

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[subscription_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        with time_machine.travel(datetime.today() - relativedelta(years=1)):
            fraud_checks = Transition1718Factory.beneficiary_fraud_checks(obj, **kwargs)
        return fraud_checks

    @factory.post_generation
    def deposit(
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        with time_machine.travel(datetime.today() - relativedelta(years=1)):
            if "dateCreated" not in kwargs:
                kwargs["dateCreated"] = obj.dateCreated

            if "expirationDate" not in kwargs:
                kwargs["expirationDate"] = datetime.today()

            deposit = DepositGrantFactory.create(user=obj, **kwargs)

        return deposit


class FreeBeneficiaryFactory(ProfileCompletedUserFactory):
    """
    Generates a free beneficiary as if it had finished the deposit activation process.
    On top of the base user form, the user went through
    - email validation
    - profile completion
    - free deposit activation
    """

    class Params:
        age = 16

    roles: list[models.UserRole] = [models.UserRole.FREE_BENEFICIARY]

    @factory.post_generation
    def deposit(
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory.create(user=obj, type=finance_models.DepositType.GRANT_FREE, amount=0, **kwargs)


####################################
# The legacy factories are below. #
####################################


class UserFactory(BaseFactory):
    class Meta:
        model = models.User

    class Params:
        age = 40

    email = factory.Sequence("jean.neige{}@example.com".format)
    address: str | factory.declarations.BaseDeclaration | None = factory.Sequence("{} place des noces rouges".format)
    city: str | None = "La Rochelle"
    dateOfBirth = LazyAttribute(lambda o: date.today() - relativedelta(years=o.age))
    firstName: str | factory.declarations.BaseDeclaration | None = "Jean"
    lastName: str | factory.declarations.BaseDeclaration | None = "Neige"
    isEmailValidated = True
    roles: list[models.UserRole] = []
    hasSeenProTutorials = True
    postalCode: str | factory.declarations.BaseDeclaration | None = factory.Faker("postcode")

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password) if password else None
        instance = super()._create(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance


class CaledonianUserFactory(UserFactory):
    address = factory.Sequence("{} route de la Corniche".format)
    city = "Le Mont-Dore"
    postalCode = "98809"
    departementCode = "988"
    phoneNumber = factory.Sequence(lambda n: f"+68777{n % 10000:04}")


class DiscordUserFactory(BaseFactory):
    class Meta:
        model = models.DiscordUser

    discordId = factory.Sequence("discord_{}".format)
    user = factory.SubFactory(UserFactory)
    hasAccess = True


class AnonymizedUserFactory(UserFactory):
    roles = [models.UserRole.ANONYMIZED]
    email = factory.Sequence("anonymous_{}@anonymized.passculture".format)
    address = None
    city = None
    postalCode = None
    dateOfBirth = LazyAttribute(lambda o: date(day=1, month=1, year=2023 - o.age))
    factory.Sequence("Anonymous_{}".format)
    firstName = factory.Sequence("Anonymous_{}".format)
    lastName = factory.Sequence("Anonymous_{}".format)


class BeneficiaryImportStatusFactory(BaseFactory):
    class Meta:
        model = BeneficiaryImportStatus

    status = ImportStatus.CREATED.value
    date = factory.Faker("date_time_between", start_date="-30d", end_date="-1d")
    detail = factory.Faker("sentence", nb_words=3)
    beneficiaryImport = factory.SubFactory("pcapi.core.users.factories.BeneficiaryImportFactory")
    author = factory.SubFactory("pcapi.core.users.factories.UserFactory")


class BeneficiaryImportFactory(BaseFactory):
    class Meta:
        model = BeneficiaryImport

    applicationId = factory.Sequence(lambda n: n)
    beneficiary = factory.SubFactory("pcapi.core.users.factories.UserFactory")
    source = BeneficiaryImportSources.ubble.value


class AdminFactory(BaseFactory):
    class Meta:
        model = models.User

    email = factory.Sequence("un.admin{}@example.com".format)
    address = factory.Sequence("{} rue des détectives".format)
    city = "Bordeaux"
    departementCode = "33"
    firstName = "Frank"
    lastName = "Columbo"
    isEmailValidated = True
    roles = [models.UserRole.ADMIN]
    hasSeenProTutorials = True
    backoffice_profile = factory.RelatedFactory(
        "pcapi.core.permissions.factories.BackOfficeUserProfileFactory", factory_related_name="user"
    )

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance


class BeneficiaryGrant18Factory(BaseFactory):
    class Meta:
        model = models.User

    email = factory.LazyFunction(lambda: f"jeanne.doux_{uuid.uuid4()}@example.com")
    address = factory.Sequence("{} rue des machines".format)
    city = "Paris"
    dateCreated = LazyAttribute(lambda _: date_utils.get_naive_utc_now())
    lastConnectionDate = LazyAttribute(lambda _: date_utils.get_naive_utc_now() - relativedelta(days=1))
    dateOfBirth = LazyAttribute(  # LazyAttribute to allow freez_time overrides
        lambda _: datetime.combine(date.today(), time(0, 0))
        - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, months=1)
    )
    firstName = "Jeanne"
    lastName = "Doux"
    isEmailValidated = True
    roles = [models.UserRole.BENEFICIARY]
    hasSeenProTutorials = True
    hasSeenProRgs = False

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        if "validatedBirthDate" not in kwargs:
            kwargs["validatedBirthDate"] = kwargs["dateOfBirth"]
        instance = super()._create(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance

    @factory.post_generation
    def beneficiaryImports(
        obj: models.User,
        create: bool,
        extracted: BeneficiaryImport | None,
        **kwargs: typing.Any,
    ) -> BeneficiaryImport | None:
        if not create:
            return None

        if extracted is not None:
            return extracted

        beneficiary_import = BeneficiaryImportFactory.create(
            beneficiary=obj,
            source=(
                BeneficiaryImportSources.educonnect.value
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else BeneficiaryImportSources.ubble.value
            ),
            eligibilityType=obj.eligibility,
        )
        BeneficiaryImportStatusFactory.create(beneficiaryImport=beneficiary_import, author=None)
        return beneficiary_import

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck | None:
        import pcapi.core.subscription.factories as subscription_factories

        if not create:
            return None

        type_ = kwargs.get(
            "type",
            (
                subscription_models.FraudCheckType.EDUCONNECT
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else subscription_models.FraudCheckType.UBBLE
            ),
        )

        assert obj.dateOfBirth  # helps mypy

        return subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            status=subscription_models.FraudCheckStatus.OK,
            type=type_,
            resultContent=(
                subscription_factories.EduconnectContentFactory.create(
                    first_name=obj.firstName,
                    last_name=obj.lastName,
                    birth_date=obj.dateOfBirth.date(),
                    ine_hash=obj.ineHash or "".join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                    registration_datetime=obj.dateCreated,
                )
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else subscription_factories.UbbleContentFactory.create(first_name=obj.firstName, last_name=obj.lastName)
            ),
            eligibilityType=obj.eligibility,
        )

    @factory.post_generation
    def deposit(
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory.create(user=obj, **kwargs)


def RichBeneficiaryFactory() -> models.User:
    # Create a rich beneficiary who can book expensive stocks. Useful
    # when we want to simulate a large amount of (booked) money
    # without having to create many bookings.
    user = BeneficiaryGrant18Factory.create()
    user.deposits[0].amount = 100_000
    db.session.add(user.deposits[0])
    db.session.commit()
    return user


class UnderageBeneficiaryFactory(BeneficiaryGrant18Factory):
    class Params:
        subscription_age = 15

    roles = [models.UserRole.UNDERAGE_BENEFICIARY]
    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine(date.today(), time(0, 0)) - relativedelta(years=o.subscription_age, months=5)
    )
    dateCreated = LazyAttribute(lambda user: user.dateOfBirth + relativedelta(years=user.subscription_age, hours=12))
    ineHash = factory.Sequence(lambda _: "".join(random.choices(string.ascii_lowercase + string.digits, k=32)))

    @factory.post_generation
    def deposit(
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory.create(user=obj, **kwargs, type=finance_models.DepositType.GRANT_15_17)


class CaledonianUnderageBeneficiaryFactory(UnderageBeneficiaryFactory):
    address = factory.Sequence("{} route du Mont Mou".format)
    city = "Païta"
    postalCode = "98889"
    departementCode = "988"
    phoneNumber = factory.Sequence(lambda n: f"+68777{n % 10000:04}")


class ExUnderageBeneficiaryFactory(UnderageBeneficiaryFactory):
    class Params:
        subscription_age = 18

    dateCreated = LazyAttribute(
        lambda user: user.dateOfBirth + relativedelta(years=users_constants.ELIGIBILITY_AGE_18 - 1, hours=12)
    )

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck | None:
        import pcapi.core.subscription.factories as subscription_factories

        if not create:
            return None

        assert obj.dateOfBirth  # helps mypy

        return subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            dateCreated=obj.dateCreated,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            resultContent=subscription_factories.EduconnectContentFactory.create(
                first_name=obj.firstName,
                last_name=obj.lastName,
                birth_date=obj.dateOfBirth.date(),
                ine_hash=obj.ineHash or "".join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                registration_datetime=obj.dateCreated,
            ),
            eligibilityType=models.EligibilityType.UNDERAGE,
        )

    @factory.post_generation
    def deposit(
        obj: models.User,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory.create(
            user=obj,
            type=finance_models.DepositType.GRANT_15_17,
            expirationDate=obj.dateCreated + relativedelta(days=1),
            **kwargs,
        )


class ExUnderageBeneficiaryWithUbbleFactory(ExUnderageBeneficiaryFactory):
    class Params:
        subscription_age = 18

    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck | None:
        import pcapi.core.subscription.factories as subscription_factories

        if not create:
            return None

        assert obj.dateOfBirth  # helps mypy

        return subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            dateCreated=obj.dateCreated,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=subscription_factories.UbbleContentFactory.create(
                status=ubble_schemas.UbbleIdentificationStatus.PROCESSED,
                first_name=obj.firstName,
                last_name=obj.lastName,
                birth_date=obj.dateOfBirth.date().isoformat(),
                registration_datetime=obj.dateCreated,
            ),
            eligibilityType=models.EligibilityType.UNDERAGE,
        )


class EligibleGrant18Factory(UserFactory):
    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine(date.today(), time(0, 0)) - relativedelta(years=18, months=5)
    )


class EligibleUnderageFactory(UserFactory):
    class Params:
        age = 15

    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine(date.today(), time(0, 0)) - relativedelta(years=o.age, months=5)
    )


class EligibleActivableFactory(EligibleGrant18Factory):
    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> None:
        import pcapi.core.subscription.factories as subscription_factories

        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
            resultContent=subscription_factories.UbbleContentFactory.create(
                first_name=obj.firstName,
                last_name=obj.lastName,
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
        )
        obj.phoneValidationStatus = models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory.create(
            user=obj, eligibilityType=models.EligibilityType.AGE18
        )


class EligibleActivableUnderageFactory(EligibleUnderageFactory):
    @factory.post_generation
    def beneficiaryFraudChecks(
        obj: models.User,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> None:
        import pcapi.core.subscription.factories as subscription_factories

        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.EduconnectContentFactory.create(
                first_name=obj.firstName,
                last_name=obj.lastName,
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=obj,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.UNDERAGE,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory.create(
            user=obj, eligibilityType=models.EligibilityType.UNDERAGE
        )


class ProFactory(BaseFactory):
    class Meta:
        model = models.User
        sqlalchemy_get_or_create = ["email"]

    email = factory.Sequence("ma.librairie{}@example.com".format)
    address = factory.Sequence("{} rue des cinémas".format)
    city = "Toulouse"
    departementCode = "31"
    firstName = "René"
    lastName = "Coty"
    isEmailValidated = True
    roles = [models.UserRole.PRO]
    hasSeenProTutorials = True

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.setClearTextPassword(settings.TEST_DEFAULT_PASSWORD)
        return instance


class NonAttachedProFactory(ProFactory):
    class Meta:
        model = models.User

    roles = [models.UserRole.NON_ATTACHED_PRO]


class UserSessionFactory(BaseFactory):
    class Meta:
        model = models.UserSession

    uuid = factory.LazyFunction(uuid.uuid4)
    expirationDatetime = factory.LazyFunction(lambda: datetime.now() + timedelta(days=1))

    @classmethod
    def _create(
        cls,
        model_class: type[models.UserSession],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.UserSession:
        try:
            user = kwargs.pop("user")
        except KeyError:
            raise ValueError('UserSessionFactory requires a "user" argument.')
        kwargs["userId"] = user.id
        return super()._create(model_class, *args, **kwargs)


class FavoriteFactory(BaseFactory):
    class Meta:
        model = models.Favorite

    offer = factory.SubFactory("pcapi.core.offers.factories.OfferFactory")
    user = factory.SubFactory(UserFactory)


# DepositFactory in users module to avoid import loops
class DepositGrantFactory(BaseFactory):
    class Meta:
        model = finance_models.Deposit

    dateCreated = LazyAttribute(lambda _: date_utils.get_naive_utc_now())
    source = "factory"
    user = factory.SubFactory(UserFactory)

    @classmethod
    def _create(
        cls,
        model_class: type[finance_models.Deposit],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit:
        user = kwargs["user"]
        age = users_utils.get_age_from_birth_date(user.birth_date)

        if age not in users_constants.ELIGIBILITY_UNDERAGE_RANGE + [users_constants.ELIGIBILITY_AGE_18]:
            age = 18  # The calling functions are responsible for setting the correct age. If age is not in the range, we generate a deposit for 18yo.

        if "type" not in kwargs:
            date_created = kwargs.get("dateCreated", date_utils.get_naive_utc_now())
            if date_created >= settings.CREDIT_V3_DECREE_DATETIME:
                kwargs["type"] = finance_models.DepositType.GRANT_17_18
            else:
                kwargs["type"] = (
                    finance_models.DepositType.GRANT_15_17
                    if age in users_constants.ELIGIBILITY_UNDERAGE_RANGE
                    else finance_models.DepositType.GRANT_18
                )
        if "amount" not in kwargs:
            if kwargs["type"] == finance_models.DepositType.GRANT_17_18:
                amount = {17: Decimal(50), 18: Decimal(150)}.get(age, Decimal(150))
            else:
                amount = {15: Decimal(20), 16: Decimal(30), 17: Decimal(30), 18: Decimal(300)}.get(age, Decimal(300))
            kwargs["amount"] = amount
        if "expirationDate" not in kwargs:
            kwargs["expirationDate"] = user.birth_date + relativedelta(years=21)
        if "version" not in kwargs:
            kwargs["version"] = 2 if kwargs["type"] == finance_models.DepositType.GRANT_18 else 1

        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def recredits(
        obj: finance_models.Deposit,
        create: bool,
        extracted: finance_models.Recredit | None,
        **kwargs: typing.Any,
    ) -> list[finance_models.Recredit]:
        from pcapi.core.finance.factories import RecreditFactory

        if not create:
            return []
        if getattr(obj, "recredits", None):
            # do not create new recredits if they already exist
            return getattr(obj, "recredits", [])
        # Immediately create the recredit that gives the first credit to the user
        user = obj.user
        if not user.age:
            return []

        if obj.type in (
            finance_models.DepositType.GRANT_15_17,
            finance_models.DepositType.GRANT_18,
            finance_models.DepositType.GRANT_FREE,
        ):
            return []

        # Immediately create the recredit that gives the first credit to the user.
        # Only for deposits of type GRANT_17_18 for now
        immediate_recredit = RecreditFactory.create(
            deposit=obj,
            amount=obj.amount,
            recreditType=RECREDIT_TYPE_AGE_MAPPING.get(user.age, finance_models.RecreditType.RECREDIT_18),
            dateCreated=obj.dateCreated,
        )

        return [immediate_recredit]


class EduconnectUserFactory(factory.Factory):
    class Meta:
        model = educonnect_models.EduconnectUser

    class Params:
        age = 15

    connection_datetime = LazyAttribute(lambda _: date.today() - relativedelta(days=1))
    birth_date = factory.LazyAttribute(lambda o: date.today() - relativedelta(years=o.age, months=1))
    educonnect_id = "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
    last_name = factory.Faker("last_name")
    first_name = factory.Faker("first_name")
    civility = models.GenderEnum.F
    logout_url = "https://educonnect.education.gouv.fr/Logout"
    user_type: str | None = None
    saml_request_id = factory.Faker("lexify", text="id-?????????????????")
    ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
    student_level = "2212"
    school_uai = "0910620E"


class TrustedDeviceFactory(BaseFactory):
    class Meta:
        model = models.TrustedDevice

    user = factory.SubFactory(UserFactory)
    deviceId = factory.LazyFunction(lambda: str(uuid.uuid4()).upper())
    os = "iOS"
    source = "iPhone 13"


class LoginDeviceHistoryFactory(BaseFactory):
    class Meta:
        model = models.LoginDeviceHistory

    user = factory.SubFactory(UserFactory)
    deviceId = factory.LazyFunction(lambda: str(uuid.uuid4()).upper())
    os = "iOS"
    source = "iPhone 13"
    location = "Paris"


class SingleSignOnFactory(BaseFactory):
    class Meta:
        model = models.SingleSignOn

    user = factory.SubFactory(UserFactory)
    ssoProvider = "google"
    ssoUserId = factory.Sequence("{}".format)


class UserEmailHistoryFactory(BaseFactory):
    class Meta:
        model = models.UserEmailHistory
        abstract = True

    user = factory.SubFactory(UserFactory)
    oldUserEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[0])
    oldDomainEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[1])
    newUserEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[0])
    newDomainEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[1] + ".update")


class EmailUpdateEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.UPDATE_REQUEST


class EmailConfirmationEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.CONFIRMATION


class NewEmailSelectionEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION


class EmailValidationEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.VALIDATION


class EmailAdminUpdateEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.ADMIN_UPDATE


class UserAccountUpdateRequestFactory(BaseFactory):
    class Meta:
        model = models.UserAccountUpdateRequest

    dsApplicationId = factory.Sequence(lambda n: 1230000 + n + 1)
    dsTechnicalId = factory.LazyAttribute(
        lambda o: (base64.urlsafe_b64encode(bytearray(f"UAUR:{o.dsApplicationId}", "utf-8"))).decode("utf-8")
    )
    status = dms_models.GraphQLApplicationStates.on_going
    firstName = "Jeune"
    lastName = "Demandeur"
    email = factory.Sequence(lambda n: f"demandeur_{n + 1}@example.com")
    birthDate = factory.Sequence(lambda n: date.today() - timedelta(days=18 * 366 + 10 * n))
    user = factory.SubFactory(
        BeneficiaryFactory,
        firstName=factory.SelfAttribute("..firstName"),
        lastName=factory.SelfAttribute("..lastName"),
        email=factory.SelfAttribute("..email"),
        dateOfBirth=factory.SelfAttribute("..birthDate"),
    )
    updateTypes: list[models.UserAccountUpdateType] = []
    oldEmail: str | factory.declarations.BaseDeclaration | None = None
    newEmail: str | factory.declarations.BaseDeclaration | None = None
    newPhoneNumber: str | None = None
    newFirstName: str | None = None
    newLastName: str | None = None
    allConditionsChecked = True
    lastInstructor = factory.SubFactory(
        AdminFactory,
        firstName="Instructeur",
        lastName="du Backoffice",
    )
    dateLastUserMessage = LazyAttribute(lambda _: date_utils.get_naive_utc_now() - relativedelta(days=1))
    dateLastInstructorMessage: factory.declarations.BaseDeclaration | None = factory.LazyAttribute(
        lambda _: date_utils.get_naive_utc_now() - relativedelta(days=3)
    )


class EmailUpdateRequestFactory(UserAccountUpdateRequestFactory):
    lastName = "Changeant d'Email"
    updateTypes = [models.UserAccountUpdateType.EMAIL]
    oldEmail = factory.Sequence(lambda n: f"ancien_email_{n + 1}@example.com")
    newEmail = factory.Sequence(lambda n: f"nouvel_email_{n + 1}@example.com")


class PhoneNumberUpdateRequestFactory(UserAccountUpdateRequestFactory):
    updateTypes = [models.UserAccountUpdateType.PHONE_NUMBER]
    newPhoneNumber = "+33730405060"


class FirstNameUpdateRequestFactory(UserAccountUpdateRequestFactory):
    updateTypes = [models.UserAccountUpdateType.FIRST_NAME]
    newFirstName = "Nouveau-Prénom"


class LastNameUpdateRequestFactory(UserAccountUpdateRequestFactory):
    updateTypes = [models.UserAccountUpdateType.LAST_NAME]
    newLastName = "Nouveau-Nom"


class LostCredentialsUpdateRequestFactory(UserAccountUpdateRequestFactory):
    lastName = "Perdu"
    updateTypes = [models.UserAccountUpdateType.LOST_CREDENTIALS]
    newEmail = factory.Sequence(lambda n: f"email_retrouve_{n + 1}@example.com")
    dateLastInstructorMessage = None


class GdprUserDataExtractBeneficiaryFactory(BaseFactory):
    class Meta:
        model = models.GdprUserDataExtract

    dateCreated = LazyAttribute(lambda _: date_utils.get_naive_utc_now() - timedelta(days=1))
    user = factory.SubFactory(BeneficiaryFactory)
    authorUser = factory.SubFactory(AdminFactory)


class GdprUserAnonymizationFactory(BaseFactory):
    class Meta:
        model = models.GdprUserAnonymization

    dateCreated = LazyAttribute(lambda _: date_utils.get_naive_utc_now() - timedelta(days=1))
    user = factory.SubFactory(BeneficiaryFactory)


class UserTagFactory(BaseFactory):
    class Meta:
        model = models.UserTag

    name = factory.Sequence("UserTag_{}".format)


class UserTagCategoryFactory(BaseFactory):
    class Meta:
        model = models.UserTagCategory

    name = factory.Sequence("user-tag-category-{}".format)


class UserTagCategoryMappingFactory(BaseFactory):
    class Meta:
        model = models.UserTagCategoryMapping


class UserProfileRefreshCampaignFactory(BaseFactory):
    campaignDate = factory.Faker("future_datetime")

    class Meta:
        model = models.UserProfileRefreshCampaign
