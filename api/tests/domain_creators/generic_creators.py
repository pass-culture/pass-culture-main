from datetime import datetime
from typing import Optional

from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.offers.models import Mediation
from pcapi.domain.booking_recap.booking_recap import BookingRecapLegacy
from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.models import Offer


def create_domain_booking_recap(
    offer_identifier: int = 1,
    offer_name: str = "Le livre de la jungle",
    offerer_name: str = "Libraire de Caen",
    offer_isbn: Optional[str] = None,
    beneficiary_lastname: str = "Sans Nom",
    beneficiary_firstname: str = "Mowgli",
    beneficiary_email: str = "mowgli@example.com",
    beneficiary_phonenumber: str = "0100000000",
    booking_amount: float = 0,
    booking_token: str = "JUNGLE",
    booking_date: datetime = datetime(2020, 3, 14, 19, 5, 3, 0),
    booking_is_duo: bool = False,
    booking_is_educational: bool = False,
    booking_is_used: bool = False,
    booking_is_cancelled: bool = False,
    booking_is_reimbursed: bool = False,
    booking_is_confirmed: bool = False,
    payment_date: Optional[datetime] = None,
    cancellation_date: Optional[datetime] = None,
    date_used: Optional[datetime] = None,
    redactor_lastname=None,
    redactor_firstname=None,
    redactor_email=None,
    venue_identifier: int = 1,
    venue_name="Librairie Kléber",
    venue_is_virtual=False,
    event_beginning_datetime: Optional[datetime] = None,
) -> BookingRecapLegacy:
    return BookingRecapLegacy(
        offer_identifier=offer_identifier,
        offer_name=offer_name,
        offerer_name=offerer_name,
        offer_isbn=offer_isbn,
        beneficiary_lastname=beneficiary_lastname,
        beneficiary_firstname=beneficiary_firstname,
        beneficiary_email=beneficiary_email,
        beneficiary_phonenumber=beneficiary_phonenumber,
        booking_amount=booking_amount,
        booking_token=booking_token,
        booking_date=booking_date,
        booking_is_duo=booking_is_duo,
        booking_is_educational=booking_is_educational,
        booking_is_used=booking_is_used,
        booking_is_cancelled=booking_is_cancelled,
        booking_is_reimbursed=booking_is_reimbursed,
        booking_is_confirmed=booking_is_confirmed,
        payment_date=payment_date,
        cancellation_date=cancellation_date,
        cancellation_limit_date=compute_cancellation_limit_date(event_beginning_datetime, booking_date),
        date_used=date_used,
        redactor_lastname=redactor_lastname,
        redactor_firstname=redactor_firstname,
        redactor_email=redactor_email,
        venue_identifier=venue_identifier,
        venue_name=venue_name,
        venue_is_virtual=venue_is_virtual,
        event_beginning_datetime=event_beginning_datetime,
    )


def create_domain_favorite(identifier: int, offer: Offer, mediation: Mediation = None, booking: dict = None):
    return FavoriteDomain(identifier=identifier, offer=offer, mediation=mediation, booking=booking)
