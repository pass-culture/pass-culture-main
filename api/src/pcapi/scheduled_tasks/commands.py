import datetime
import logging

import sqlalchemy.orm as sqla_orm

from pcapi import settings
from pcapi.core.bookings import exceptions as bookings_exceptions
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.bookings.repository import find_educational_bookings_done_yesterday
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.utils as finance_utils
import pcapi.core.fraud.api as fraud_api
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    send_individual_booking_event_reminder_email_to_beneficiary,
)
from pcapi.core.mails.transactional.educational.eac_satisfaction_study_to_pro import (
    send_eac_satisfaction_study_email_to_pro,
)
from pcapi.core.mails.transactional.pro.reminder_before_event_to_pro import send_reminder_7_days_before_event_to_pro
from pcapi.core.mails.transactional.users.birthday_to_newly_eligible_user import (
    send_birthday_age_18_email_to_newly_eligible_user,
)
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_collective_offers
from pcapi.core.offers.repository import delete_past_draft_offers
from pcapi.core.offers.repository import find_event_stocks_happening_in_x_days
from pcapi.core.offers.repository import find_today_event_stock_ids_metropolitan_france
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import api as users_api
import pcapi.core.users.constants as users_constants
from pcapi.core.users.external import user_automations
from pcapi.core.users.repository import get_newly_eligible_age_18_users
from pcapi.local_providers.provider_api import provider_api_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.notifications.push.transactional_notifications import (
    get_soon_expiring_bookings_with_offers_notification_data,
)
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.scripts.beneficiary import archive_dms_applications
from pcapi.scripts.beneficiary.handle_inactive_dms_applications import handle_inactive_dms_applications
from pcapi.scripts.beneficiary.import_dms_accepted_applications import import_dms_accepted_applications
from pcapi.scripts.booking import handle_expired_bookings as handle_expired_bookings_module
from pcapi.scripts.booking import notify_soon_to_be_expired_bookings
from pcapi.scripts.payment import user_recredit
from pcapi.scripts.subscription.handle_deleted_dms_applications import handle_deleted_dms_applications
from pcapi.tasks import batch_tasks
from pcapi.utils.blueprint import Blueprint
from pcapi.workers.push_notification_job import send_today_stock_notification

from .clock import DMS_OLD_PROCEDURE_ID


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("update_booking_used")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used() -> None:
    """Automatically mark as used bookings that correspond to events that
    have happened (with a delay).
    """
    bookings_api.auto_mark_as_used_after_event()


@blueprint.cli.command("synchronize_allocine_stocks")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks() -> None:
    """Launch AlloCine synchronization."""
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@blueprint.cli.command("synchronize_provider_api")
@log_cron_with_transaction
def synchronize_provider_api() -> None:
    """Launch Providers (excepts AlloCine) synchronization."""
    provider_api_stocks.synchronize_stocks()


# FIXME (asaunier, 2021-05-25): This clock must be removed once every application from procedure
#  defined in DMS_NEW_ENROLLMENT_PROCEDURE_ID has been treated
@blueprint.cli.command("import_dms_users_beneficiaries")
@log_cron_with_transaction
def import_dms_users_beneficiaries() -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    import_dms_accepted_applications(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


# FIXME (xordoquy, 2021-06-16): This clock must be removed once every application from procedure
#  defined in 44623 has been treated
@blueprint.cli.command("import_dms_users_beneficiaries_from_old_dms")
@log_cron_with_transaction
def import_dms_users_beneficiaries_from_old_dms() -> None:
    if not settings.IS_PROD:
        return
    procedure_id = DMS_OLD_PROCEDURE_ID
    import_dms_accepted_applications(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@blueprint.cli.command("import_beneficiaries_from_dms_v3")
@log_cron_with_transaction
def import_beneficiaries_from_dms_v3() -> None:
    procedure_id = settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING
    import_dms_accepted_applications(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@blueprint.cli.command("import_beneficiaries_from_dms_v4")
@log_cron_with_transaction
def import_beneficiaries_from_dms_v4() -> None:
    for procedure_name, procedure_id in (
        ("v4_FR", settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_FR),
        ("v4_ET", settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_ET),
    ):
        if not procedure_id:
            logger.info("Skipping DMS %s because procedure id is empty", procedure_name)
            continue
        import_dms_accepted_applications(procedure_id)
        archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@blueprint.cli.command("handle_expired_bookings")
@log_cron_with_transaction
def handle_expired_bookings() -> None:
    handle_expired_bookings_module.handle_expired_bookings()


@blueprint.cli.command("notify_soon_to_be_expired_individual_bookings")
@log_cron_with_transaction
def notify_soon_to_be_expired_individual_bookings() -> None:
    notify_soon_to_be_expired_bookings.notify_soon_to_be_expired_individual_bookings()


@blueprint.cli.command("notify_newly_eligible_age_18_users")
@log_cron_with_transaction
def notify_newly_eligible_age_18_users() -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    for user in get_newly_eligible_age_18_users(yesterday):
        send_birthday_age_18_email_to_newly_eligible_user(user)


@blueprint.cli.command("clean_expired_tokens")
@log_cron_with_transaction
def clean_expired_tokens() -> None:
    users_api.delete_expired_tokens()
    db.session.commit()


@blueprint.cli.command("check_stock_quantity_consistency")
@log_cron_with_transaction
def check_stock_quantity_consistency() -> None:
    inconsistent_stocks = check_stock_consistency()
    if inconsistent_stocks:
        logger.error("Found inconsistent stocks: %s", ", ".join([str(stock_id) for stock_id in inconsistent_stocks]))


@blueprint.cli.command("send_yesterday_event_offers_notifications")
@log_cron_with_transaction
def send_yesterday_event_offers_notifications() -> None:
    """Triggers email to be sent for yesterday events"""
    for educational_booking in find_educational_bookings_done_yesterday():
        send_eac_satisfaction_study_email_to_pro(educational_booking)


@blueprint.cli.command("send_today_events_notifications_metropolitan_france")
@log_cron_with_transaction
def send_today_events_notifications_metropolitan_france() -> None:
    """
    Find bookings (grouped by stocks) that occur today in metropolitan
    France but not the morning (11h UTC -> 12h/13h local time), and
    send notification to all the user to remind them of the event.
    """
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=11))
    stock_ids = find_today_event_stock_ids_metropolitan_france(today_min)

    for stock_id in stock_ids:
        send_today_stock_notification.delay(stock_id)


@blueprint.cli.command("send_email_reminder_7_days_before_event")
@log_cron_with_transaction
def send_email_reminder_7_days_before_event() -> None:
    """Triggers email to be sent for events happening in 7 days"""
    stocks = find_event_stocks_happening_in_x_days(7).options(sqla_orm.joinedload(Stock.offer).joinedload(Offer.venue))
    for stock in stocks:
        send_reminder_7_days_before_event_to_pro(stock)


@blueprint.cli.command("send_email_reminder_tomorrow_event_to_beneficiaries")
@log_cron_with_transaction
def send_email_reminder_tomorrow_event_to_beneficiaries() -> None:
    """Triggers email reminder to beneficiaries for none digitals events happening tomorrow"""
    individual_bookings = bookings_repository.find_individual_bookings_event_happening_tomorrow_query()
    for individual_booking in individual_bookings:
        send_individual_booking_event_reminder_email_to_beneficiary(individual_booking)


@blueprint.cli.command("clean_past_draft_offers")
@log_cron_with_transaction
def clean_past_draft_offers() -> None:
    """Deletes past offers and past collective offers that are in draft status"""
    delete_past_draft_offers()
    delete_past_draft_collective_offers()


@blueprint.cli.command("recredit_underage_users")
@log_cron_with_transaction
def recredit_underage_users() -> None:
    user_recredit.recredit_underage_users()


@blueprint.cli.command("price_bookings")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.PRICE_BOOKINGS)
def price_bookings() -> None:
    """Price bookings that have been recently marked as used."""
    finance_api.price_bookings()


@blueprint.cli.command("generate_cashflows_and_payment_files")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.GENERATE_CASHFLOWS_BY_CRON)
def generate_cashflows_and_payment_files() -> None:
    last_day = datetime.date.today() - datetime.timedelta(days=1)
    cutoff = finance_utils.get_cutoff_as_datetime(last_day)
    finance_api.generate_cashflows_and_payment_files(cutoff)


@blueprint.cli.command("users_turned_eighteen_automation")
@log_cron_with_transaction
def users_turned_eighteen_automation() -> None:
    """Includes all young users who will turn 18 exactly 30 days later in "jeunes-18-m-1" list.
    This command is meant to be called every day."""
    user_automations.users_turned_eighteen_automation()


@blueprint.cli.command("users_beneficiary_credit_expiration_within_next_3_months_automation")
@log_cron_with_transaction
def users_beneficiary_credit_expiration_within_next_3_months_automation() -> None:
    """Includes all young user whose pass expires in the next 3 months in "jeunes-expiration-M-3" list.
    This command is meant to be called every day."""
    user_automations.users_beneficiary_credit_expiration_within_next_3_months_automation()


@blueprint.cli.command("users_ex_beneficiary_automation")
@log_cron_with_transaction
def users_ex_beneficiary_automation() -> None:
    """Includes all young users whose credit is expired in "jeunes-ex-benefs" list.
    This command is meant to be called every day."""
    user_automations.users_ex_beneficiary_automation()


@blueprint.cli.command("users_inactive_since_30_days_automation")
@log_cron_with_transaction
def users_inactive_since_30_days_automation() -> None:
    """Updates the list of users who are inactive since 30 days or more ("jeunes-utilisateurs-inactifs" list).
    This command is meant to be called every day."""
    user_automations.users_inactive_since_30_days_automation()


@blueprint.cli.command("users_one_year_with_pass_automation")
@log_cron_with_transaction
def users_one_year_with_pass_automation() -> None:
    """Includes young users who created their PassCulture account in the same month
    (from first to last day) one year earlier in "jeunes-un-an-sur-le-pass" list.
            This command is meant to be called every month."""
    user_automations.users_one_year_with_pass_automation()


@blueprint.cli.command("notify_users_bookings_not_retrieved")
@log_cron_with_transaction
def notify_users_bookings_not_retrieved() -> None:
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


@blueprint.cli.command("delete_suspended_accounts_after_withdrawal_period")
@log_cron_with_transaction
def delete_suspended_accounts_after_withdrawal_period() -> None:
    if not FeatureToggle.ALLOW_ACCOUNT_REACTIVATION:
        return

    users = fraud_api.get_suspended_upon_user_request_accounts_since(settings.DELETE_SUSPENDED_ACCOUNTS_SINCE)
    for user in users:
        users_api.suspend_account(user, users_constants.SuspensionReason.DELETED, None)


@blueprint.cli.command("handle_inactive_dms_applications_cron")
@log_cron_with_transaction
def handle_inactive_dms_applications_cron() -> None:
    procedures = [
        settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_FR,
        settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_ET,
        settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING,
        settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID,
    ]
    if settings.IS_PROD:
        procedures.append(DMS_OLD_PROCEDURE_ID)
    for procedure_id in procedures:
        try:
            handle_inactive_dms_applications(procedure_id)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to handle inactive DMS applications for procedure %s", procedure_id)


@blueprint.cli.command("handle_deleted_dms_applications_cron")
@log_cron_with_transaction
def handle_deleted_dms_applications_cron() -> None:
    procedures = [
        settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_FR,
        settings.DMS_ENROLLMENT_PROCEDURE_ID_v4_ET,
        settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING,
        settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID,
    ]
    if settings.IS_PROD:
        procedures.append(DMS_OLD_PROCEDURE_ID)
    for procedure_id in procedures:
        try:
            handle_deleted_dms_applications(procedure_id)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to handle deleted DMS applications for procedure %s", procedure_id)
