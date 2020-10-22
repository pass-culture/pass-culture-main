from typing import Callable, List, Union

from pcapi.domain.beneficiary.beneficiary import Beneficiary
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import \
    CantRegisterBeneficiary
from pcapi.core.bookings.models import Booking
from pcapi.emails.beneficiary_activation import get_activation_email_data
from pcapi.emails.beneficiary_booking_cancellation import \
    make_beneficiary_booking_cancellation_email_data
from pcapi.emails.beneficiary_booking_confirmation import \
    retrieve_data_for_beneficiary_booking_confirmation_email
from pcapi.emails.beneficiary_offer_cancellation import \
    retrieve_offerer_booking_recap_email_data_after_user_cancellation
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import \
    BeneficiaryIsNotEligible
from pcapi.emails.beneficiary_pre_subscription_rejected import \
    make_duplicate_beneficiary_pre_subscription_rejected_data, make_not_eligible_beneficiary_pre_subscription_rejected_data
from pcapi.emails.beneficiary_warning_after_pro_booking_cancellation import \
    retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation
from pcapi.emails.new_offerer_validation import \
    retrieve_data_for_new_offerer_validation_email
from pcapi.emails.offerer_attachment_validation import \
    retrieve_data_for_offerer_attachment_validation_email
from pcapi.emails.offerer_booking_recap import \
    retrieve_data_for_offerer_booking_recap_email
from pcapi.emails.offerer_bookings_recap_after_deleting_stock import \
    retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation
from pcapi.emails.offerer_ongoing_attachment import \
    retrieve_data_for_offerer_ongoing_attachment_email
from pcapi.emails.pro_reset_password import \
    retrieve_data_for_reset_password_pro_email
from pcapi.emails.pro_waiting_validation import \
    retrieve_data_for_pro_user_waiting_offerer_validation_email
from pcapi.emails.user_notification_after_stock_update import \
    retrieve_data_to_warn_user_after_stock_update_affecting_booking
from pcapi.emails.user_reset_password import \
    retrieve_data_for_reset_password_user_email
from pcapi.models import Booking, Offerer, UserOfferer, UserSQLEntity, \
    VenueSQLEntity
from pcapi.repository.user_queries import find_all_emails_of_user_offerers_admins
from pcapi.utils.mailing import ADMINISTRATION_EMAIL_ADDRESS, \
    compute_email_html_part_and_recipients, \
    make_offerer_driven_cancellation_email_for_offerer, \
    make_user_validation_email, make_venue_validated_email


def send_booking_recap_emails(booking: Booking, send_email: Callable[..., bool]) -> None:
    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    booking_email = booking.stock.offer.bookingEmail
    if booking_email:
        recipients.append(booking_email)

    data = retrieve_data_for_offerer_booking_recap_email(booking, recipients)
    send_email(data=data)


def send_booking_confirmation_email_to_beneficiary(booking: Booking, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)
    send_email(data=data)


def send_beneficiary_booking_cancellation_email(booking: Booking, send_email: Callable[..., bool]) -> None:
    data = make_beneficiary_booking_cancellation_email_data(booking)
    send_email(data=data)


def send_user_driven_cancellation_email_to_offerer(booking: Booking, send_email: Callable[..., bool]) -> None:
    recipients = _build_recipients_list(booking)
    data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(
        booking, recipients)
    send_email(data=data)


def send_offerer_driven_cancellation_email_to_offerer(booking: Booking,
                                                      send_email: Callable[..., bool]) -> None:
    offerer_email = booking.stock.offer.bookingEmail
    recipients = []
    if offerer_email:
        recipients.append(offerer_email)
    recipients.append(ADMINISTRATION_EMAIL_ADDRESS)
    email = make_offerer_driven_cancellation_email_for_offerer(booking)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(
        email['Html-part'], recipients)
    send_email(data=email)


def send_warning_to_beneficiary_after_pro_booking_cancellation(booking: Booking,
                                                               send_email: Callable[..., bool]) -> None:
    data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(
        booking)
    send_email(data=data)


def send_reset_password_email_to_user(user: UserSQLEntity, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_reset_password_user_email(user)
    send_email(data=data)


def send_reset_password_email_to_pro(user: UserSQLEntity, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_reset_password_pro_email(user)
    send_email(data=data)


def send_validation_confirmation_email_to_pro(offerer: Offerer, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_new_offerer_validation_email(offerer)
    send_email(data=data)


def send_ongoing_offerer_attachment_information_email_to_pro(user_offerer: UserOfferer,
                                                             send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_offerer_ongoing_attachment_email(user_offerer)
    send_email(data=data)


def send_attachment_validation_email_to_pro_offerer(user_offerer: UserOfferer, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_for_offerer_attachment_validation_email(
        user_offerer=user_offerer)
    send_email(data=data)


def send_batch_cancellation_emails_to_users(bookings: List[Booking], send_email: Callable[..., bool]) -> None:
    for booking in bookings:
        send_warning_to_beneficiary_after_pro_booking_cancellation(
            booking, send_email)


def send_offerer_bookings_recap_email_after_offerer_cancellation(bookings: List[Booking],
                                                                 send_email: Callable[..., bool]) -> None:
    recipients = _build_recipients_list(bookings[0])
    data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(
        bookings, recipients)
    send_email(data=data)


def send_booking_cancellation_emails_to_user_and_offerer(booking: Booking, is_offerer_cancellation: bool,
                                                         is_user_cancellation: bool, send_email: Callable[..., bool]) -> None:
    if is_user_cancellation:
        send_beneficiary_booking_cancellation_email(booking, send_email)
        send_user_driven_cancellation_email_to_offerer(booking, send_email)
    if is_offerer_cancellation:
        send_warning_to_beneficiary_after_pro_booking_cancellation(
            booking, send_email)
        send_offerer_driven_cancellation_email_to_offerer(booking, send_email)


def send_venue_validation_confirmation_email(venue: VenueSQLEntity, send_email: Callable[..., bool]) -> None:
    recipients = find_all_emails_of_user_offerers_admins(
        venue.managingOffererId)
    email = make_venue_validated_email(venue)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(
        email['Html-part'], recipients)
    send_email(data=email)


def send_user_validation_email(user: UserSQLEntity, send_email: Callable[..., bool], app_origin_url: str,
                               is_webapp: bool) -> None:
    data = make_user_validation_email(user, app_origin_url, is_webapp)
    send_email(data=data)


def send_pro_user_waiting_for_validation_by_admin_email(user: UserSQLEntity, send_email: Callable[..., bool],
                                                        offerer: Offerer) -> None:
    data = retrieve_data_for_pro_user_waiting_offerer_validation_email(
        user, offerer)
    send_email(data=data)


def send_activation_email(user: Union[UserSQLEntity, Beneficiary], send_email: Callable[..., bool]) -> None:
    data = get_activation_email_data(user=user)
    send_email(data=data)


def send_batch_stock_postponement_emails_to_users(bookings: List[Booking],
                                                  send_email: Callable[..., bool]) -> None:
    for booking in bookings:
        send_booking_postponement_emails_to_users(booking, send_email)


def send_booking_postponement_emails_to_users(booking: Booking, send_email: Callable[..., bool]) -> None:
    data = retrieve_data_to_warn_user_after_stock_update_affecting_booking(
        booking)
    send_email(data=data)


def send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription: BeneficiaryPreSubscription, error: CantRegisterBeneficiary, send_email: Callable[..., bool]) -> None:
    if isinstance(error, BeneficiaryIsNotEligible):
        data = make_not_eligible_beneficiary_pre_subscription_rejected_data(
            beneficiary_pre_subscription)
    else:
        data = make_duplicate_beneficiary_pre_subscription_rejected_data(
            beneficiary_pre_subscription)

    send_email(data=data)


def _build_recipients_list(booking: Booking) -> str:
    recipients = []
    offerer_booking_email = booking.stock.offer.bookingEmail
    if offerer_booking_email:
        recipients.append(offerer_booking_email)
    recipients.append(ADMINISTRATION_EMAIL_ADDRESS)
    return ", ".join(recipients)
