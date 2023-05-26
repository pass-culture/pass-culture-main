from datetime import datetime

from sqlalchemy.orm import joinedload

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.categories import subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.utils.urls import build_pc_pro_offer_link


def get_first_venue_approved_offer_email_data(offer: Offer) -> models.TransactionalEmailData:
    venue = (
        Venue.query.filter(Venue.id == offer.venueId)
        .options(joinedload(Venue.bankInformation))
        .options(joinedload(Venue.reimbursement_point_links))
        .one()
    )
    now = datetime.utcnow()
    current_reimbursement_point = any(
        reimbursement_point_link
        for reimbursement_point_link in venue.reimbursement_point_links
        if now in reimbursement_point_link.timespan
    )

    return models.TransactionalEmailData(
        template=TransactionalEmail.FIRST_VENUE_APPROVED_OFFER_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "IS_EVENT": offer.isEvent,
            "IS_THING": offer.isThing,
            "IS_DIGITAL": offer.isDigital,
            "WITHDRAWAL_PERIOD": booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
            if offer.subcategoryId == subcategories.LIVRE_PAPIER.id
            else booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
            "NEEDS_BANK_INFORMATION_REMINDER": not (
                venue.hasPendingBankInformationApplication or current_reimbursement_point
            ),
        },
    )


def send_first_venue_approved_offer_email_to_pro(offer: Offer) -> bool:
    recipient = offer.venue.bookingEmail
    if not recipient:
        return True
    data = get_first_venue_approved_offer_email_data(offer)
    return mails.send(recipients=[recipient], data=data)
