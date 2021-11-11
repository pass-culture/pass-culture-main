from datetime import datetime
from datetime import timedelta
import logging
from random import choice

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


MAX_RATIO_OF_INITIAL_CREDIT = 0.4
OFFER_WITH_BOOKINGS_RATIO = 3
OFFER_WITH_SEVERAL_STOCKS_REMOVE_MODULO = 2
BOOKINGS_USED_REMOVE_MODULO = 5


def create_industrial_bookings(offers_by_name, users_by_name):
    logger.info("create_industrial_bookings")

    bookings_by_name = {}

    list_of_users_with_no_more_money = []

    token = 100000

    active_offers_with_stocks = {
        booking_key: offer
        for booking_key, offer in offers_by_name.items()
        if offer.venue.managingOfferer.isValidated is True and len(offer.stocks) > 0
    }

    for (user_name, user) in users_by_name.items():
        if (
            user.firstName != "PC Test Jeune"
            or "has-signed-up" in user_name
            or "has-filled-cultural-survey" in user_name
        ):
            continue

        if "has-booked-some" in user.email:
            _create_has_booked_some_bookings(bookings_by_name, active_offers_with_stocks, user, user_name)
        else:
            token = _create_bookings_for_other_beneficiaries(
                bookings_by_name, list_of_users_with_no_more_money, active_offers_with_stocks, token, user, user_name
            )

    repository.save(*bookings_by_name.values())

    logger.info("created %d bookings", len(bookings_by_name))


def _create_bookings_for_other_beneficiaries(
    bookings_by_name, list_of_users_with_no_more_money, offers_by_name, token: int, user: User, user_name: str
) -> int:
    user_should_have_no_more_money = "has-no-more-money" in user.email
    for (offer_index, (offer_name, offer)) in enumerate(list(offers_by_name.items())):
        # FIXME (viconnex, 2020-12-22) trying to adapt previous code - not sure of the result and intention
        if offer_index % OFFER_WITH_BOOKINGS_RATIO != 0:
            continue

        user_has_only_activation_booked = (
            "has-booked-activation" in user.email or "has-confirmed-activation" in user.email
        )

        is_activation_offer = offer.product.subcategoryId in (
            subcategories.ACTIVATION_EVENT.id,
            subcategories.ACTIVATION_THING.id,
        )

        if user_has_only_activation_booked and not is_activation_offer:
            continue

        for (index, stock) in enumerate(offer.stocks):
            # every STOCK_MODULO RECO will have several stocks
            if index > 0 and offer_index % (OFFER_WITH_SEVERAL_STOCKS_REMOVE_MODULO + index):
                continue

            booking_name = "{} / {} / {}".format(offer_name, user_name, str(token))

            if is_activation_offer:
                is_used = (
                    "has-confirmed-activation" in user.email
                    or "has-booked-some" in user.email
                    or "has-no-more-money" in user.email
                )
            else:
                is_used = offer_index % BOOKINGS_USED_REMOVE_MODULO != 0

            if is_used:
                stock.beginningDatetime = datetime.now() - timedelta(days=2)
                stock.bookingLimitDatetime = datetime.now() - timedelta(days=5)
                repository.save(stock)

            if user_should_have_no_more_money and user not in list_of_users_with_no_more_money:
                booking_amount = user.deposit.amount
                list_of_users_with_no_more_money.append(user)
            elif user_should_have_no_more_money and user in list_of_users_with_no_more_money:
                booking_amount = 0
            else:
                booking_amount = None

            bookings_by_name[booking_name] = IndividualBookingFactory(
                individualBooking__user=user,
                isUsed=is_used,
                status=BookingStatus.USED if is_used else BookingStatus.CONFIRMED,
                stock=stock,
                dateUsed=datetime.now() - timedelta(days=2) if is_used else None,
                amount=booking_amount,
                token=str(token),
                offerer=offer.venue.managingOfferer,
                venue=offer.venue,
            )

            token = token + 1

    return token


def _create_has_booked_some_bookings(bookings_by_name, offers_by_name, user, user_name):

    for (offer_index, (offer_name, offer)) in enumerate(list(offers_by_name.items())):
        # FIXME (viconnex, 2020-12-22) trying to adapt previous code - not sure of the result and intention
        # FIXME (asaunier, 2021-01-22) UPDATE - We should replace the "ratio" mechanism by a more immutable data
        #  construction. We currently pick among the list of available offers that may change.
        if offer_index % OFFER_WITH_BOOKINGS_RATIO != 0:
            continue
        domains_credit = get_domains_credit(user)
        digital_credit = domains_credit.digital
        all_credit = domains_credit.all

        if digital_credit and digital_credit.remaining < MAX_RATIO_OF_INITIAL_CREDIT * float(digital_credit.initial):
            break

        if all_credit.remaining < MAX_RATIO_OF_INITIAL_CREDIT * float(all_credit.initial):
            break

        is_activation_offer = offer.product.subcategoryId in (
            subcategories.ACTIVATION_EVENT.id or subcategories.ACTIVATION_THING.id
        )

        stock = choice(offer.stocks)

        if is_activation_offer:
            is_used = True
        else:
            is_used = offer_index % BOOKINGS_USED_REMOVE_MODULO != 0

        if is_used:
            stock.beginningDatetime = datetime.now() - timedelta(days=2)
            stock.bookingLimitDatetime = datetime.now() - timedelta(days=5)
            repository.save(stock)

        booking = IndividualBookingFactory(
            individualBooking__user=user,
            isUsed=is_used,
            status=BookingStatus.USED if is_used else BookingStatus.CONFIRMED,
            stock=stock,
            dateUsed=datetime.now() - timedelta(days=2) if is_used else None,
        )
        booking_name = "{} / {} / {}".format(offer_name, user_name, booking.token)
        bookings_by_name[booking_name] = booking
