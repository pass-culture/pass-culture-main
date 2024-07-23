from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import random
import string
import typing
import uuid

from dateutil.relativedelta import relativedelta
import factory
from factory import LazyAttribute
import time_machine

from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.factories import BaseFactory
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import utils as users_utils
import pcapi.core.users.constants as users_constants
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository
from pcapi.utils import crypto

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

    dateOfBirth = LazyAttribute(lambda o: date.today() - relativedelta(years=o.age))
    comment = LazyAttribute(lambda o: str(o.__dict__))
    isEmailValidated = False

    @classmethod
    def _create(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        kwargs.update(**cls._set_non_nullable_attributes(**kwargs))
        instance = super()._create(model_class, *args, **kwargs)
        cls.set_custom_attributes(instance, **kwargs)
        repository.save(instance)
        return instance

    @classmethod
    def _build(
        cls,
        model_class: type[models.User],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.User:
        kwargs.update(**cls._set_non_nullable_attributes(**kwargs))
        instance = super()._build(model_class, *args, **kwargs)
        cls.set_custom_attributes(instance, **kwargs)
        return instance

    @classmethod
    def _set_non_nullable_attributes(cls, **kwargs: typing.Any) -> dict:
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["clearTextPassword"] = password
        kwargs["password"] = crypto.hash_password(password)

        if "email" not in kwargs:
            kwargs["email"] = f"{uuid.uuid4()}@to_override.com"
        return kwargs

    @classmethod
    def set_custom_attributes(cls, obj: models.User, **kwargs: typing.Any) -> None:
        if obj.email.endswith("@to_override.com"):
            if obj.firstName and obj.lastName:
                obj.email = f"{obj.firstName}.{obj.lastName}.{obj.id}@passculture.gen".lower()
            else:
                obj.email = f"user.{obj.id}@passculture.gen"

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        return []

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
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
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        if obj.age == users_constants.ELIGIBILITY_AGE_18:
            obj.phoneNumber = f"+336{obj.id:08}"  # type: ignore[method-assign]
            obj.phoneValidationStatus = models.PhoneValidationStatusType.VALIDATED
            fraud_checks.append(fraud_factories.PhoneValidationFraudCheckFactory(user=obj))
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
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

    address = factory.Faker("street_address", locale="fr_FR")
    city = factory.Faker("city", locale="fr_FR")
    # locale is set to "en_UK" not to have accents, 'ç' or other french fantaisies
    # An easy way to generate email from names without any conversion
    firstName = factory.Faker("first_name", locale="en_UK")
    lastName = factory.Faker("last_name", locale="en_UK")
    postalCode = factory.LazyAttribute(lambda o: f"{random.randint(10, 959) * 100:05}")

    @classmethod
    def set_custom_attributes(cls, obj: models.User, **kwargs: typing.Any) -> None:
        super().set_custom_attributes(obj)
        if obj.address:
            obj.address = obj.address.replace(",", "")

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        fraud_checks.append(
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=obj,
                resultContent__address=obj.address,
                resultContent__city=obj.city,
                resultContent__firstName=obj.firstName,
                resultContent__lastName=obj.lastName,
                resultContent__postalCode=obj.postalCode,
            )
        )
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
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

    validatedBirthDate = LazyAttribute(lambda o: datetime.utcnow().date() - relativedelta(years=o.age))

    @classmethod
    def set_custom_attributes(cls, obj: models.User, **kwargs: typing.Any) -> None:
        super().set_custom_attributes(obj)
        obj.idPieceNumber = f"{obj.id:012}"

    @classmethod
    def beneficiary_fraud_checks(
        cls, obj: models.User, **kwargs: typing.Any
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        identity_check_type = kwargs.get("type", fraud_models.FraudCheckType.UBBLE)
        identity_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=identity_check_type,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_checks.append(identity_fraud_check)
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        return IdentityValidatedUserFactory.beneficiary_fraud_checks(obj, **kwargs)


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
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_checks = super().beneficiary_fraud_checks(obj, **kwargs)
        fraud_checks.append(fraud_factories.HonorStatementFraudCheckFactory(user=obj))
        return fraud_checks

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
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
    roles = factory.LazyAttribute(
        lambda o: (
            [models.UserRole.UNDERAGE_BENEFICIARY]
            if o.age in users_constants.ELIGIBILITY_UNDERAGE_RANGE
            else [models.UserRole.BENEFICIARY]
        )
    )

    @factory.post_generation
    def deposit(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(user=obj, **kwargs)


class Transition1718Factory(BeneficiaryFactory):
    roles = [models.UserRole.UNDERAGE_BENEFICIARY]

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> list[fraud_models.BeneficiaryFraudCheck]:
        if not create:
            return []

        with time_machine.travel(datetime.today() - relativedelta(years=1)):
            fraud_checks = Transition1718Factory.beneficiary_fraud_checks(obj, **kwargs)
        return fraud_checks

    @factory.post_generation
    def deposit(  # pylint: disable=no-self-argument
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

            deposit = DepositGrantFactory(user=obj, **kwargs)

        return deposit


####################################
# The legacy factories are below. #
####################################


class UserFactory(BaseFactory):
    class Meta:
        model = models.User

    class Params:
        age = 40

    email = factory.Sequence("jean.neige{}@example.com".format)
    address: str | None = factory.Sequence("{} place des noces rouges".format)
    city: str | None = "La Rochelle"
    dateOfBirth = LazyAttribute(lambda o: date.today() - relativedelta(years=o.age))
    firstName = "Jean"
    lastName = "Neige"
    isEmailValidated = True
    roles: list[models.UserRole] = []
    hasSeenProTutorials = True
    postalCode: str | None = factory.Faker("postcode")

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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


class BeneficiaryGrant18Factory(BaseFactory):
    class Meta:
        model = models.User

    email = factory.LazyFunction(lambda: f"jeanne.doux_{uuid.uuid4()}@example.com")
    address = factory.Sequence("{} rue des machines".format)
    city = "Paris"
    dateCreated = LazyAttribute(lambda _: datetime.utcnow())
    lastConnectionDate = LazyAttribute(lambda _: datetime.utcnow() - relativedelta(days=1))
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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @factory.post_generation
    def beneficiaryImports(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: BeneficiaryImport | None,
        **kwargs: typing.Any,
    ) -> BeneficiaryImport | None:
        if not create:
            return None

        if extracted is not None:
            return extracted

        beneficiary_import = BeneficiaryImportFactory(
            beneficiary=obj,
            source=(
                BeneficiaryImportSources.educonnect.value
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else BeneficiaryImportSources.ubble.value
            ),
            eligibilityType=obj.eligibility,
        )
        BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import, author=None)
        return beneficiary_import

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> fraud_models.BeneficiaryFraudCheck | None:
        import pcapi.core.fraud.factories as fraud_factories

        if not create:
            return None

        type_ = kwargs.get(
            "type",
            (
                fraud_models.FraudCheckType.EDUCONNECT
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else fraud_models.FraudCheckType.UBBLE
            ),
        )

        return fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            status=fraud_models.FraudCheckStatus.OK,
            type=type_,
            resultContent=(
                fraud_factories.EduconnectContentFactory(
                    first_name=obj.firstName,
                    last_name=obj.lastName,
                    birth_date=obj.dateOfBirth.date(),
                    ine_hash=obj.ineHash or "".join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                    registration_datetime=obj.dateCreated,
                )
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else fraud_factories.UbbleContentFactory(first_name=obj.firstName, last_name=obj.lastName)
            ),
            eligibilityType=(
                models.EligibilityType.UNDERAGE
                if obj.eligibility == models.EligibilityType.UNDERAGE
                else models.EligibilityType.AGE18
            ),
        )

    @factory.post_generation
    def deposit(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(user=obj, **kwargs)


def RichBeneficiaryFactory() -> models.User:
    # Create a rich beneficiary who can book expensive stocks. Useful
    # when we want to simulate a large amount of (booked) money
    # without having to create many bookings.
    user = BeneficiaryGrant18Factory()
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
    def deposit(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(user=obj, **kwargs, type=finance_models.DepositType.GRANT_15_17)


class ExUnderageBeneficiaryFactory(UnderageBeneficiaryFactory):
    class Params:
        subscription_age = 18

    dateCreated = LazyAttribute(
        lambda user: user.dateOfBirth + relativedelta(years=users_constants.ELIGIBILITY_AGE_18 - 1, hours=12)
    )

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> fraud_models.BeneficiaryFraudCheck | None:
        import pcapi.core.fraud.factories as fraud_factories

        if not create:
            return None

        return fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            dateCreated=obj.dateCreated,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name=obj.firstName,
                last_name=obj.lastName,
                birth_date=obj.dateOfBirth.date(),
                ine_hash=obj.ineHash or "".join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                registration_datetime=obj.dateCreated,
            ),
            eligibilityType=models.EligibilityType.UNDERAGE,
        )

    @factory.post_generation
    def deposit(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: finance_models.Deposit | None,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit | None:
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(
            user=obj,
            **kwargs,
            type=finance_models.DepositType.GRANT_15_17,
            expirationDate=obj.dateCreated + relativedelta(days=1),
        )


class ExUnderageBeneficiaryWithUbbleFactory(ExUnderageBeneficiaryFactory):
    class Params:
        subscription_age = 18

    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> fraud_models.BeneficiaryFraudCheck | None:
        import pcapi.core.fraud.factories as fraud_factories
        from pcapi.core.fraud.ubble import models as ubble_fraud_models

        if not create:
            return None

        return fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            dateCreated=obj.dateCreated,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
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
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> fraud_models.BeneficiaryFraudCheck | None:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=obj.firstName,
                last_name=obj.lastName,
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
        )
        obj.phoneValidationStatus = models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.AGE18,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=obj, eligibilityType=models.EligibilityType.AGE18)
        return None


class EligibleActivableUnderageFactory(EligibleUnderageFactory):
    @factory.post_generation
    def beneficiaryFraudChecks(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: fraud_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> None:
        import pcapi.core.fraud.factories as fraud_factories

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name=obj.firstName,
                last_name=obj.lastName,
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=models.EligibilityType.UNDERAGE,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=obj, eligibilityType=models.EligibilityType.UNDERAGE)


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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
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
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


class NonAttachedProFactory(ProFactory):
    class Meta:
        model = models.User

    roles = [models.UserRole.NON_ATTACHED_PRO]


class UserSessionFactory(BaseFactory):
    class Meta:
        model = models.UserSession

    uuid = factory.LazyFunction(uuid.uuid4)

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

    dateCreated = LazyAttribute(lambda _: datetime.utcnow())
    user = factory.SubFactory(UserFactory)  # BeneficiaryGrant18Factory is already creating a deposit
    source = "public"

    @classmethod
    def _create(
        cls,
        model_class: type[finance_models.Deposit],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> finance_models.Deposit:
        age = users_utils.get_age_from_birth_date(kwargs["user"].birth_date)
        eligibility = (
            models.EligibilityType.UNDERAGE
            if age in users_constants.ELIGIBILITY_UNDERAGE_RANGE
            else models.EligibilityType.AGE18
        )
        granted_deposit = finance_api.get_granted_deposit(kwargs["user"], eligibility, age_at_registration=age)
        assert granted_deposit is not None

        if "version" not in kwargs:
            kwargs["version"] = granted_deposit.version
        if "amount" not in kwargs:
            kwargs["amount"] = granted_deposit.amount
        if "expirationDate" not in kwargs:
            kwargs["expirationDate"] = granted_deposit.expiration_date
        if "type" not in kwargs:
            kwargs["type"] = granted_deposit.type
        return super()._create(model_class, *args, **kwargs)


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
    user_type = None
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
    eventType = models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value


class EmailConfirmationEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.CONFIRMATION.value


class NewEmailSelectionEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION.value


class EmailValidationEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.VALIDATION.value


class EmailAdminValidationEntryFactory(UserEmailHistoryFactory):
    eventType = models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION.value


class UserProFlagsFactory(BaseFactory):
    class Meta:
        model = models.UserProFlags

    user = factory.SubFactory(ProFactory)
    firebase = {"BETTER_OFFER_CREATION": "true"}


class UserProNewNavStateFactory(BaseFactory):
    class Meta:
        model = models.UserProNewNavState

    user = factory.SubFactory(ProFactory)
    eligibilityDate = LazyAttribute(lambda _: datetime.utcnow())
    newNavDate = LazyAttribute(lambda _: datetime.utcnow())


class GdprUserDataExtractBeneficiaryFactory(BaseFactory):
    class Meta:
        model = models.GdprUserDataExtract

    dateCreated = LazyAttribute(lambda _: datetime.utcnow() - timedelta(days=1))
    user = factory.SubFactory(BeneficiaryFactory)
    authorUser = factory.SubFactory(AdminFactory)
