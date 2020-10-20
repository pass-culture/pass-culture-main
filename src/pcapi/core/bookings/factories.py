import factory

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.testing import BaseFactory
from pcapi.utils.token import random_token

from . import models


class BookingFactory(BaseFactory):
    class Meta:
        model = models.BookingSQLEntity

    stock = factory.SubFactory(offers_factories.StockFactory)
    quantity = 1
    token = factory.LazyFunction(random_token)
    user = factory.SubFactory(users_factories.UserFactory)
    amount = factory.SelfAttribute('stock.price')
