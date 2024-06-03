"""
Refresh all PRO attributes in Sendinblue.
This command should be run when a new attribute is added for pro users or when its content scope is changed.
"""

import time

import sqlalchemy as sa

from pcapi.core.external.attributes.api import get_pro_attributes
from pcapi.core.external.sendinblue import update_contact_attributes
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User
from pcapi.models import db


def get_all_booking_emails() -> set[str]:
    rows = (
        db.session.query(Venue.bookingEmail)
        .distinct()
        .filter(Venue.bookingEmail.is_not(None), Venue.bookingEmail != "")
        .all()
    )
    print(f"{len(rows)} booking emails")
    return {email for email, in rows}


def get_all_pro_users_emails() -> set[str]:
    rows = (
        db.session.query(User.email)
        .filter(
            User.isActive,
            sa.or_(User.has_pro_role, User.has_non_attached_pro_role),  # type: ignore[type-var]
            sa.not_(User.has_admin_role),
        )
        .all()
    )
    print(f"{len(rows)} pro users emails")
    return {email for email, in rows}


def sendinblue_update_all_pro_attributes(start_index: int = 0) -> None:
    all_emails = get_all_booking_emails()
    all_emails |= get_all_pro_users_emails()

    print(f"Total: {len(all_emails)} distinct emails")

    # Sort so that we can resume from somewhere in case the script is paused or fails
    all_emails_to_process = sorted(all_emails)[start_index:]

    print(f"{len(all_emails_to_process)} emails to process")

    errors = []

    for i, email in enumerate(all_emails_to_process):
        print(f"({start_index + i + 1}/{len(all_emails)}) {email}")

        # In this script we don't need to delay using a Google Cloud Task because:
        # - this would create too many tasks,
        # - emails are already unique in the set, so no de-duplication is required,
        # - script does not need to return quickly, so synchronous call is ok.
        try:
            attributes = get_pro_attributes(email)
            update_contact_attributes(email, attributes, asynchronous=False)
        except Exception as e:  # pylint: disable=broad-except
            print(f"***** Exception while processing {email}: {e}")
            errors.append(email)

        # Avoid flooding our database and Sendinblue API!
        time.sleep(0.1)

    print(f"Completed with {len(errors)} errors")
    for email in errors:
        print(f" - {email}")
