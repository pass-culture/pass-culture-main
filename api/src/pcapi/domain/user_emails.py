from datetime import timedelta
import logging
import typing

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary import (
    send_booking_cancellation_by_beneficiary_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_pro_to_beneficiary import (
    send_booking_cancellation_by_pro_to_beneficiary_email,
)
from pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected import (
    send_duplicate_beneficiary_pre_subscription_rejected_data,
)
from pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected import (
    send_not_eligible_beneficiary_pre_subscription_rejected_data,
)
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import find_new_offerer_user_email
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.core.users import api as users_api
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.emails import beneficiary_activation
from pcapi.emails.beneficiary_booking_confirmation import retrieve_data_for_beneficiary_booking_confirmation_email
from pcapi.emails.beneficiary_expired_bookings import build_expired_bookings_recap_email_data_for_beneficiary
from pcapi.emails.beneficiary_offer_cancellation import (
    retrieve_offerer_booking_recap_email_data_after_user_cancellation,
)
from pcapi.emails.beneficiary_pre_subscription_rejected import make_dms_wrong_values_data
from pcapi.emails.beneficiary_soon_to_be_expired_bookings import (
    build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary,
)
from pcapi.emails.beneficiary_soon_to_be_expired_bookings import filter_books_bookings
from pcapi.emails.new_offer_validation import retrieve_data_for_offer_approval_email
from pcapi.emails.new_offer_validation import retrieve_data_for_offer_rejection_email
from pcapi.emails.new_offerer_validated_withdrawal_terms import (
    retrieve_data_for_new_offerer_validated_withdrawal_terms_email,
)
from pcapi.emails.offer_webapp_link import build_data_for_offer_webapp_link
from pcapi.emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email
from pcapi.emails.offerer_bookings_recap_after_deleting_stock import (
    retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation,
)
from pcapi.emails.offerer_expired_bookings import build_expired_bookings_recap_email_data_for_offerer
from pcapi.emails.pro_reset_password import retrieve_data_for_reset_password_link_to_admin_email
from pcapi.emails.pro_reset_password import retrieve_data_for_reset_password_pro_email
from pcapi.emails.user_document_validation import build_data_for_document_verification_error
from pcapi.emails.user_notification_after_stock_update import (
    retrieve_data_to_warn_user_after_stock_update_affecting_booking,
)
from pcapi.utils.mailing import make_admin_user_validation_email
from pcapi.utils.mailing import make_offerer_driven_cancellation_email_for_offerer
from pcapi.utils.mailing import make_pro_user_validation_email


logger = logging.getLogger(__name__)


def send_individual_booking_confirmation_email_to_offerer(individual_booking: IndividualBooking) -> bool:
    offerer_booking_email = individual_booking.booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = retrieve_data_for_offerer_booking_recap_email(individual_booking)
    return mails.send(recipients=[offerer_booking_email], data=data)


def send_individual_booking_confirmation_email_to_beneficiary(individual_booking: IndividualBooking) -> bool:
    data = retrieve_data_for_beneficiary_booking_confirmation_email(individual_booking)
    return mails.send(recipients=[individual_booking.user.email], data=data)


def send_user_webapp_offer_link_email(user: User, offer: Offer) -> None:
    data = build_data_for_offer_webapp_link(user, offer)
    return mails.send(recipients=[user.email], data=data)


def send_user_driven_cancellation_email_to_offerer(booking: Booking) -> bool:
    offerer_booking_email = booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking)
    return mails.send(recipients=[offerer_booking_email], data=data)


def send_offerer_driven_cancellation_email_to_offerer(booking: Booking) -> bool:
    offerer_booking_email = booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    email = make_offerer_driven_cancellation_email_for_offerer(booking)
    return mails.send(recipients=[offerer_booking_email], data=email)


def send_reset_password_email_to_pro(user: User) -> None:
    token = users_api.create_reset_password_token(user)
    data = retrieve_data_for_reset_password_pro_email(user, token)
    return mails.send(recipients=[user.email], data=data)


def send_offerer_bookings_recap_email_after_offerer_cancellation(bookings: list[Booking]) -> bool:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings)
    return mails.send(recipients=[offerer_booking_email], data=data)


def send_booking_cancellation_emails_to_user_and_offerer(
    booking: Booking,
    reason: BookingCancellationReasons,
) -> bool:
    if reason == BookingCancellationReasons.BENEFICIARY and booking.individualBooking is not None:
        send_booking_cancellation_by_beneficiary_email(booking.individualBooking)
        return send_user_driven_cancellation_email_to_offerer(booking)
    if reason == BookingCancellationReasons.OFFERER:
        send_booking_cancellation_by_pro_to_beneficiary_email(booking)
        return send_offerer_driven_cancellation_email_to_offerer(booking)
    if reason == BookingCancellationReasons.FRAUD:
        return send_user_driven_cancellation_email_to_offerer(booking)
    return True


def send_expired_bookings_recap_email_to_beneficiary(beneficiary: User, bookings: list[Booking]) -> bool:
    success = True
    books_bookings, other_bookings = filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = build_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary, bookings, booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[beneficiary.email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = build_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary, bookings, booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[beneficiary.email], data=other_bookings_data)

    return success


def send_expired_individual_bookings_recap_email_to_offerer(offerer: Offerer, bookings: list[Booking]) -> bool:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return True

    success = True
    books_bookings, other_bookings = filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = build_expired_bookings_recap_email_data_for_offerer(
            offerer, books_bookings, booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[offerer_booking_email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = build_expired_bookings_recap_email_data_for_offerer(
            offerer, other_bookings, booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[offerer_booking_email], data=other_bookings_data)

    return success


def send_pro_user_validation_email(user: User) -> bool:
    data = make_pro_user_validation_email(user)
    return mails.send(recipients=[user.email], data=data)


def send_admin_user_validation_email(user: User, token: Token) -> bool:
    data = make_admin_user_validation_email(user, token.value)
    return mails.send(recipients=[user.email], data=data)


def send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
    beneficiary: User, bookings: list[Booking]
) -> bool:
    success = True
    books_bookings, other_bookings = filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary=beneficiary,
            bookings=books_bookings,
            days_before_cancel=booking_constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
            days_from_booking=booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
            - booking_constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
        )
        success &= mails.send(recipients=[beneficiary.email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary=beneficiary,
            bookings=other_bookings,
            days_before_cancel=booking_constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
            days_from_booking=booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
            - booking_constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
        )
        success &= mails.send(recipients=[beneficiary.email], data=other_bookings_data)

    return success


def send_activation_email(user: User, reset_password_token_life_time: typing.Optional[timedelta] = None) -> bool:
    token = users_api.create_reset_password_token(user, token_life_time=reset_password_token_life_time)
    data = beneficiary_activation.get_activation_email_data(user=user, token=token)

    return mails.send(recipients=[user.email], data=data)


def send_batch_stock_postponement_emails_to_users(bookings: list[Booking]) -> bool:
    success = True
    for booking in bookings:
        success &= send_booking_postponement_emails_to_users(booking)
    return success


def send_booking_postponement_emails_to_users(booking: Booking) -> bool:
    data = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)
    return mails.send(recipients=[booking.email], data=data)


def send_rejection_email_to_beneficiary_pre_subscription(
    beneficiary_pre_subscription: BeneficiaryPreSubscription,
    beneficiary_is_eligible: bool,
) -> bool:
    if not beneficiary_is_eligible:
        return send_not_eligible_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription.email)
    return send_duplicate_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription.email)


def send_newly_eligible_user_email(user: User) -> bool:
    data = beneficiary_activation.get_newly_eligible_user_email_data(user)
    return mails.send(recipients=[user.email], data=data)


def send_reset_password_link_to_admin_email(created_user: User, admin_email: User, reset_password_link: str) -> bool:
    data = retrieve_data_for_reset_password_link_to_admin_email(created_user, reset_password_link)
    return mails.send(recipients=[admin_email], data=data)


def send_offer_validation_status_update_email(
    offer: Offer, validation_status: OfferValidationStatus, recipient_emails: list[str]
) -> bool:
    if validation_status is OfferValidationStatus.APPROVED:
        offer_data = retrieve_data_for_offer_approval_email(offer)
        return mails.send(recipients=recipient_emails, data=offer_data)

    if validation_status is OfferValidationStatus.REJECTED:
        offer_data = retrieve_data_for_offer_rejection_email(offer)
        return mails.send(recipients=recipient_emails, data=offer_data)
    return True


def send_document_verification_error_email(email: str, code: str) -> bool:
    data = build_data_for_document_verification_error(code)
    return mails.send(recipients=[email], data=data)


def send_withdrawal_terms_to_newly_validated_offerer(offerer: Offerer) -> bool:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = retrieve_data_for_new_offerer_validated_withdrawal_terms_email()
    return mails.send(recipients=[offerer_email], data=data)


def send_dms_application_emails(users: typing.Iterable[User]) -> bool:
    data = beneficiary_activation.get_dms_application_data()
    return mails.send(recipients=[user.email for user in users], data=data)


def send_dms_wrong_values_emails(
    user_email: str, postal_code: typing.Optional[str], id_piece_number: typing.Optional[str]
) -> bool:
    data = make_dms_wrong_values_data(postal_code, id_piece_number)
    return mails.send(recipients=[user_email], data=data)
