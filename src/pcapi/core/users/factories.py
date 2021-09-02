import datetime
import uuid

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.testing import BaseFactory
import pcapi.core.users.models
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import user_session
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.utils import crypto

from . import constants
from . import models


DEFAULT_PASSWORD = "user@AZERTY123"


class UserFactory(BaseFactory):
    class Meta:
        model = pcapi.core.users.models.User

    email = factory.Sequence("jean.neige{}@example.com".format)
    address = factory.Sequence("{} place des noces rouges".format)
    city = "La Rochelle"
    dateOfBirth = datetime.datetime(1980, 1, 1)
    departementCode = "75"
    firstName = "Jean"
    lastName = "Neige"
    publicName = "Jean Neige"
    isEmailValidated = True
    isBeneficiary = False
    isAdmin = False
    roles = []
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance


class AdminFactory(BaseFactory):
    class Meta:
        model = pcapi.core.users.models.User

    email = factory.Sequence("un.admin{}@example.com".format)
    address = factory.Sequence("{} rue des détectives".format)
    city = "Bordeaux"
    departementCode = "33"
    firstName = "Frank"
    lastName = "Columbo"
    publicName = "Frank Columbo"
    isEmailValidated = True
    isAdmin = True
    isBeneficiary = False
    roles = [pcapi.core.users.models.UserRole.ADMIN]
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance


class BeneficiaryFactory(BaseFactory):
    class Meta:
        model = pcapi.core.users.models.User

    email = factory.Sequence("jeanne.doux{}@example.com".format)
    address = factory.Sequence("{} rue des machines".format)
    city = "Paris"
    dateOfBirth = datetime.datetime.today() - relativedelta(years=18, months=1)
    departementCode = "75"
    firstName = "Jeanne"
    lastName = "Doux"
    publicName = "Jeanne Doux"
    isEmailValidated = True
    isAdmin = False
    isBeneficiary = True
    roles = [pcapi.core.users.models.UserRole.BENEFICIARY]
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):  # pylint: disable=no-self-argument
        from pcapi.core.payments.factories import DepositGrant18Factory

        if not create:
            return None
        return DepositGrant18Factory(user=obj, **kwargs)


class UnderageBeneficiaryFactory(BeneficiaryFactory):
    dateOfBirth = datetime.datetime.now() - relativedelta(years=15, months=5)
    roles = [pcapi.core.users.models.UserRole.UNDERAGE_BENEFICIARY]


class ProFactory(BaseFactory):
    class Meta:
        model = pcapi.core.users.models.User

    email = factory.Sequence("ma.librairie{}@example.com".format)
    address = factory.Sequence("{} rue des cinémas".format)
    city = "Toulouse"
    departementCode = "31"
    firstName = "René"
    lastName = "Coty"
    publicName = "René Coty"
    isEmailValidated = True
    isAdmin = False
    isBeneficiary = False
    roles = [pcapi.core.users.models.UserRole.PRO]
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._create(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = crypto.hash_password(password)
        instance = super()._build(model_class, *args, **kwargs)
        instance.clearTextPassword = DEFAULT_PASSWORD
        return instance


class TokenFactory(BaseFactory):
    class Meta:
        model = models.Token

    value = factory.Sequence("XYZ{0}".format)


class ResetPasswordToken(TokenFactory):
    type = models.TokenType.RESET_PASSWORD
    expirationDate = factory.LazyFunction(lambda: datetime.datetime.now() + constants.RESET_PASSWORD_TOKEN_LIFE_TIME)


class EmailValidationToken(TokenFactory):
    type = models.TokenType.EMAIL_VALIDATION
    expirationDate = factory.LazyFunction(lambda: datetime.datetime.now() + constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME)


class IdCheckToken(TokenFactory):
    type = models.TokenType.ID_CHECK
    creationDate = factory.LazyFunction(datetime.datetime.now)
    expirationDate = factory.LazyFunction(lambda: datetime.datetime.now() + constants.ID_CHECK_TOKEN_LIFE_TIME)


class UserSessionFactory(BaseFactory):
    class Meta:
        model = user_session.UserSession

    uuid = factory.LazyFunction(uuid.uuid4)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
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


class BeneficiaryImportFactory(BaseFactory):
    class Meta:
        model = BeneficiaryImport

    applicationId = factory.Sequence(lambda n: n)
    beneficiary = factory.SubFactory("pcapi.core.users.factories.UserFactory")
    source = BeneficiaryImportSources.jouve.value


class BeneficiaryImportStatusFactory(BaseFactory):
    class Meta:
        model = BeneficiaryImportStatus

    status = ImportStatus.CREATED.value
    date = factory.Faker("date_time_between", start_date="-30d", end_date="-1d")
    detail = factory.Faker("sentence", nb_words=3)
    beneficiaryImport = factory.SubFactory(BeneficiaryImportFactory)
    author = factory.SubFactory("pcapi.core.users.factories.UserFactory")
