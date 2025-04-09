import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core import mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.tasks.mails_tasks import send_withdrawal_detail_changed_emails
from pcapi.tasks.serialization.mails_tasks import WithdrawalChangedMailBookingDetail
from pcapi.tasks.serialization.mails_tasks import WithdrawalChangedMailRequest
from pcapi.utils.date import format_time_in_second_to_human_readable


def send_email_for_each_ongoing_booking(offer: offers_models.Offer) -> None:
    ongoing_bookings = (
        bookings_models.Booking.query.join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .filter(
            offers_models.Offer.id == offer.id,
            offers_models.Stock.isSoftDeleted.is_(False),
            offers_models.Stock.beginningDatetime.is_(None) | (offers_models.Stock.beginningDatetime > sa.func.now()),
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        )
        .options(
            sa_orm.joinedload(bookings_models.Booking.user).load_only(
                users_models.User.firstName, users_models.User.email
            ),
            sa_orm.joinedload(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.withdrawalDelay,
                offers_models.Offer.withdrawalDetails,
                offers_models.Offer.withdrawalType,
            )
            .joinedload(offers_models.Offer.venue)
            .load_only(offerers_models.Venue.street),
            sa_orm.joinedload(bookings_models.Booking.activationCode).load_only(offers_models.ActivationCode.code),
            sa_orm.joinedload(bookings_models.Booking.stock)
            .load_only(offers_models.Stock.id)
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.id)
            .joinedload(offers_models.Offer.offererAddress)
            .options(
                sa_orm.joinedload(offerers_models.OffererAddress.address),
                sa_orm.selectinload(offerers_models.OffererAddress.venues),
            ),
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
                offer_address=booking.stock.offer.fullAddress,
            )
        )
    send_withdrawal_detail_changed_emails.delay(payload=mails_request)


def send_booking_withdrawal_updated(
    *,
    recipients: list[str],
    user_first_name: str,
    offer_name: str,
    offer_token: str,
    offer_withdrawal_delay: str | None,
    offer_withdrawal_details: str | None,
    offer_withdrawal_type: str | None,
    offerer_name: str,
    venue_address: str,
    offer_address: str | None,
) -> None:
    data = get_booking_withdrawal_updated_email_data(
        user_first_name=user_first_name,
        offer_name=offer_name,
        offer_token=offer_token,
        offer_withdrawal_delay=offer_withdrawal_delay,
        offer_withdrawal_details=offer_withdrawal_details,
        offer_withdrawal_type=offer_withdrawal_type,
        offerer_name=offerer_name,
        venue_address=venue_address,
        offer_address=offer_address,
    )
    mails.send(recipients=recipients, data=data)


def get_booking_withdrawal_updated_email_data(
    *,
    user_first_name: str,
    offer_name: str,
    offer_token: str,
    offer_withdrawal_delay: str | None,
    offer_withdrawal_details: str | None,
    offer_withdrawal_type: str | None,
    offerer_name: str,
    venue_address: str,
    offer_address: str | None,
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
            "OFFER_ADDRESS": offer_address,
        },
    )
