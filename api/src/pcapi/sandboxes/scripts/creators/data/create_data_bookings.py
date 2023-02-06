from datetime import datetime
from datetime import timedelta
import logging
from random import choice,sample,randint

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.offers.models import Offer
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


MAX_RATIO_OF_INITIAL_CREDIT = 0.4
OFFER_WITH_BOOKINGS_RATIO = 1
OFFER_WITH_SEVERAL_STOCKS_REMOVE_MODULO = 1
BOOKINGS_USED_REMOVE_MODULO = 1


def create_data_bookings(offers_by_name: dict[str, Offer], users_by_name: dict[str, User]) -> None:
    logger.info("create_data_bookings_data")
    bookings_by_name: dict[str, Booking] = {}
    for (user_name, user) in users_by_name.items():
        if (
            user.firstName != "DATA Test Jeune"
            and user.firstName != "DATA Test Mineur"
        ):
            continue
        user_number_of_bookings=randint(0, 35)
        logger.info("creating %d bookings for current user",user_number_of_bookings)
        temp_offers_by_name=offers_by_name.copy()
        for _booking_index in range(user_number_of_bookings):
            offer_name, offer = choice(list(temp_offers_by_name.items()))
            del temp_offers_by_name[offer_name]
            domains_credit = get_domains_credit(user)
            if not domains_credit:
                continue
            all_credit = domains_credit.all
            stock = choice(offer.stocks)
            if all_credit.remaining<stock.price:
                continue
            booking = IndividualBookingFactory(
                individualBooking__user=user,
                user=user,
                stock=stock,
            )
            #logger.info("created booking {}/{} with {}".format(booking_index,user_number_of_bookings,stock.offer.subcategoryId))

            booking_name = "{} / {} / {}".format(offer_name, user_name, booking.token)
            bookings_by_name[booking_name] = booking
    repository.save(*bookings_by_name.values())
    logger.info("created %d bookings", len(bookings_by_name))
    finance_api.price_bookings()


