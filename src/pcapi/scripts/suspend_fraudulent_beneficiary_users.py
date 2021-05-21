import logging

from pcapi.core.bookings.api import cancel_booking_for_fraud
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.repository import find_cancellable_bookings_by_beneficiaries
from pcapi.core.bookings.repository import find_offers_booked_by_beneficiaries
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import User
from pcapi.repository.user_queries import find_beneficiary_users_by_email_provider
from pcapi.repository.user_queries import find_user_by_email


logger = logging.getLogger(__name__)


def suspend_fraudulent_beneficiary_users_by_email_providers(
    fraudulent_email_providers: list[str], admin_user_email: str, dry_run: bool = True
) -> None:
    fraudulent_users = []
    admin_user = find_user_by_email(admin_user_email)

    for email_provider in fraudulent_email_providers:
        fraudulent_users.extend(find_beneficiary_users_by_email_provider(email_provider))
    offers = find_offers_booked_by_beneficiaries(fraudulent_users)
    bookings_to_cancel = find_cancellable_bookings_by_beneficiaries(fraudulent_users)

    if not dry_run:
        _suspend_fraudulent_beneficiary_users(fraudulent_users, admin_user)
        _cancel_bookings_by_fraudulent_beneficiary_users(bookings_to_cancel)
        logger.info(
            "Fraudulent beneficiaries accounts suspended",
            extra={
                "beneficiaries_suspended_count": len(fraudulent_users),
                "bookings_cancelled_count": len(bookings_to_cancel),
            },
        )
    else:
        logger.info(
            "Dry run results",
            extra={
                "beneficiaries_concerned_count": len(fraudulent_users),
                "bookings_concerned_count": len(bookings_to_cancel),
            },
        )
    if len(offers) > 0:
        print(f"Suspended users booked following distinct offers {[offer.id for offer in offers]}")

    return {"fraudulent_users": fraudulent_users, "nb_cancelled_bookings": len(bookings_to_cancel)}


def _suspend_fraudulent_beneficiary_users(fraudulent_users: list[User], admin_user: User) -> None:
    for fraudulent_user in fraudulent_users:
        suspend_account(fraudulent_user, SuspensionReason.FRAUD, admin_user)


def _cancel_bookings_by_fraudulent_beneficiary_users(bookings_to_cancel: list[Booking]) -> None:
    for booking in bookings_to_cancel:
        cancel_booking_for_fraud(booking)
