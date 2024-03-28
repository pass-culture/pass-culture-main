import decimal

import sqlalchemy as sa

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models


class Valid:
    def __init__(self, is_valid: bool, message: str | None = None) -> None:
        self.is_valid = is_valid
        self.messages = [message] if message is not None else []

    def __bool__(self) -> bool:
        return self.is_valid

    def __and__(self, other: "Valid") -> "Valid":
        new_valid = Valid(is_valid=self.is_valid and other.is_valid)
        new_valid.messages = self.messages + other.messages
        return new_valid

    def __or__(self, other: "Valid") -> "Valid":
        new_valid = Valid(is_valid=self.is_valid or other.is_valid)
        # keep the message only for `Valid` instances having `is_valid == False`
        new_valid.messages = ([] if self.is_valid else self.messages) + ([] if other.is_valid else other.messages)
        return new_valid


def check_incident_bookings(bookings: list[bookings_models.Booking]) -> Valid:
    if not bookings:
        return Valid(
            is_valid=False,
            message="""Seules les réservations ayant le statut "remboursée" peuvent faire l'objet d'un incident.""",
        )

    if len({booking.venueId for booking in bookings}) > 1:
        return Valid(
            is_valid=False, message="Un incident ne peut être créé qu'à partir de réservations venant du même lieu."
        )

    if sum(booking.total_amount for booking in bookings) == 0:
        return Valid(
            is_valid=False,
            message="Impossible de créer un incident d'un montant de 0 €.",
        )

    booking_incident_already_created_or_validated = (
        finance_models.BookingFinanceIncident.query.join(finance_models.FinanceIncident)
        .filter(
            sa.and_(
                finance_models.BookingFinanceIncident.bookingId.in_([booking.id for booking in bookings]),
                finance_models.FinanceIncident.status.in_(
                    [finance_models.IncidentStatus.CREATED, finance_models.IncidentStatus.VALIDATED]
                ),
            )
        )
        .count()
    )

    if booking_incident_already_created_or_validated:
        return Valid(
            is_valid=False,
            message="Au moins une des réservations fait déjà l'objet d'un incident non annulé.",
        )

    return Valid(True)


def check_incident_collective_booking(collective_booking: educational_models.CollectiveBooking) -> Valid:
    pending_incident_on_same_booking = (
        finance_models.BookingFinanceIncident.query.join(finance_models.FinanceIncident)
        .filter(
            sa.and_(
                finance_models.BookingFinanceIncident.collectiveBookingId == collective_booking.id,
                finance_models.FinanceIncident.status.in_(
                    [finance_models.IncidentStatus.CREATED, finance_models.IncidentStatus.VALIDATED]
                ),
            )
        )
        .count()
    )
    if pending_incident_on_same_booking:
        return Valid(False, """Cette réservation fait déjà l'objet d'un incident au statut "créé" ou "validé".""")

    return Valid(True)


def check_total_amount(
    input_amount: decimal.Decimal | None,
    bookings: list[bookings_models.Booking | educational_models.CollectiveBooking],
) -> Valid:
    # Temporary: The total_amount field is optional only for multiple bookings incident (no need for total overpayment)
    if len(bookings) == 1 and not input_amount:
        return Valid(True)

    if not input_amount:
        return Valid(False, "Impossible de créer un incident d'un montant de 0 €.")

    if input_amount < 0:
        return Valid(False, "Le montant d'un incident ne peut être négatif.")

    max_incident_amount = sum(booking.total_amount for booking in bookings)
    if input_amount > max_incident_amount:
        return Valid(
            is_valid=False,
            message="Le montant de l'incident ne peut pas être supérieur au montant total des réservations sélectionnées.",
        )
    return Valid(True)
