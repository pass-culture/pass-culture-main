import datetime

import factory

from pcapi.core.testing import BaseFactory
from pcapi.models import user_sql_entity

from . import constants
from . import models


DEFAULT_PASSWORD = "user@AZERTY123"


class UserFactory(BaseFactory):
    class Meta:
        model = user_sql_entity.UserSQLEntity

    email = factory.Sequence("jeanne.doux{0}@example.com".format)
    address = factory.Sequence("{0} rue des machines".format)
    city = "Paris"
    dateOfBirth = datetime.datetime(2000, 1, 1)
    departementCode = "75"
    firstName = "Jeanne"
    lastName = "Doux"
    publicName = "Jeanne Doux"
    isEmailValidated = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", DEFAULT_PASSWORD)
        kwargs["password"] = user_sql_entity.hash_password(password)
        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):
        from pcapi.core.payments.factories import DepositFactory

        if not create:
            return None
        if obj.isAdmin or not obj.canBookFreeOffers:
            return None
        deposit_kwargs = {"user": obj}
        if extracted:
            deposit_kwargs["amount"] = extracted
        else:
            pass  # use the default value of DepositFactory.amount
        return DepositFactory(**deposit_kwargs)


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
