from factory import SubFactory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers.factories import FutureOfferFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory

from . import models


class FutureOfferReminderFactory(BaseFactory):
    class Meta:
        model = models.FutureOfferReminder

    futureOffer = SubFactory(FutureOfferFactory)
    user = SubFactory(UserFactory)


class OfferReminderFactory(BaseFactory):
    class Meta:
        model = models.OfferReminder

    offer = SubFactory(OfferFactory)
    user = SubFactory(UserFactory)
