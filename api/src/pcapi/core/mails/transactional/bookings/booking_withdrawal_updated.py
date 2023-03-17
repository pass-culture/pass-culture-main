from sqlalchemy.orm import joinedload

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
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
        Booking.query.join(Booking.stock, Stock.offer)
        .filter(
            Offer.id == offer.id,
            Stock.isSoftDeleted.is_(False),
            Booking.isCancelled.is_(False),  # type: ignore [attr-defined]
            Booking.is_used_or_reimbursed.is_(False),  # type: ignore [attr-defined]
        )
        .options(
            joinedload(Booking.user).load_only(User.firstName, User.email),
            joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.venue).load_only(Venue.address),
            joinedload(Booking.activationCode).load_only(ActivationCode.code),
        )
    )

    mails_request = WithdrawalChangedMailRequest(
        offer_withdrawal_delay=(
            format_time_in_second_to_human_readable(offer.withdrawalDelay) if offer.withdrawalDelay else None
        ),
        offer_withdrawal_details=offer.withdrawalDetails,
        offer_withdrawal_type=getattr(offer.withdrawalType, "value", None),
        offerer_name=offer.venue.managingOfferer.name,
        venue_address=offer.venue.address,
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
) -> bool:
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
    return mails.send(recipients=recipients, data=data)


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
