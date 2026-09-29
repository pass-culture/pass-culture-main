import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory

from . import models


class FavoriteOfferFactory(BaseFactory):
    class Meta:
        model = models.FavoriteOffer

    offer = factory.SubFactory(OfferFactory)
    user = factory.SubFactory(UserFactory)
