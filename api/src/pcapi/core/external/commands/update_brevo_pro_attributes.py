"""
Refresh all PRO attributes in Brevo.
This command should be run when a new attribute is added for pro users or when its content scope is changed.
"""

import logging
import time

import sqlalchemy as sa

from pcapi.core.external.attributes.api import get_pro_attributes
from pcapi.core.external.sendinblue import update_contact_attributes
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def get_all_booking_emails() -> set[str]:
    rows = (
        db.session.query(Venue.bookingEmail)
        .distinct()
        .filter(Venue.bookingEmail.is_not(None), Venue.bookingEmail != "")
        .all()
    )
    logger.info("[update_brevo_pro] %d booking emails", len(rows))
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
    logger.info("[update_brevo_pro] %d pro users emails", len(rows))
    return {email for email, in rows}


def update_brevo_pro_attributes(start_index: int = 0) -> None:
    all_emails = get_all_booking_emails()
    all_emails |= get_all_pro_users_emails()

    logger.info("[update_brevo_pro] Total: %d distinct emails", len(all_emails))

    # Sort so that we can resume from somewhere in case the script is paused or fails
    all_emails_to_process = sorted(all_emails)[start_index:]

    logger.info("[update_brevo_pro] %d emails to process", len(all_emails_to_process))

    errors = []

    for i, email in enumerate(all_emails_to_process):
        logger.info("[update_brevo_pro] (%d/%d) %s", start_index + i + 1, len(all_emails), email)

        # In this script we don't need to delay using a Google Cloud Task because:
        # - this would create too many tasks,
        # - emails are already unique in the set, so no de-duplication is required,
        # - script does not need to return quickly, so synchronous call is ok.
        try:
            attributes = get_pro_attributes(email)
            update_contact_attributes(email, attributes, asynchronous=False)
        except Exception as exc:
            logger.exception("[update_brevo_pro] ***** Exception while processing %s: %s", email, exc)
            errors.append(email)

        # Avoid flooding our database and Brevo API!
        time.sleep(0.1)

    logger.info("[update_brevo_pro] Completed with %d errors", len(errors))
    for email in errors:
        logger.info("[update_brevo_pro] - %s", email)
