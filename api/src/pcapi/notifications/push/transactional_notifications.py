from datetime import date
from enum import Enum
import logging

from pcapi.core.bookings import exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.utils.urls import booking_app_link
from pcapi.utils.urls import offer_app_link


logger = logging.getLogger(__name__)


class GroupId(Enum):
    CANCEL_BOOKING = "Cancel_booking"
    TODAY_STOCK = "Today_stock"
    OFFER_LINK = "Offer_link"
    SOON_EXPIRING_BOOKINGS = "Soon_expiring_bookings"
    FAVORITES_NOT_BOOKED = "Favorites_not_booked"


class TransactionalNotificationMessage(BaseModel):
    body: str
    title: str | None = None


class TransactionalNotificationData(BaseModel):
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: list[int]
    message: TransactionalNotificationMessage
    extra: dict = {}


def get_bookings_cancellation_notification_data(booking_ids: list[int]) -> TransactionalNotificationData | None:
    bookings = db.session.query(Booking).filter(Booking.id.in_(booking_ids))

    if not bookings:
        return None

    cancelled_object = (
        "commande" if bookings[0].stock.offer.isDigital or bookings[0].stock.offer.isThing else "réservation"
    )
    return TransactionalNotificationData(
        group_id=GroupId.CANCEL_BOOKING.value,
        user_ids=[booking.userId for booking in bookings],
        message=TransactionalNotificationMessage(
            title=f"{cancelled_object.capitalize()} annulée",
            body=f"""Ta {cancelled_object} "{bookings[0].stock.offer.name}" a été annulée par l'offreur.""",
        ),
    )


def get_today_stock_booking_notification_data(booking: Booking, offer: Offer) -> TransactionalNotificationData | None:
    return TransactionalNotificationData(
        group_id=GroupId.TODAY_STOCK.value,
        user_ids=[booking.userId],
        message=TransactionalNotificationMessage(
            title="C'est aujourd'hui !",
            body=f"Retrouve les détails de la réservation pour {offer.name} sur l’application pass Culture",
        ),
        extra={"deeplink": booking_app_link(booking)},
    )


def get_offer_notification_data(user_id: int, offer: Offer) -> TransactionalNotificationData:
    return TransactionalNotificationData(
        group_id=GroupId.OFFER_LINK.value,
        user_ids=[user_id],
        message=TransactionalNotificationMessage(
            title=f"Ta réservation pour {offer.name}",
            body="Pour la confirmer, clique sur le lien que tu as reçu par mail 📩",
        ),
    )


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
