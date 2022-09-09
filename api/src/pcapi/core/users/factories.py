from datetime import date
from datetime import datetime
from datetime import time
import random
import string
import uuid

from dateutil.relativedelta import relativedelta
import factory
from factory.declarations import LazyAttribute

from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.fraud import models as fraud_models
import pcapi.core.payments.api as payments_api
import pcapi.core.payments.models as payments_models
from pcapi.core.testing import BaseFactory
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
import pcapi.core.users.constants as users_constants
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.utils import crypto

from . import constants
from . import models


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


class UserFactory(BaseFactory):
    class Meta:
        model = users_models.User

    email = factory.Sequence("jean.neige{}@example.com".format)
    address = factory.Sequence("{} place des noces rouges".format)
    city = "La Rochelle"
    dateOfBirth = datetime.combine(date(1980, 1, 1), time(0, 0))
    firstName = "Jean"
    lastName = "Neige"
    publicName = "Jean Neige"
    isEmailValidated = True
    roles = []  # type: ignore [var-annotated]
    hasSeenProTutorials = True
    postalCode = factory.Faker("postcode")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


class AdminFactory(BaseFactory):
    class Meta:
        model = users_models.User

    email = factory.Sequence("un.admin{}@example.com".format)
    address = factory.Sequence("{} rue des détectives".format)
    city = "Bordeaux"
    departementCode = "33"
    firstName = "Frank"
    lastName = "Columbo"
    publicName = "Frank Columbo"
    isEmailValidated = True
    roles = [users_models.UserRole.ADMIN]
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


class BeneficiaryGrant18Factory(BaseFactory):
    class Meta:
        model = users_models.User

    email = factory.Sequence("jeanne.doux{}@example.com".format)
    address = factory.Sequence("{} rue des machines".format)
    city = "Paris"
    dateCreated = LazyAttribute(lambda _: datetime.utcnow())
    dateOfBirth = LazyAttribute(  # LazyAttribute to allow freez_time overrides
        lambda _: datetime.combine(date.today(), time(0, 0))
        - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, months=1)
    )
    firstName = "Jeanne"
    lastName = "Doux"
    isEmailValidated = True
    roles = [users_models.UserRole.BENEFICIARY]
    hasSeenProTutorials = True
    hasSeenProRgs = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        if "publicName" not in kwargs and kwargs["firstName"] and kwargs["lastName"]:
            kwargs["publicName"] = "%s %s" % (kwargs["firstName"], kwargs["lastName"])
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        if "publicName" not in kwargs and kwargs["firstName"] and kwargs["lastName"]:
            kwargs["publicName"] = "%s %s" % (kwargs["firstName"], kwargs["lastName"])
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @factory.post_generation
    def beneficiaryImports(obj, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not create:
            return None

        if extracted is not None:
            return extracted

        beneficiary_import = BeneficiaryImportFactory(
            beneficiary=obj,
            source=BeneficiaryImportSources.educonnect.value
            if obj.eligibility == users_models.EligibilityType.UNDERAGE
            else BeneficiaryImportSources.ubble.value,
            eligibilityType=obj.eligibility,
        )
        BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import, author=None)
        return beneficiary_import

    @factory.post_generation
    def beneficiaryFraudChecks(obj, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        import pcapi.core.fraud.factories as fraud_factories

        if not create:
            return None

        type_ = kwargs.get(
            "type",
            (
                fraud_models.FraudCheckType.EDUCONNECT
                if obj.eligibility == users_models.EligibilityType.UNDERAGE
                else fraud_models.FraudCheckType.UBBLE
            ),
        )

        return fraud_factories.BeneficiaryFraudCheckFactory(
            user=obj,
            status=fraud_models.FraudCheckStatus.OK,
            type=type_,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name=obj.firstName,
                last_name=obj.lastName,
                birth_date=obj.dateOfBirth.date(),
                ine_hash=obj.ineHash or "".join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                registration_datetime=obj.dateCreated,
            )
            if obj.eligibility == users_models.EligibilityType.UNDERAGE
            else fraud_factories.UbbleContentFactory(first_name=obj.firstName, last_name=obj.lastName),
            eligibilityType=users_models.EligibilityType.UNDERAGE
            if obj.eligibility == users_models.EligibilityType.UNDERAGE
            else users_models.EligibilityType.AGE18,
        )

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(user=obj, **kwargs)


class UnderageBeneficiaryFactory(BeneficiaryGrant18Factory):
    class Params:
        subscription_age = 15

    roles = [users_models.UserRole.UNDERAGE_BENEFICIARY]
    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine(date.today(), time(0, 0)) - relativedelta(years=o.subscription_age, months=5)
    )
    dateCreated = LazyAttribute(lambda user: user.dateOfBirth + relativedelta(years=user.subscription_age, hours=12))
    ineHash = factory.Sequence(lambda _: "".join(random.choices(string.ascii_lowercase + string.digits, k=32)))

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not create:
            return None

        if "dateCreated" not in kwargs:
            kwargs["dateCreated"] = obj.dateCreated

        return DepositGrantFactory(user=obj, **kwargs, type=payments_models.DepositType.GRANT_15_17)


class ProFactory(BaseFactory):
    class Meta:
        model = users_models.User

    email = factory.Sequence("ma.librairie{}@example.com".format)
    address = factory.Sequence("{} rue des cinémas".format)
    city = "Toulouse"
    departementCode = "31"
    firstName = "René"
    lastName = "Coty"
    publicName = "René Coty"
    isEmailValidated = True
    roles = [users_models.UserRole.PRO]
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        password = kwargs.get("password", settings.TEST_DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = settings.TEST_DEFAULT_PASSWORD
        return instance


class TokenFactory(BaseFactory):
    class Meta:
        model = models.Token

    type = users_models.TokenType.EMAIL_VALIDATION
    user = factory.SubFactory(UserFactory)
    value = factory.Sequence("XYZ{0}".format)


class PasswordResetTokenFactory(TokenFactory):
    type = models.TokenType.RESET_PASSWORD
    expirationDate = factory.LazyFunction(lambda: datetime.utcnow() + constants.RESET_PASSWORD_TOKEN_LIFE_TIME)


class EmailValidationTokenFactory(TokenFactory):
    type = models.TokenType.EMAIL_VALIDATION
    expirationDate = factory.LazyFunction(lambda: datetime.utcnow() + constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME)


class UserSessionFactory(BaseFactory):
    class Meta:
        model = models.UserSession

    uuid = factory.LazyFunction(uuid.uuid4)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
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
        model = payments_models.Deposit

    dateCreated = LazyAttribute(lambda _: datetime.utcnow())
    user = factory.SubFactory(UserFactory)  # BeneficiaryGrant18Factory is already creating a deposit
    source = "public"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        age = users_utils.get_age_from_birth_date(kwargs["user"].dateOfBirth)
        eligibility = (
            models.EligibilityType.UNDERAGE
            if age in users_constants.ELIGIBILITY_UNDERAGE_RANGE
            else models.EligibilityType.AGE18
        )
        granted_deposit = payments_api.get_granted_deposit(kwargs["user"], eligibility, age_at_registration=age)

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


class UserEmailHistoryFactory(BaseFactory):
    class Meta:
        model = users_models.UserEmailHistory
        abstract = True

    user = factory.SubFactory(UserFactory)
    oldUserEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[0])
    oldDomainEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[1])
    newUserEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[0])
    newDomainEmail = factory.LazyAttribute(lambda o: o.user.email.split("@")[1] + ".update")


class EmailUpdateEntryFactory(UserEmailHistoryFactory):
    eventType = users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value


class EmailValidationEntryFactory(UserEmailHistoryFactory):
    eventType = users_models.EmailHistoryEventTypeEnum.VALIDATION.value


class EmailAdminValidationEntryFactory(UserEmailHistoryFactory):
    eventType = users_models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION.value


class UserSuspensionBaseFactory(BaseFactory):
    class Meta:
        model = users_models.UserSuspension
        abstract = True

    user = factory.SubFactory(UserFactory, isActive=False)
    actorUser = factory.SubFactory(AdminFactory)
    eventType = users_models.SuspensionEventType.SUSPENDED
    eventDate = factory.LazyFunction(lambda: datetime.utcnow() - relativedelta(days=1))


class UserSuspensionByFraudFactory(UserSuspensionBaseFactory):
    reasonCode = users_constants.SuspensionReason.FRAUD_SUSPICION


class UnsuspendedSuspensionFactory(UserSuspensionBaseFactory):
    eventType = users_constants.SuspensionEventType.UNSUSPENDED


class SuspendedUponUserRequestFactory(UserSuspensionBaseFactory):
    reasonCode = users_constants.SuspensionReason.UPON_USER_REQUEST


class DeletedAccountSuspensionFactory(UserSuspensionByFraudFactory):
    reasonCode = users_constants.SuspensionReason.DELETED
