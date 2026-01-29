from pcapi.core import mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models as mails_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offers import models as offers_models


def send_finance_incident_emails(finance_incident: finance_models.FinanceIncident) -> None:
    venue = finance_incident.venue

    if not venue.current_bank_account_link or not venue.bookingEmail:
        return
    booking_email = venue.bookingEmail

    if finance_incident.kind != finance_models.IncidentType.OVERPAYMENT:
        return

    offers_incidents: dict[
        offers_models.Offer | educational_models.CollectiveOffer, list[finance_models.BookingFinanceIncident]
    ] = {}
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        booking = booking_finance_incident.booking or booking_finance_incident.collectiveBooking
        assert booking  # helps mypy
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
        else:
            offer = booking.collectiveStock.collectiveOffer

        # if a given offer has multiple incidents, we need to group them under one key
        offers_incidents.setdefault(offer, []).append(booking_finance_incident)

    for offer, offer_booking_incidents in offers_incidents.items():
        if isinstance(offer, offers_models.Offer):
            if finance_incident.forceDebitNote:
                template = TransactionalEmail.RETRIEVE_DEBIT_NOTE_ON_INDIVIDUAL_BOOKINGS
            else:
                template = TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS
            data = mails_models.TransactionalEmailData(
                template=template.value,
                params={
                    "OFFER_NAME": offer.name,
                    "VENUE_NAME": venue.common_name,
                    "TOKEN_LIST": ", ".join(
                        [
                            booking_incident.booking.token
                            for booking_incident in offer_booking_incidents
                            if booking_incident.booking
                        ]
                    ),
                },
            )
        else:
            template = TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_COLLECTIVE_BOOKINGS
            data = mails_models.TransactionalEmailData(
                template=template.value,
                params={
                    "OFFER_NAME": offer.name,
                    "VENUE_NAME": venue.common_name,
                    "BOOKING_ID": ", ".join(
                        [
                            str(booking_incident.collectiveBookingId)
                            for booking_incident in offer_booking_incidents
                            if booking_incident.collectiveBookingId
                        ]
                    ),
                },
            )

        mails.send(
            recipients=[booking_email],
            data=data,
        )


def send_commercial_gesture_email(finance_incident: finance_models.FinanceIncident) -> None:
    if finance_incident.kind != finance_models.IncidentType.COMMERCIAL_GESTURE:
        return

    venue = finance_incident.venue

    if not venue.current_bank_account_link or not venue.bookingEmail:
        return
    booking_email = venue.bookingEmail

    offers_incidents: dict[
        offers_models.Offer | educational_models.CollectiveOffer, list[finance_models.BookingFinanceIncident]
    ] = {}
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        booking = booking_finance_incident.booking or booking_finance_incident.collectiveBooking
        assert booking  # helps mypy
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
        else:
            offer = booking.collectiveStock.collectiveOffer

        # if a given offer has multiple incidents, we need to group them under one key
        offers_incidents.setdefault(offer, []).append(booking_finance_incident)

    for offer, offer_booking_incidents in offers_incidents.items():
        amount = finance_utils.cents_to_full_unit(
            sum((booking_incident.due_amount_by_offerer or 0) for booking_incident in offer_booking_incidents)
        )
        data = mails_models.TransactionalEmailData(
            template=TransactionalEmail.COMMERCIAL_GESTURE_REIMBURSEMENT.value,
            params={
                "OFFER_NAME": offer.name,
                "VENUE_NAME": venue.common_name,
                "MONTANT_REMBOURSEMENT": amount,
                "FORMATTED_MONTANT_REMBOURSEMENT": format_price(amount, venue),
                "TOKEN_LIST": ", ".join(
                    [
                        booking_incident.booking.token
                        for booking_incident in offer_booking_incidents
                        if booking_incident.booking
                    ]
                ),
            },
        )

        mails.send(recipients=[booking_email], data=data)
