from factory import SubFactory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory

from . import models


class OfferReminderFactory(BaseFactory):
    class Meta:
        model = models.OfferReminder

    offer = SubFactory(OfferFactory)
    user = SubFactory(UserFactory)
