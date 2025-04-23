import datetime

import factory

import pcapi.core.bookings.factories as booking_factories
from pcapi.core.factories import BaseFactory
import pcapi.core.users.factories as users_factories

from . import models


class AchievementFactory(BaseFactory):
    class Meta:
        model = models.Achievement

    user = factory.SubFactory(users_factories.BeneficiaryFactory)
    name = models.AchievementEnum.FIRST_BOOK_BOOKING
    unlockedDate = factory.LazyFunction(datetime.datetime.utcnow)
    seenDate: datetime.datetime | None = None
    booking = factory.SubFactory(booking_factories.BookingFactory)
