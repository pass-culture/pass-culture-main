import logging
import typing
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from enum import Enum

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.external.batch import tasks
from pcapi.core.external.batch.serialization import TransactionalNotificationData
from pcapi.core.external.batch.serialization import TransactionalNotificationDataV2
from pcapi.core.external.batch.serialization import TransactionalNotificationMessage
from pcapi.core.external.batch.serialization import TransactionalNotificationMessageV2
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils.urls import booking_app_link
from pcapi.utils.urls import offer_app_link


logger = logging.getLogger(__name__)


class GroupId(Enum):
    CANCEL_BOOKING = "Cancel_booking"
    TODAY_STOCK = "Today_stock"
    OFFER_LINK = "Offer_link"
    SOON_EXPIRING_BOOKINGS = "Soon_expiring_bookings"
    FAVORITES_NOT_BOOKED = "Favorites_not_booked"


def send_cancel_booking_notification(booking_ids: list[int]) -> None:
    bookings = db.session.query(Booking).filter(Booking.id.in_(booking_ids)).all()

    if not bookings:
        return None

    offer = bookings[0].stock.offer
    cancelled_object = "commande" if offer.hasUrl or offer.isThing else "réservation"
    payload = TransactionalNotificationDataV2(
        group_id=GroupId.CANCEL_BOOKING.value,
        user_ids=[booking.userId for booking in bookings],
        message=TransactionalNotificationMessageV2(
            title=f"{cancelled_object.capitalize()} annulée",
            body=f"""Ta {cancelled_object} "{offer.name}" a été annulée par l'offreur.""",
        ),
    )
    tasks.send_transactional_notification_task.delay(payload.model_dump())


def _setup_today_min_max(utc_mean_offset: int, start_utc_hour: int = 13) -> tuple[datetime, datetime]:
    """
    Build datetime time slots: the UTC datetimes that corresponds to the
    expected local ones.

    Example:
        * local time is UTC+5, and the target is 13h->23h59,
          the corresponding UTC time slots is 8h->18h59;

          _setup_today_min_max(5)
          returns datetime(<today>, 8, 0), datetime(<today>, 18, 59)

        * local time is UTC-6, and the target is still 13h->23h59,
          the corresponding UTC time slots is 19h(today)->5h59(tomorrow);

          _setup_today_min_max(-6)
          returns datetime(<today>, 19, 0), datetime(<tomorrow>, 5, 59)
    """
    today_min_base = datetime.combine(date.today(), time(hour=start_utc_hour))
    today_max_base = datetime.combine(date.today(), time(hour=23, minute=59))

    today_min = today_min_base - timedelta(hours=utc_mean_offset)
    today_max = today_max_base - timedelta(hours=utc_mean_offset)

    return today_min, today_max


def _send_today_event_notification(stock_ids: set[int]) -> None:
    for stock_id in stock_ids:
        try:
            offer = (
                db.session.query(offers_models.Offer)
                .join(offers_models.Offer.stocks)
                .filter(offers_models.Stock.id == stock_id)
                .one()
            )
            bookings = bookings_api.get_individual_bookings_from_stock(stock_id)

            for booking in bookings:
                payload = TransactionalNotificationDataV2(
                    group_id=GroupId.TODAY_STOCK.value,
                    user_ids=[booking.userId],
                    message=TransactionalNotificationMessageV2(
                        title="C'est aujourd'hui !",
                        body=f"Retrouve les détails de la réservation pour {offer.name} sur l’application pass Culture",
                    ),
                    extra={"deeplink": booking_app_link(booking)},
                )
                tasks.send_transactional_notification_task.delay(payload.model_dump())
        except Exception:
            logger.exception("Could not send today stock notification", extra={"stock": stock_id})


def send_today_events_notifications_metropolitan_france() -> None:
    """
    Find bookings (grouped by stocks) that occur today in metropolitan
    France but not the morning (11h UTC -> 12h/13h local time) and
    send notifications to all the users.
    """
    today_min, today_max = _setup_today_min_max(utc_mean_offset=1)
    stock_ids = offers_repository.find_today_event_stock_ids_metropolitan_france(today_min, today_max)

    if not stock_ids:
        logger.warning("No stock found", extra={"today_min": today_min, "today_max": today_max})
        return

    _send_today_event_notification(stock_ids)


def send_today_events_notifications_overseas(utc_mean_offset: int, departments: typing.Iterable[str]) -> None:
    """
    Find bookings (grouped by stocks) that occur today in overseas
    french departments but not the morning (11h UTC), and send
    notifications to all the users.

    Example:
        to target bookings from la Réunion,
        send_today_events_notifications_overseas(5, ["974"])
    """
    today_min, today_max = _setup_today_min_max(utc_mean_offset)
    stock_ids = offers_repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments)

    if not stock_ids:
        logger.warning(
            "No stock found",
            extra={
                "today_min": today_min,
                "today_max": today_max,
                "utc_mean_offset": utc_mean_offset,
                "departments": departments,
            },
        )
        return

    _send_today_event_notification(stock_ids)


def send_offer_link_by_push(user_id: int, offer: Offer) -> None:
    payload = TransactionalNotificationDataV2(
        group_id=GroupId.OFFER_LINK.value,
        user_ids=[user_id],
        message=TransactionalNotificationMessageV2(
            title=f"Ta réservation pour {offer.name}",
            body="Pour la confirmer, clique sur le lien que tu as reçu par mail 📩",
        ),
    )
    tasks.send_transactional_notification_task.delay(payload.model_dump())


def get_soon_expiring_bookings_with_offers_notification_data(booking: Booking) -> TransactionalNotificationData:
    assert booking.expirationDate is not None  # help mypy
    remaining_days = (booking.expirationDate.date() - date.today()).days

    if remaining_days < 0:
        raise exceptions.BookingIsExpired(booking.id)

    if remaining_days > 1:
        body = f'Vite, il ne te reste plus que {remaining_days} jours pour récupérer "{booking.stock.offer.name}"'
    elif remaining_days == 1:
        body = f'Vite, il ne te reste plus qu\'un jour pour récupérer "{booking.stock.offer.name}"'
    else:
        body = f'Vite, dernier jour pour récupérer "{booking.stock.offer.name}"'

    return TransactionalNotificationData(
        group_id=GroupId.SOON_EXPIRING_BOOKINGS.value,
        user_ids=[booking.userId],
        message=TransactionalNotificationMessage(title="Tu n'as pas récupéré ta réservation", body=body),
        extra={"deeplink": booking_app_link(booking)},
    )


def get_favorites_not_booked_notification_data(
    offer_id: int, offer_name: str, user_ids: list[int]
) -> TransactionalNotificationData:
    msg_title = "Ne t’arrête pas en si bon chemin 😮"
    msg_body = f"{offer_name} t’attend sur le pass Culture !"
    utm = "utm_campaign=favorisj%2B3&utm_source=transac&utm_medium=push"

    return TransactionalNotificationData(
        group_id=GroupId.FAVORITES_NOT_BOOKED.value,
        user_ids=user_ids,
        message=TransactionalNotificationMessage(title=msg_title, body=msg_body),
        extra={"deeplink": offer_app_link(offer_id, utm=utm)},
    )
