import factory

import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models.db import db
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
    amount = factory.SelfAttribute("stock.price")

    @factory.post_generation
    def compute_confirmation_date(self, create, extracted, **kwargs):
        self.confirmationDate = api.compute_confirmation_date(self.stock.beginningDatetime, self.dateCreated)
        db.session.add(self)
        db.session.flush()


class BookingWithoutConfirmationDateFactory(BookingFactory):
    @factory.post_generation
    def compute_confirmation_date(self, create, extracted, **kwargs):
        pass
