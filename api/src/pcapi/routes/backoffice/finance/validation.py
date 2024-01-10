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
        flash("Au moins une des réservations fait déjà l'objet d'un incident non annulé.", "warning")
        return False

    return True


def check_incident_collective_booking(collective_booking: educational_models.CollectiveBooking) -> bool:
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
        flash("Cette réservation fait déjà l'objet d'un incident au statut 'créé' ou 'validé'.", "warning")
        return False

    return True


def check_total_amount(
    input_amount: decimal.Decimal | None,
    bookings: list[bookings_models.Booking | educational_models.CollectiveBooking],
    is_commercial_gesture: bool = False,
) -> bool:
    # Temporary: The total_amount field is optional only for multiple bookings incident (no need for total overpayment)
    if len(bookings) == 1 and not input_amount and not is_commercial_gesture:
        return True

    if not input_amount:
        flash("Impossible de créer un incident d'un montant de 0€.", "warning")
        return False

    if input_amount < 0:
        flash("Le montant d'un incident ne peut être négatif.", "warning")
        return False

    max_incident_amount = sum(booking.total_amount for booking in bookings)
    if is_commercial_gesture:
        for booking in bookings:
            cg_amount = booking.quantity * input_amount
            if cg_amount > (decimal.Decimal(1.20) * booking.total_amount):
                flash(
                    "Le montant de l'incident ne peut pas être supérieur à 120% du montant d'une réservation sélectionnée",
                    "warning",
                )
                return False

            if cg_amount > decimal.Decimal(300 * len(bookings)):
                flash(
                    "Le montant de l'incident ne peut JAMAIS être supérieur à 300€ par réservation.",
                    "warning",
                )
                return False
    else:
        if input_amount > max_incident_amount:
            flash(
                "Le montant de l'incident ne peut pas être supérieur au montant total des réservations sélectionnées.",
                "warning",
            )
            return False
    return True


def check_all_same_stock(bookings: list[bookings_models.Booking | educational_models.CollectiveBooking]) -> bool:
    if not bookings:
        return True

    stock_id = bookings[0].stockId
    for booking in bookings:
        if booking.stockId != stock_id:
            return False
    return True


def check_empty_deposits(
    bookings: list[bookings_models.Booking | educational_models.CollectiveBooking],
    amount_per_booking: float,
) -> bool:
    for booking in bookings:
        if booking.deposit and booking.deposit.user.wallet_balance > amount_per_booking:
            return False

    return True
