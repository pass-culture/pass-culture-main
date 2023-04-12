from datetime import datetime
from datetime import timedelta
import logging
from random import choice
from random import randint

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.finance import api as finance_api
import pcapi.core.finance.factories as finance_factories
from pcapi.core.offers.models import Offer
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_data_bookings(offers_by_name: dict[str, Offer], users_by_name: dict[str, User]) -> None:
    logger.info("create_data_bookings_data")
    bookings_by_name: dict[str, bookings_models.Booking] = {}
    token = 200000
    for user_name, user in users_by_name.items():
        if user.firstName not in ("DATA Test Jeune", "DATA Test Mineur"):
            continue
        user_number_of_bookings = randint(0, 35)
        logger.info("creating %d bookings for current user", user_number_of_bookings)
        temp_offers_by_name = offers_by_name.copy()
        for _booking_index in range(user_number_of_bookings):
            offer_name, offer = choice(list(temp_offers_by_name.items()))
            del temp_offers_by_name[offer_name]
            domains_credit = get_domains_credit(user)
            if not domains_credit:
                continue
            all_credit = domains_credit.all
            stock = choice(offer.stocks)
            if all_credit.remaining < stock.price:
                continue
            booking_name = f"{offer_name} / {user_name} / DATA"
            booking = bookings_factories.UsedBookingFactory(
                user=user,
                stock=stock,
                dateUsed=datetime.utcnow() - timedelta(days=2),
                token=str(token),
            )
            finance_factories.UsedBookingFinanceEventFactory(booking=booking)
            bookings_by_name[booking_name] = booking
            token = token + 1
    repository.save(*bookings_by_name.values())
    logger.info("created %d bookings", len(bookings_by_name))
    finance_api.price_events()
