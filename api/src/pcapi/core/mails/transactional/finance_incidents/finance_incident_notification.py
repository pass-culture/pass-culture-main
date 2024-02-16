from pcapi.core import mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models as mails_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import models as offers_models
from pcapi.models.feature import FeatureToggle


def send_finance_incident_emails(finance_incident: finance_models.FinanceIncident) -> None:
    venue = finance_incident.venue

    if not FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
        if not venue.current_reimbursement_point or not venue.current_reimbursement_point.bookingEmail:
            return
        booking_email = venue.current_reimbursement_point.bookingEmail
    else:
        if not venue.current_bank_account_link or not venue.bookingEmail:
            return
        booking_email = venue.bookingEmail

    if finance_incident.forceDebitNote or finance_incident.kind != finance_models.IncidentType.OVERPAYMENT:
        return

    offers = set()
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        # this email refers to a cancelled booking (which is the case in total overpayment incidents only)
        if booking_finance_incident.is_partial:
            continue

        booking = booking_finance_incident.booking or booking_finance_incident.collectiveBooking
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
        else:
            offer = booking.collectiveStock.collectiveOffer

        offers.add(offer)

    for offer in offers:
        if isinstance(offer, offers_models.Offer):
            template = TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS
        else:
            template = TransactionalEmail.RETRIEVE_INCIDENT_AMOUNT_ON_COLLECTIVE_BOOKINGS

        data = mails_models.TransactionalEmailData(
            template=template.value,
            params={"OFFER_NAME": offer.name, "VENUE_NAME": venue.common_name},
        )

        mails.send(
            recipients=[booking_email],
            data=data,
        )


def send_commercial_gesture_email(finance_incident: finance_models.FinanceIncident) -> None:
    if finance_incident.kind != finance_models.IncidentType.COMMERCIAL_GESTURE:
        return

    venue = finance_incident.venue

    if not FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
        if not venue.current_reimbursement_point or not venue.current_reimbursement_point.bookingEmail:
            return
        booking_email = venue.current_reimbursement_point.bookingEmail
    else:
        if not venue.current_bank_account_link or not venue.bookingEmail:
            return
        booking_email = venue.bookingEmail

    offers_incidents: dict[tuple, list[finance_models.BookingFinanceIncident]] = {}
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        booking = booking_finance_incident.booking or booking_finance_incident.collectiveBooking
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
        else:
            offer = booking.collectiveStock.collectiveOffer

        # if a given offer has multiple incidents, we need to group them under one key
        offers_incidents.setdefault((offer.id, offer.name), []).extend([booking_finance_incident])

    for (_, offer_name), offer_booking_incidents in offers_incidents.items():
        data = mails_models.TransactionalEmailData(
            template=TransactionalEmail.COMMERCIAL_GESTURE_REIMBURSEMENT.value,
            params={
                "OFFER_NAME": offer_name,
                "VENUE_NAME": venue.common_name,
                "MONTANT_REMBOURSEMENT": finance_utils.to_euros(
                    sum(booking_incident.newTotalAmount for booking_incident in offer_booking_incidents)
                ),
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
