from datetime import datetime

import sqlalchemy as sa

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.core.offers.models import Offer
from pcapi.utils.urls import build_pc_pro_offer_link


def get_first_venue_approved_offer_email_data(offer: Offer) -> models.TransactionalEmailData:
    venue = (
        Venue.query.filter(Venue.id == offer.venueId)
        .outerjoin(
            VenueBankAccountLink,
            sa.and_(
                Venue.id == VenueBankAccountLink.venueId, VenueBankAccountLink.timespan.contains(datetime.utcnow())
            ),
        )
        .outerjoin(finance_models.BankAccount, VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id)
        .options(
            sa.orm.contains_eager(Venue.bankAccountLinks)
            .load_only(VenueBankAccountLink.timespan)
            .contains_eager(VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.status)
        )
        .one()
    )

    return models.TransactionalEmailData(
        template=TransactionalEmail.FIRST_VENUE_APPROVED_OFFER_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "IS_EVENT": offer.isEvent,
            "IS_THING": offer.isThing,
            "IS_DIGITAL": offer.isDigital,
            "WITHDRAWAL_PERIOD": (
                booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
                if offer.subcategoryId == subcategories.LIVRE_PAPIER.id
                else booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
            ),
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
            "NEEDS_BANK_INFORMATION_REMINDER": venue.current_bank_account is None,
        },
    )


def send_first_venue_approved_offer_email_to_pro(offer: Offer) -> None:
    recipient = offer.venue.bookingEmail
    if not recipient:
        return
    data = get_first_venue_approved_offer_email_data(offer)
    mails.send(recipients=[recipient], data=data)
