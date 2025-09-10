import logging
import typing
from itertools import groupby
from operator import attrgetter

import click

import pcapi.core.mails.transactional as transactional_mails
import pcapi.utils.cron as cron_decorators
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.bookings.external import booking_notifications
from pcapi.core.educational.api import booking as educational_booking_api
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("archive_old_bookings")
@cron_decorators.log_cron_with_transaction
def archive_old_bookings() -> None:
    api.archive_old_bookings()


@blueprint.cli.command("recompute_dnBookedQuantity")
@click.argument("stock-ids", type=int, nargs=-1, required=True)
@click.option("--not-dry", is_flag=True)
def recompute_dnBookedQuantity(stock_ids: list[int], not_dry: bool = False) -> None:
    api.recompute_dnBookedQuantity(stock_ids)
    if not_dry:
        db.session.commit()
    else:
        db.session.rollback()


@blueprint.cli.command("update_booking_used")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used() -> None:
    """Automatically mark as used bookings that correspond to events that
    have happened (with a delay).
    """
    api.auto_mark_as_used_after_event()


@blueprint.cli.command("cancel_unstored_external_bookings")
@cron_decorators.log_cron_with_transaction
def cancel_unstored_external_bookings() -> None:
    api.cancel_unstored_external_bookings()


@blueprint.cli.command("cancel_ems_external_bookings")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.EMS_CANCEL_PENDING_EXTERNAL_BOOKING)
def cancel_ems_external_bookings() -> None:
    api.cancel_ems_external_bookings()


@blueprint.cli.command("handle_expired_bookings")
@cron_decorators.log_cron_with_transaction
def handle_expired_bookings() -> None:
    bookings_api.handle_expired_individual_bookings()
    educational_booking_api.handle_expired_collective_bookings()


@blueprint.cli.command("notify_soon_to_be_expired_individual_bookings")
@cron_decorators.log_cron_with_transaction
def notify_soon_to_be_expired_individual_bookings() -> None:
    _notify_soon_to_be_expired_individual_bookings()  # useful for tests


def _notify_soon_to_be_expired_individual_bookings() -> None:
    logger.info("[notify_users_of_soon_to_be_expired_bookings] Start")

    expired_individual_bookings_grouped_by_user = {
        user: list(booking)
        for user, booking in groupby(
            bookings_repository.find_soon_to_be_expiring_individual_bookings_ordered_by_user(),
            attrgetter("user"),
        )
    }

    notified_users = []

    for user, bookings in expired_individual_bookings_grouped_by_user.items():
        transactional_mails.send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(user, bookings)
        notified_users.append(user)

    logger.info(
        "[notify_soon_to_be_expired_individual_bookings] %d Users have been notified: %s",
        len(notified_users),
        notified_users,
    )

    logger.info("[notify_soon_to_be_expired_individual_bookings] End")


@blueprint.cli.command("send_today_events_notifications_metropolitan_france")
@cron_decorators.log_cron_with_transaction
def send_today_events_notifications_metropolitan_france_command() -> None:
    """
    Find bookings that occur today in metropolitan France and send
    notification to all the user to remind them of the event to remind
    the users of the incoming event
    """
    booking_notifications.send_today_events_notifications_metropolitan_france()


@blueprint.cli.command("send_today_events_notifications_overseas_france")
@cron_decorators.log_cron_with_transaction
@click.option("--utc-mean-offset", help="UTC offset to use (can be negative)", type=int, required=True)
@click.argument("departments", nargs=-1)
def send_today_events_notifications_overseas_france(utc_mean_offset: int, departments: typing.Iterable[str]) -> None:
    """
    Find bookings (grouped by stocks) that occur today in overseas
    France departments and send notifications to remind the users
    of the incoming event
    """
    booking_notifications.send_today_events_notifications_overseas(
        utc_mean_offset=utc_mean_offset, departments=departments
    )


@blueprint.cli.command("send_email_reminder_tomorrow_event_to_beneficiaries")
@cron_decorators.log_cron_with_transaction
def send_email_reminder_tomorrow_event_to_beneficiaries() -> None:
    _send_email_reminder_tomorrow_event_to_beneficiaries()  # useful for tests


def _send_email_reminder_tomorrow_event_to_beneficiaries() -> None:
    """Triggers email reminder to beneficiaries for none digitals events happening tomorrow"""
    bookings = bookings_repository.find_individual_bookings_event_happening_tomorrow_query()
    for booking in bookings:
        try:
            transactional_mails.send_individual_booking_event_reminder_email_to_beneficiary(booking)
        except Exception:
            logger.exception(
                "Could not send email reminder tomorrow event to beneficiary",
                extra={
                    "BookingId": booking.id,
                    "userId": booking.userId,
                },
            )


@blueprint.cli.command("notify_users_bookings_not_retrieved")
@cron_decorators.log_cron_with_transaction
def notify_users_bookings_not_retrieved_command() -> None:
    """
    Find soon expiring bookings that will expire in exactly N days and
    send a notification to each user.
    """
    booking_notifications.notify_users_bookings_not_retrieved()
