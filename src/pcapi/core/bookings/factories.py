import factory

import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.utils.token import random_token

from . import api
from . import models


class BookingFactory(BaseFactory):
    class Meta:
        model = models.Booking

    stock = factory.SubFactory(offers_factories.StockFactory)
    quantity = 1
    token = factory.LazyFunction(random_token)
    user = factory.SubFactory(users_factories.UserFactory)
    amount = factory.SelfAttribute('stock.price')

    @factory.post_generation
    def confirmationDate(self, create, override, **extra):
        if override:
            self.confirmationDate = override
        else:
            self.confirmationDate = api.compute_confirmation_date(self.stock.beginningDatetime, self.dateCreated)
        repository.save(self)
