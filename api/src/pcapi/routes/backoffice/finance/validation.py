import decimal
import typing

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.models import db


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


def _collective_booking_has_pending_incident(collective_booking: educational_models.CollectiveBooking) -> bool:
    return db.session.query(
        db.session.query(finance_models.BookingFinanceIncident)
        .join(finance_models.FinanceIncident)
        .filter(
            finance_models.BookingFinanceIncident.collectiveBookingId == collective_booking.id,
            finance_models.FinanceIncident.status.in_(
                [finance_models.IncidentStatus.CREATED, finance_models.IncidentStatus.VALIDATED]
            ),
        )
        .exists()
    ).scalar()


def _bookings_have_pending_incident(bookings: list[bookings_models.Booking]) -> bool:
    return db.session.query(
        db.session.query(finance_models.BookingFinanceIncident)
        .join(finance_models.FinanceIncident)
        .filter(
            finance_models.BookingFinanceIncident.bookingId.in_([booking.id for booking in bookings]),
            finance_models.FinanceIncident.status.in_(
                [finance_models.IncidentStatus.CREATED, finance_models.IncidentStatus.VALIDATED]
            ),
        )
        .exists()
    ).scalar()


def get_overpayment_incident_amount_interval(
    bookings: list[bookings_models.Booking],
) -> tuple[decimal.Decimal, decimal.Decimal | typing.Literal[0]]:
    return decimal.Decimal(0), sum(booking.total_amount for booking in bookings)


def get_commercial_gesture_amount_interval(
    bookings: list[bookings_models.Booking],
) -> tuple[decimal.Decimal, decimal.Decimal | typing.Literal[0]]:
    return decimal.Decimal(0), sum(booking.total_amount for booking in bookings)


def check_incident_bookings(bookings: list[bookings_models.Booking]) -> Valid:
    if not bookings:
        return Valid(
            is_valid=False,
            message="""Seules les réservations ayant le statut "remboursée" peuvent faire l'objet d'un trop perçu.""",
        )

    if len({booking.venueId for booking in bookings}) > 1:
        return Valid(
            is_valid=False,
            message="Un incident ne peut être créé qu'à partir de réservations venant du même partenaire culturel.",
        )

    if sum(booking.total_amount for booking in bookings) == 0:
        return Valid(
            is_valid=False,
            message="Impossible de créer un incident d'un montant de 0 €.",
        )

    if _bookings_have_pending_incident(bookings):
        return Valid(
            is_valid=False,
            message="Au moins une des réservations fait déjà l'objet d'un incident ou geste commercial non annulé.",
        )

    return Valid(True)


def check_commercial_gesture_bookings(bookings: list[bookings_models.Booking]) -> Valid:
    if not bookings:
        return Valid(
            is_valid=False,
            message="""Seules les réservations ayant le statut "annulée" peuvent faire l'objet d'un geste comercial.""",
        )

    if _bookings_have_pending_incident(bookings):
        return Valid(
            is_valid=False,
            message="Au moins une des réservations fait déjà l'objet d'un incident ou geste commercial non annulé.",
        )

    if len({booking.stockId for booking in bookings}) > 1:
        return Valid(
            is_valid=False,
            message="Un geste commercial ne peut concerner que des réservations faites sur un même stock.",
        )

    if len({booking.venueId for booking in bookings}) > 1:
        return Valid(
            is_valid=False,
            message="Un geste commercial ne peut être créé qu'à partir de réservations venant du même partenaire culturel.",
        )

    return Valid(True)


def check_commercial_gesture_collective_booking(collective_booking: educational_models.CollectiveBooking) -> Valid:
    if _collective_booking_has_pending_incident(collective_booking):
        return Valid(
            is_valid=False,
            message="""Cette réservation fait déjà l'objet d'un geste commercial au statut "créé" ou "validé".""",
        )

    return Valid(True)


def check_incident_collective_booking(collective_booking: educational_models.CollectiveBooking) -> Valid:
    if _collective_booking_has_pending_incident(collective_booking):
        return Valid(
            is_valid=False,
            message="""Cette réservation fait déjà l'objet d'un incident au statut "créé" ou "validé".""",
        )

    return Valid(True)


def check_total_amount(
    *,
    input_amount: decimal.Decimal | None = None,
    input_percent: decimal.Decimal | None = None,
    bookings: list[bookings_models.Booking],
) -> Valid:
    _, max_amount = get_overpayment_incident_amount_interval(bookings)

    if len(bookings) == 1:
        if not input_amount:
            return Valid(False, "Impossible de créer un incident d'un montant de 0 €.")

        if input_amount < 0:
            return Valid(False, "Le montant d'un incident ne peut être négatif.")

        if input_amount > max_amount:
            return Valid(
                is_valid=False,
                message="Le montant de l'incident ne peut pas être supérieur au montant total des réservations sélectionnées.",
            )
    else:
        if not input_percent:
            return Valid(False, "Impossible de créer un incident de 0 %%.")

    return Valid(True)


def check_commercial_gesture_total_amount(
    input_amount: decimal.Decimal, bookings: list[bookings_models.Booking]
) -> Valid:
    amount_per_booking = input_amount / sum(booking.quantity for booking in bookings)

    for booking in bookings:
        if booking.quantity * amount_per_booking > decimal.Decimal(1.20) * booking.total_amount:
            return Valid(
                is_valid=False,
                message="Le montant du geste commercial ne peut pas être supérieur à 120% du montant d'une réservation sélectionnée.",
            )

        if booking.quantity * amount_per_booking > decimal.Decimal(300) * len(bookings):
            return Valid(
                is_valid=False,
                message="Le montant du geste commercial ne peut JAMAIS être supérieur à 300€ par réservation.",
            )

        if booking.deposit and booking.deposit.user.wallet_balance > amount_per_booking:
            return Valid(
                is_valid=False,
                message="Au moins un des jeunes ayant fait une réservation a encore du crédit pour payer la réservation.",
            )
    return Valid(True)


def check_validate_or_cancel_finance_incidents(
    finance_incidents: list[finance_models.FinanceIncident], is_validation_action: bool
) -> Valid:
    if len({incident.kind for incident in finance_incidents}) != 1:
        return Valid(
            is_valid=False,
            message="Impossible de {action} des trop perçus et des gestes commerciaux dans la même action".format(
                action="valider" if is_validation_action else "rejeter"
            ),
        )

    if {incident.status for incident in finance_incidents} != {finance_models.IncidentStatus.CREATED}:
        return Valid(
            is_valid=False,
            message="""Seuls les incidents au statut "créé" peuvent faire l'objet d'une {action}""".format(
                action="validation" if is_validation_action else "annulation"
            ),
        )
    return Valid(True)
