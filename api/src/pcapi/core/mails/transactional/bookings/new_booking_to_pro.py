from datetime import datetime

import sqlalchemy as sa

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_new_booking_to_pro_email_data(
    booking: Booking, first_venue_booking: bool = False
) -> models.TransactionalEmailData:
    offer = booking.stock.offer

    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == offer.venueId)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .outerjoin(
            finance_models.BankAccount,
            offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
        )
        .options(
            sa.orm.contains_eager(offerers_models.Venue.bankAccountLinks)
            .load_only(offerers_models.VenueBankAccountLink.timespan)
            .contains_eager(offerers_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.status)
        )
        .one()
    )

    if offer.isEvent:
        event_date = format_booking_date_for_email(booking)
        event_hour = format_booking_hours_for_email(booking)
    else:
        event_date = ""
        event_hour = ""

    if offer.subcategoryId in subcategories.BOOK_WITH_EAN:
        ean = offer.extraData.get("ean", "") if offer.extraData is not None else ""
        offer_subcategory = "book"
    else:
        ean = ""
        offer_subcategory = offer.subcategoryId

    if booking.stock.canHaveActivationCodes and booking.activationCode:
        can_expire = False
        is_booking_autovalidated = True
    else:
        can_expire = offer.subcategory.can_expire
        is_booking_autovalidated = False

    if first_venue_booking:
        template = TransactionalEmail.FIRST_VENUE_BOOKING_TO_PRO.value
    else:
        template = TransactionalEmail.NEW_BOOKING_TO_PRO.value

    data = models.TransactionalEmailData(
        reply_to=models.EmailInfo(
            email=booking.user.email,
            name=booking.user.full_name,
        ),
        template=template,
        params={
            "CAN_EXPIRE": can_expire,
            "COUNTERMARK": booking.token,
            "DEPARTMENT_CODE": offer.departementCode if not offer.isDigital else "numérique",
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "IS_BOOKING_AUTOVALIDATED": is_booking_autovalidated,
            "IS_EVENT": offer.isEvent,
            "IS_THING": offer.isThing,
            "IS_DIGITAL": offer.isDigital,
            "IS_EXTERNAL": booking.isExternal,
            "ISBN": ean,  # TODO: update template variable to ean
            "OFFER_NAME": offer.name,
            "OFFER_SUBCATEGORY": offer_subcategory,
            "PRICE": "Gratuit" if booking.stock.price == 0 else f"{booking.stock.price} €",
            "QUANTITY": booking.quantity,
            "USER_EMAIL": booking.user.email,
            "USER_FIRSTNAME": booking.user.firstName,
            "USER_LASTNAME": booking.user.lastName,
            "USER_PHONENUMBER": booking.user.phoneNumber or "",
            "VENUE_NAME": venue.publicName if venue.publicName else venue.name,
            "NEEDS_BANK_INFORMATION_REMINDER": venue.current_bank_account is None,
            "MUST_USE_TOKEN_FOR_PAYMENT": not (
                booking.stock.price == 0 or booking.activationCode or is_booking_autovalidated
            ),
            "WITHDRAWAL_PERIOD": (
                booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
                if offer.subcategoryId == subcategories.LIVRE_PAPIER.id
                else booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
            ),
            "FEATURES": ", ".join(booking.stock.features),
        },
    )

    return data


def send_user_new_booking_to_pro_email(booking: Booking, first_venue_booking: bool) -> None:
    if first_venue_booking:
        offerer_booking_email = booking.stock.offer.venue.bookingEmail
    else:
        offerer_booking_email = booking.stock.offer.bookingEmail

    if not offerer_booking_email:
        return
    data = get_new_booking_to_pro_email_data(booking, first_venue_booking)
    mails.send(recipients=[offerer_booking_email], data=data)
