import datetime
import decimal
import logging
from operator import attrgetter

from flask import url_for
from markupsafe import Markup

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.utils import access_control
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def _get_token_link(booking: bookings_models.Booking) -> str:
    if not access_control.has_current_user_permission(perm_models.Permissions.READ_BOOKINGS):
        return booking.token
    return Markup('<a class="link-primary" href="{url}">{token}</a>').format(
        token=booking.token,
        url=url_for("backoffice_web.individual_bookings.list_individual_bookings", q=booking.token),
    )


def _get_incident_link(finance_incident: finance_models.FinanceIncident) -> str:
    if not access_control.has_current_user_permission(perm_models.Permissions.READ_INCIDENTS):
        return f"#{finance_incident.id}"
    return Markup('<a class="link-primary" href="{url}">#{incident_id}</a>').format(
        incident_id=finance_incident.id,
        url=url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id),
    )


class ReportRow:
    description: str
    date: datetime.datetime
    amount: decimal.Decimal
    remaining_credit: decimal.Decimal | None = None


class ReportDepositRow(ReportRow):
    def __init__(self, deposit: finance_models.Deposit):
        self.description = Markup("Attribution d'un {deposit_type}").format(
            deposit_type=filters.format_deposit_type(deposit)
        )
        self.date = deposit.dateCreated
        initial_recredit = deposit.initial_recredit
        self.amount = deposit.amount - sum(
            recredit.amount for recredit in deposit.recredits if recredit != initial_recredit
        )


class ReportRecreditRow(ReportRow):
    def __init__(self, recredit: finance_models.Recredit):
        self.description = filters.format_recredit_type(recredit)
        self.date = recredit.dateCreated
        self.amount = recredit.amount


class ReportDepositExpirationRow(ReportRow):
    def __init__(self, deposit: finance_models.Deposit, bookings: list[bookings_models.Booking]):
        self.description = Markup("Expiration d'un {deposit_type}").format(
            deposit_type=filters.format_deposit_type(deposit)
        )
        assert deposit.expirationDate is not None
        self.date = deposit.expirationDate
        self.amount = -deposit.amount
        for booking in bookings:
            if booking.depositId != deposit.id:
                continue
            if (
                booking.isCancelled
                and booking.cancellationDate is not None
                and booking.cancellationDate < deposit.expirationDate
            ):
                continue
            if validated_booking_incident := booking.validated_booking_incident:
                if validation_date := validated_booking_incident.incident.validation_date:
                    if validation_date < deposit.expirationDate:
                        self.amount += decimal.Decimal(validated_booking_incident.newTotalAmount) / decimal.Decimal(100)
                        continue
            self.amount += booking.total_amount


class ReportBookingRow(ReportRow):
    def __init__(self, booking: bookings_models.Booking):
        self.description = Markup("Réservation {token}").format(token=_get_token_link(booking))
        self.date = booking.dateCreated
        self.amount = -booking.total_amount


class ReportCancelBookingRow(ReportRow):
    def __init__(self, booking: bookings_models.Booking):
        self.description = Markup("Annulation de la réservation {token}").format(token=_get_token_link(booking))
        assert booking.cancellationDate is not None
        self.date = booking.cancellationDate
        if (
            booking.deposit is None
            or booking.deposit.expirationDate is None
            or booking.cancellationDate < booking.deposit.expirationDate
        ):
            self.amount = booking.total_amount
        else:
            self.description += Markup(" (crédit expiré depuis le {date})").format(
                date=filters.format_date(booking.deposit.expirationDate)
            )
            self.amount = decimal.Decimal(0)


class ReportIncidentRow(ReportRow):
    def __init__(self, booking_finance_incident: finance_models.BookingFinanceIncident):
        assert booking_finance_incident.booking is not None  # helps mypy
        incident = booking_finance_incident.incident
        self.description = Markup("Incident {incident_id} lié à la réservation {token}").format(
            incident_id=_get_incident_link(incident), token=_get_token_link(booking_finance_incident.booking)
        )
        validation_date = incident.validation_date
        assert validation_date is not None  # helps mypy
        self.date = validation_date
        self.amount = booking_finance_incident.booking.total_amount - decimal.Decimal(
            booking_finance_incident.newTotalAmount
        ) / decimal.Decimal("100")


class Report:
    is_consistent: bool = True
    _rows: list[ReportRow]

    def __init__(self, user: users_models.User, credit: users_models.DomainsCredit | None):
        rows: list[ReportRow] = []

        for deposit in user.deposits:
            rows.append(ReportDepositRow(deposit))
            initial_recredit = deposit.initial_recredit
            for recredit in deposit.recredits:
                if recredit != initial_recredit:
                    rows.append(ReportRecreditRow(recredit))
            if deposit.expirationDate and deposit.expirationDate < date_utils.get_naive_utc_now():
                rows.append(ReportDepositExpirationRow(deposit, user.userBookings))

        for booking in user.userBookings:
            rows.append(ReportBookingRow(booking))
            if booking.isCancelled:
                rows.append(ReportCancelBookingRow(booking))
            else:
                for booking_finance_incident in booking.incidents:
                    if booking_finance_incident.is_partial and booking_finance_incident.incident.status in (
                        finance_models.IncidentStatus.VALIDATED,
                        finance_models.IncidentStatus.INVOICED,
                    ):
                        rows.append(ReportIncidentRow(booking_finance_incident))

        rows = sorted(rows, key=attrgetter("date"), reverse=True)

        remaining = decimal.Decimal(0)
        for row in reversed(rows):
            remaining += row.amount
            row.remaining_credit = remaining

        if credit and credit.all.remaining != remaining:
            self.is_consistent = False
            logger.error(
                "Wrong remaining credit at the end of the report",
                extra={
                    "user_id": user.id,
                    "credit.all.remaining": credit.all.remaining,
                    "report.remaining": remaining,
                },
            )

        self._rows = rows

    @property
    def length(self) -> int:
        return len(self._rows)

    @property
    def rows(self) -> list[ReportRow]:
        return self._rows
