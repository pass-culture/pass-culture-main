import datetime
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Blueprint
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.core.bookings import exceptions as bookings_exceptions
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.finance.api as finance_api
from pcapi.core.mails.transactional.users.birthday_to_newly_eligible_user import (
    send_birthday_age_18_email_to_newly_eligible_user,
)
from pcapi.core.offerers.repository import get_offerers_by_date_validated
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_offers
from pcapi.core.offers.repository import find_tomorrow_event_stock_ids
import pcapi.core.payments.utils as payments_utils
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.subscription.dms import api as dms_api
from pcapi.core.users import api as users_api
from pcapi.core.users.external.user_automations import (
    users_beneficiary_credit_expiration_within_next_3_months_automation,
)
from pcapi.core.users.external.user_automations import users_ex_beneficiary_automation
from pcapi.core.users.external.user_automations import users_inactive_since_30_days_automation
from pcapi.core.users.external.user_automations import users_one_year_with_pass_automation
from pcapi.core.users.external.user_automations import users_turned_eighteen_automation
from pcapi.core.users.repository import get_newly_eligible_age_18_users
from pcapi.domain.user_emails import send_withdrawal_terms_to_newly_validated_offerer
from pcapi.local_providers.provider_api import provider_api_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.notifications.push.transactional_notifications import (
    get_soon_expiring_bookings_with_offers_notification_data,
)
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.scripts.beneficiary import archive_dms_applications
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_individual_bookings
from pcapi.scripts.payment.user_recredit import recredit_underage_users
from pcapi.tasks import batch_tasks
from pcapi.workers.push_notification_job import send_tomorrow_stock_notification


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used() -> None:
    bookings_api.auto_mark_as_used_after_event()


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks() -> None:
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@cron_context
@log_cron_with_transaction
def synchronize_provider_api() -> None:
    provider_api_stocks.synchronize_stocks()


# FIXME (asaunier, 2021-05-25): This clock must be removed once every application from procedure
#  defined in DMS_NEW_ENROLLMENT_PROCEDURE_ID has been treated
@cron_context
@log_cron_with_transaction
def pc_import_dms_users_beneficiaries() -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    dms_api.import_dms_users(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


# FIXME (xordoquy, 2021-06-16): This clock must be removed once every application from procedure
#  defined in 44623 has been treated
@cron_context
@log_cron_with_transaction
def pc_import_dms_users_beneficiaries_from_old_dms() -> None:
    if not settings.IS_PROD:
        return
    procedure_id = 44623
    dms_api.import_dms_users(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@cron_context
@log_cron_with_transaction
def pc_import_beneficiaries_from_dms_v3() -> None:
    procedure_id = settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING
    dms_api.import_dms_users(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@cron_context
@log_cron_with_transaction
def pc_import_beneficiaries_from_dms_v4() -> None:
    for procedure_name, procedure_id in (
        ("v4_FR", settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_FR),
        ("v4_ET", settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_ET),
    ):
        if not procedure_id:
            logger.info("Skipping DMS %s because procedure id is empty", procedure_name)
            continue
        dms_api.import_dms_users(procedure_id)
        archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@cron_context
@log_cron_with_transaction
def pc_handle_expired_bookings() -> None:
    handle_expired_bookings()


@cron_context
@log_cron_with_transaction
def pc_notify_soon_to_be_expired_individual_bookings() -> None:
    notify_soon_to_be_expired_individual_bookings()


@cron_context
@log_cron_with_transaction
def pc_notify_newly_eligible_age_18_users() -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    for user in get_newly_eligible_age_18_users(yesterday):
        send_birthday_age_18_email_to_newly_eligible_user(user)


@cron_context
@log_cron_with_transaction
def pc_clean_expired_tokens() -> None:
    users_api.delete_expired_tokens()
    db.session.commit()


@cron_context
@log_cron_with_transaction
def pc_check_stock_quantity_consistency() -> None:
    inconsistent_stocks = check_stock_consistency()
    if inconsistent_stocks:
        logger.error("Found inconsistent stocks: %s", ", ".join([str(stock_id) for stock_id in inconsistent_stocks]))


@cron_context
@log_cron_with_transaction
def pc_send_tomorrow_events_notifications() -> None:
    stock_ids = find_tomorrow_event_stock_ids()
    for stock_id in stock_ids:
        send_tomorrow_stock_notification.delay(stock_id)


@cron_context
@log_cron_with_transaction
def pc_clean_past_draft_offers() -> None:
    delete_past_draft_offers()


@cron_context
@log_cron_with_transaction
def pc_send_withdrawal_terms_to_offerers_validated_yesterday() -> None:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    offerers_validated_yesterday = get_offerers_by_date_validated(yesterday)
    for offerer in offerers_validated_yesterday:
        send_withdrawal_terms_to_newly_validated_offerer(offerer)


@cron_context
@log_cron_with_transaction
def pc_recredit_underage_users() -> None:
    recredit_underage_users()


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.PRICE_BOOKINGS)
def price_bookings() -> None:
    finance_api.price_bookings()


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.GENERATE_CASHFLOWS_BY_CRON)
def generate_cashflows_and_payment_files() -> None:
    # FIXME (dbaty, 2011-11-18): once `get_cutoff_as_datetime()` is
    # only used here (and not by the old payment generation script
    # anymore), adapt the function to take a `datetime` object and not
    # a string.
    last_day = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    cutoff = payments_utils.get_cutoff_as_datetime(last_day)
    finance_api.generate_cashflows_and_payment_files(cutoff)


@cron_context
@log_cron_with_transaction
def pc_user_turned_eighteen_automation() -> None:
    users_turned_eighteen_automation()


@cron_context
@log_cron_with_transaction
def pc_users_beneficiary_credit_expiration_within_next_3_months_automation() -> None:
    users_beneficiary_credit_expiration_within_next_3_months_automation()


@cron_context
@log_cron_with_transaction
def pc_user_ex_beneficiary_automation() -> None:
    users_ex_beneficiary_automation()


@cron_context
@log_cron_with_transaction
def pc_users_inactive_since_30_days_automation() -> None:
    users_inactive_since_30_days_automation()


@cron_context
@log_cron_with_transaction
def pc_users_one_year_with_pass_automation() -> None:
    users_one_year_with_pass_automation()


@cron_context
@log_cron_with_transaction
def pc_notify_users_bookings_not_retrieved() -> None:
    """
    Find soon expiring bookings that will expire in exactly N days and
    send a notification to each user.
    """
    bookings = bookings_repository.get_soon_expiring_bookings(settings.SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION)
    for booking in bookings:
        try:
            notification_data = get_soon_expiring_bookings_with_offers_notification_data(booking)
            batch_tasks.send_transactional_notification_task.delay(notification_data)
        except bookings_exceptions.BookingIsExpired:
            logger.exception("Booking %d is expired", booking.id, extra={"booking": booking.id, "user": booking.userId})
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "Failed to register send_transactional_notification_task for booking %d",
                booking.id,
                extra={"booking": booking.id, "user": booking.userId},
            )


@blueprint.cli.command("clock")
def clock() -> None:
    set_tag("pcapi.app_type", "clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", day="*", hour="23")

    scheduler.add_job(synchronize_provider_api, "cron", day="*", hour="1")

    scheduler.add_job(pc_import_dms_users_beneficiaries, "cron", day="*", hour="21", minute="50")

    scheduler.add_job(pc_import_dms_users_beneficiaries_from_old_dms, "cron", day="*", hour="20", minute="50")

    scheduler.add_job(pc_import_beneficiaries_from_dms_v3, "cron", hour="*")

    scheduler.add_job(pc_import_beneficiaries_from_dms_v4, "cron", hour="*", minute="20")

    scheduler.add_job(update_booking_used, "cron", day="*", hour="0")

    scheduler.add_job(
        pc_handle_expired_bookings,
        "cron",
        day="*",
        hour="5",
    )

    scheduler.add_job(
        pc_notify_soon_to_be_expired_individual_bookings,
        "cron",
        day="*",
        hour="5",
        minute="30",
    )

    scheduler.add_job(pc_notify_newly_eligible_age_18_users, "cron", day="*", hour="3")

    scheduler.add_job(pc_clean_expired_tokens, "cron", day="*", hour="2")

    scheduler.add_job(pc_check_stock_quantity_consistency, "cron", day="*", hour="1")

    scheduler.add_job(pc_send_tomorrow_events_notifications, "cron", day="*", hour="16")

    scheduler.add_job(pc_clean_past_draft_offers, "cron", day="*", hour="20")

    scheduler.add_job(pc_send_withdrawal_terms_to_offerers_validated_yesterday, "cron", day="*", hour="6")

    scheduler.add_job(pc_recredit_underage_users, "cron", day="*", hour="7")

    scheduler.add_job(price_bookings, "cron", day="*", minute="5,15,25,35,45,55")

    scheduler.add_job(generate_cashflows_and_payment_files, "cron", day="1,16", hour="5", minute="0")

    # Marketing user automations
    scheduler.add_job(pc_user_turned_eighteen_automation, "cron", day="*", hour="4", minute="0")
    scheduler.add_job(
        pc_users_beneficiary_credit_expiration_within_next_3_months_automation, "cron", day="*", hour="4", minute="20"
    )
    scheduler.add_job(pc_user_ex_beneficiary_automation, "cron", day="*", hour="4", minute="40")
    scheduler.add_job(pc_users_inactive_since_30_days_automation, "cron", day="*", hour="5", minute="0")
    scheduler.add_job(pc_users_one_year_with_pass_automation, "cron", day="1", hour="5", minute="20")

    scheduler.add_job(pc_notify_users_bookings_not_retrieved, "cron", hour="12")

    scheduler.start()
