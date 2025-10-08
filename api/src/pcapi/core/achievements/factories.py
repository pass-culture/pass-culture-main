import datetime

import factory

import pcapi.core.bookings.factories as booking_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.factories import BaseFactory
from pcapi.utils import date as date_utils

from . import models


class AchievementFactory(BaseFactory):
    class Meta:
        model = models.Achievement

    user = factory.SubFactory(users_factories.BeneficiaryFactory)
    name = models.AchievementEnum.FIRST_BOOK_BOOKING
    unlockedDate = factory.LazyFunction(date_utils.get_naive_utc_now)
    seenDate: datetime.datetime | None = None
    booking = factory.SubFactory(booking_factories.BookingFactory)
