import datetime
import uuid

import factory

from pcapi.core.testing import BaseFactory
import pcapi.core.users.models
from pcapi.models import user_session

from . import constants
from . import models


DEFAULT_PASSWORD = "user@AZERTY123"


class UserFactory(BaseFactory):
    class Meta:
        model = pcapi.core.users.models.User

    email = factory.Sequence("jeanne.doux{0}@example.com".format)
    address = factory.Sequence("{0} rue des machines".format)
    city = "Paris"
    dateOfBirth = datetime.datetime(2000, 1, 1)
    departementCode = "75"
    firstName = "Jeanne"
    lastName = "Doux"
    publicName = "Jeanne Doux"
    isEmailValidated = True
    isBeneficiary = True
    hasSeenProTutorials = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = pcapi.core.users.models.hash_password(password)
        # Let us just say `UserFactory(isAdmin=True)` and not have to
        # mention `isBeneficiary=False` (because it's enforced by a
        # database constraint anyway).
        if kwargs.get("isAdmin"):
            kwargs["isBeneficiary"] = False
        return super()._create(model_class, *args, **kwargs)

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = pcapi.core.users.models.hash_password(password)
        return super()._build(model_class, *args, **kwargs)

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):  # pylint: disable=no-self-argument
        from pcapi.core.payments.factories import DepositFactory

        if not create:
            return None
        if obj.isAdmin or not obj.isBeneficiary:
            return None
        return DepositFactory(user=obj, **kwargs)


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
