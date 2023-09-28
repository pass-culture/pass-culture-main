import decimal

from flask import flash
import sqlalchemy as sa

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models


def check_incident_bookings(bookings: list[bookings_models.Booking]) -> bool:
    venue_ids = {booking.venueId for booking in bookings}

    if len(venue_ids) > 1:
        flash("Un incident ne peut être créé qu'à partir de réservations venant du même lieu.", "warning")
        return False

    booking_incident_already_created_or_validated = (
        finance_models.BookingFinanceIncident.query.options(
            sa.orm.joinedload(finance_models.BookingFinanceIncident.incident)
        )
        .join(finance_models.FinanceIncident)
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
        flash("Au moins une des réservations fait déjà l'objet d'un incident qui n'est pas encore validé.", "warning")
        return False

    return True


def check_incident_collective_booking(collective_booking: educational_models.CollectiveBooking) -> bool:
    pending_incident_on_same_booking = (
        finance_models.BookingFinanceIncident.query.options(
            sa.orm.joinedload(finance_models.BookingFinanceIncident.incident)
        )
        .join(finance_models.FinanceIncident)
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
        flash("Cette réservation fait déjà l'objet d'un incident au statut 'créé' ou 'validé'.", "warning")
        return False

    return True


def check_total_amount(
    input_amount: decimal.Decimal | None,
    bookings: list[bookings_models.Booking | educational_models.CollectiveBooking],
    check_positive_amount: bool = True,
) -> bool:
    # Temporary: The total_amount field is optional only for multiple bookings incident (no need for total overpayment)
    if not input_amount:
        flash("Impossible de créer un incident d'un montant de 0€.", "warning")
        return False

    if check_positive_amount and input_amount < 0:
        flash("Le montant d'un incident ne peut être négatif.", "warning")
        return False

    max_incident_amount = sum(booking.total_amount for booking in bookings)
    if input_amount > max_incident_amount:
        flash(
            "Le montant de l'incident ne peut pas être supérieur au montant total des réservations sélectionnées.",
            "warning",
        )
        return False
    return True
