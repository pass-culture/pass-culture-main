from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import User
from pcapi.repository.user_queries import find_pro_users_by_email_provider
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


def suspend_fraudulent_pro_by_email_providers(
    fraudulent_email_providers: list[str], admin_user: User, dry_run: bool = True
) -> None:
    fraudulent_pros: list[User] = []

    for email_provider in fraudulent_email_providers:
        fraudulent_pros.extend(find_pro_users_by_email_provider(email_provider=email_provider))

    if not dry_run:
        for fraudulent_pro in fraudulent_pros:
            for user_offerer in fraudulent_pro.UserOfferers:
                try:
                    delete_cascade_offerer_by_id(offerer_id=user_offerer.offererId)  # type: ignore[arg-type]
                except CannotDeleteOffererWithBookingsException:
                    pass

        _suspend_fraudulent_pro_users(users=fraudulent_pros, admin_user=admin_user)
    else:
        print(f"dry run: would suspend {len(fraudulent_pros)} fraudulent pro user")
        print("dry run: all emails of fraudulent pro user:")
        for _, pros in enumerate(fraudulent_pros):
            print(f"{pros.publicName}: {pros.email}")


def _suspend_fraudulent_pro_users(users: list[User], admin_user: User) -> None:
    for fraudulent_user in users:
        suspend_account(fraudulent_user, SuspensionReason.FRAUD_SUSPICION, admin_user)
