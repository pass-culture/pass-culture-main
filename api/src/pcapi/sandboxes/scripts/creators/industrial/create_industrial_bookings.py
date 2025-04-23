from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import logging
from random import choice

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.finance import api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


MAX_RATIO_OF_INITIAL_CREDIT = 0.4
OFFER_WITH_BOOKINGS_RATIO = 3
OFFER_WITH_SEVERAL_STOCKS_REMOVE_MODULO = 2
BOOKINGS_USED_REMOVE_MODULO = 5


def create_industrial_bookings(offers_by_name: dict[str, Offer], users_by_name: dict[str, User]) -> None:
    logger.info("create_industrial_bookings")

    bookings_by_name: dict[str, Booking] = {}

    list_of_users_with_no_more_money: list[User] = []

    token = 100000

    active_offers_with_stocks = {
        booking_key: offer
        for booking_key, offer in offers_by_name.items()
        if offer.venue.managingOfferer.isValidated is True and len(offer.stocks) > 0
    }

    for user_name, user in users_by_name.items():
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
                bookings_by_name=bookings_by_name,
                list_of_users_with_no_more_money=list_of_users_with_no_more_money,
                offers_by_name=active_offers_with_stocks,
                token=token,
                user=user,
                user_name=user_name,
            )

    repository.save(*bookings_by_name.values())
    logger.info("created %d bookings", len(bookings_by_name))

    finance_api.price_events()


def _create_bookings_for_other_beneficiaries(
    *,
    bookings_by_name: dict[str, Booking],
    list_of_users_with_no_more_money: list[User],
    offers_by_name: dict[str, Offer],
    token: int,
    user: User,
    user_name: str,
) -> int:
    user_should_have_no_more_money = "has-no-more-money" in user.email
    for offer_index, (offer_name, offer) in enumerate(list(offers_by_name.items())):
        if offer_index % OFFER_WITH_BOOKINGS_RATIO != 0:
            continue

        for index, stock in enumerate(offer.stocks):
            # every STOCK_MODULO RECO will have several stocks
            if index > 0 and offer_index % (OFFER_WITH_SEVERAL_STOCKS_REMOVE_MODULO + index):
                continue

            booking_name = "{} / {} / {}".format(offer_name, user_name, str(token))

            is_used = offer_index % BOOKINGS_USED_REMOVE_MODULO != 0

            if is_used:
                stock.beginningDatetime = datetime.utcnow() - timedelta(days=2)
                stock.bookingLimitDatetime = datetime.utcnow() - timedelta(days=5)
                repository.save(stock)

            if user_should_have_no_more_money and user not in list_of_users_with_no_more_money:
                assert user.deposit
                booking_amount = user.deposit.amount
                list_of_users_with_no_more_money.append(user)
            elif user_should_have_no_more_money and user in list_of_users_with_no_more_money:
                booking_amount = Decimal(0)
            else:
                booking_amount = None

            booking = bookings_factories.BookingFactory.create(
                user=user,
                status=BookingStatus.USED if is_used else BookingStatus.CONFIRMED,
                stock=stock,
                dateUsed=datetime.utcnow() - timedelta(days=2) if is_used else None,
                amount=booking_amount if booking_amount is not None else stock.price,
                token=str(token),
                offerer=offer.venue.managingOfferer,
            )
            if is_used:
                finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
            bookings_by_name[booking_name] = booking

            token = token + 1

    return token


def _create_has_booked_some_bookings(
    bookings_by_name: dict[str, Booking], offers_by_name: dict[str, Offer], user: User, user_name: str
) -> None:
    for offer_index, (offer_name, offer) in enumerate(list(offers_by_name.items())):
        if offer_index % OFFER_WITH_BOOKINGS_RATIO != 0:
            continue
        domains_credit = get_domains_credit(user)
        if not domains_credit:
            continue
        digital_credit = domains_credit.digital
        all_credit = domains_credit.all

        if digital_credit and digital_credit.remaining < MAX_RATIO_OF_INITIAL_CREDIT * float(digital_credit.initial):
            break

        if all_credit.remaining < MAX_RATIO_OF_INITIAL_CREDIT * float(all_credit.initial):
            break

        stock = choice(offer.stocks)

        is_used = offer_index % BOOKINGS_USED_REMOVE_MODULO != 0

        if is_used:
            stock.beginningDatetime = datetime.utcnow() - timedelta(days=2)
            stock.bookingLimitDatetime = datetime.utcnow() - timedelta(days=5)
            repository.save(stock)

        booking = bookings_factories.BookingFactory.create(
            user=user,
            status=BookingStatus.USED if is_used else BookingStatus.CONFIRMED,
            stock=stock,
            dateUsed=datetime.utcnow() - timedelta(days=2) if is_used else None,
        )
        if is_used:
            finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
        booking_name = "{} / {} / {}".format(offer_name, user_name, booking.token)
        bookings_by_name[booking_name] = booking


def create_fraudulent_bookings() -> None:
    logger.info("create_fraudulent_bookings")
    offerer = offerers_factories.OffererFactory.create(name="Entité avec des réservations frauduleuses")
    good_venue = offerers_factories.VenueFactory.create(
        name="Structure sans réservations frauduleuses", managingOfferer=offerer
    )
    bad_venue = offerers_factories.VenueFactory.create(
        name="Structure avec des réservations frauduleuses", managingOfferer=offerer
    )
    bookings_factories.BookingFactory.create(stock__offer__venue=good_venue)
    bookings_factories.BookingFactory.create(stock__offer__venue=good_venue)
    bookings_factories.FraudulentBookingTagFactory.create(
        booking__stock__offer__venue=bad_venue, booking__stock__offer__name="Offre avec réservation frauduleuse"
    )
    bookings_factories.BookingFactory.create(stock__offer__venue=bad_venue)
