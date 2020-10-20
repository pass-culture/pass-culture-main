import datetime

import factory

from pcapi.core.testing import BaseFactory
from pcapi.models import user_sql_entity


class UserFactory(BaseFactory):
    class Meta:
        model = user_sql_entity.UserSQLEntity

    email = factory.Sequence('jeanne.doux{0}@example.com'.format)
    address = factory.Sequence('{0} rue des machines'.format)
    city = 'Paris'
    dateOfBirth = datetime.datetime(2000, 1, 1)
    departementCode = '75'
    firstName = "Jeanne"
    lastName = "Doux"
    publicName = "Jeanne Doux"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get('password', 'user@AZERTY123')
        kwargs['password'] = user_sql_entity.hash_password(password)
        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def deposit(obj, create, extracted, **kwargs):
        from pcapi.core.payments.factories import DepositFactory

        if not create:
            return
        if obj.isAdmin or not obj.canBookFreeOffers:
            return
        deposit_kwargs = {'user': obj}
        if extracted:
            deposit_kwargs['amount'] = extracted
        else:
            pass  # use the default value of DepositFactory.amount
        return DepositFactory(**deposit_kwargs)
