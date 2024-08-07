import sqlalchemy as sa

from pcapi.core import mails
import pcapi.core.bookings.models as bookings_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.tasks.mails_tasks import send_withdrawal_detail_changed_emails
from pcapi.tasks.serialization.mails_tasks import WithdrawalChangedMailBookingDetail
from pcapi.tasks.serialization.mails_tasks import WithdrawalChangedMailRequest
from pcapi.utils.date import format_time_in_second_to_human_readable


def send_email_for_each_ongoing_booking(offer: Offer) -> None:
    ongoing_bookings = (
        bookings_models.Booking.query.join(bookings_models.Booking.stock)
        .join(Stock.offer)
        .filter(
            Offer.id == offer.id,
            Stock.isSoftDeleted.is_(False),
            Stock.beginningDatetime.is_(None) | (Stock.beginningDatetime > sa.func.now()),
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        )
        .options(
            sa.orm.joinedload(bookings_models.Booking.user).load_only(User.firstName, User.email),
            sa.orm.joinedload(bookings_models.Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
            .load_only(Venue.street),
            sa.orm.joinedload(bookings_models.Booking.activationCode).load_only(ActivationCode.code),
        )
    )

    venue_address = " ".join(filter(None, (offer.venue.street, offer.venue.postalCode, offer.venue.city)))
    mails_request = WithdrawalChangedMailRequest(
        offer_withdrawal_delay=(
            format_time_in_second_to_human_readable(offer.withdrawalDelay) if offer.withdrawalDelay else None
        ),
        offer_withdrawal_details=offer.withdrawalDetails,
        offer_withdrawal_type=getattr(offer.withdrawalType, "value", None),
        offerer_name=offer.venue.managingOfferer.name,
        venue_address=venue_address,
        bookers=[],
    )
    for booking in ongoing_bookings:
        mails_request.bookers.append(
            WithdrawalChangedMailBookingDetail(
                recipients=[booking.user.email],
                user_first_name=booking.user.firstName,
                offer_name=offer.name,
                offer_token=booking.activationCode.code if booking.activationCode else booking.token,
            )
        )
    send_withdrawal_detail_changed_emails.delay(mails_request)


def send_booking_withdrawal_updated(
    recipients: list[str],
    user_first_name: str,
    offer_name: str,
    offer_token: str,
    offer_withdrawal_delay: str | None,
    offer_withdrawal_details: str | None,
    offer_withdrawal_type: str | None,
    offerer_name: str,
    venue_address: str,
) -> None:
    data = get_booking_withdrawal_updated_email_data(
        user_first_name,
        offer_name,
        offer_token,
        offer_withdrawal_delay,
        offer_withdrawal_details,
        offer_withdrawal_type,
        offerer_name,
        venue_address,
    )
    mails.send(recipients=recipients, data=data)


def get_booking_withdrawal_updated_email_data(
    user_first_name: str,
    offer_name: str,
    offer_token: str,
    offer_withdrawal_delay: str | None,
    offer_withdrawal_details: str | None,
    offer_withdrawal_type: str | None,
    offerer_name: str,
    venue_address: str,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_WITHDRAWAL_UPDATED_BY_PRO.value,
        params={
            "OFFER_NAME": offer_name,
            "OFFER_TOKEN": offer_token,
            "OFFER_WITHDRAWAL_DELAY": offer_withdrawal_delay,
            "OFFER_WITHDRAWAL_DETAILS": offer_withdrawal_details,
            "OFFER_WITHDRAWAL_TYPE": offer_withdrawal_type,
            "OFFERER_NAME": offerer_name,
            "USER_FIRST_NAME": user_first_name,
            "VENUE_ADDRESS": venue_address,
        },
    )
