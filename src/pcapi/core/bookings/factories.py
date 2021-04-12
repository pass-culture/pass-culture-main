import factory

import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models.db import db
from pcapi.utils.token import random_token

from . import api
from . import models


class BookingFactory(BaseFactory):
    class Meta:
        model = models.Booking

    quantity = 1
    stock = factory.Maybe(
        "isCancelled",
        yes_declaration=factory.SubFactory(offers_factories.StockFactory),
        no_declaration=factory.SubFactory(
            offers_factories.StockFactory, dnBookedQuantity=factory.SelfAttribute("..quantity")
        ),
    )
    token = factory.LazyFunction(random_token)
    user = factory.SubFactory(users_factories.UserFactory)
    amount = factory.SelfAttribute("stock.price")

    @factory.post_generation
    def confirmation_date(self, create, extracted, **kwargs):
        if extracted:
            self.confirmationDate = extracted
        else:
            self.confirmationDate = api.compute_confirmation_date(self.stock.beginningDatetime, self.dateCreated)
        db.session.add(self)
        db.session.flush()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get("stock") and not kwargs.get("isCancelled", False):
            stock = kwargs.get("stock")
            stock.dnBookedQuantity = stock.dnBookedQuantity + kwargs.get("quantity", 1)
            kwargs["stock"] = stock
        return super()._create(model_class, *args, **kwargs)
