from pcapi.core import mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models as mails_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import models as offers_models


def send_finance_incident_emails(
    finance_incident: finance_models.FinanceIncident,
) -> bool:
    venue = finance_incident.venue

    if not venue.current_reimbursement_point or not venue.current_reimbursement_point.bookingEmail:
        return True

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
            recipients=[venue.current_reimbursement_point.bookingEmail],
            data=data,
        )

    return True
