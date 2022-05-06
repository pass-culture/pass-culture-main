import datetime
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from sentry_sdk import set_tag
import sqlalchemy.orm as sqla_orm

from pcapi import settings
from pcapi.core.bookings import exceptions as bookings_exceptions
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.bookings.repository import find_educational_bookings_done_yesterday
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.utils as finance_utils
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
from pcapi.core.users.external.user_automations import (
    users_beneficiary_credit_expiration_within_next_3_months_automation,
)
from pcapi.core.users.external.user_automations import users_ex_beneficiary_automation
from pcapi.core.users.external.user_automations import users_inactive_since_30_days_automation
from pcapi.core.users.external.user_automations import users_one_year_with_pass_automation
from pcapi.core.users.external.user_automations import users_turned_eighteen_automation
from pcapi.core.users.repository import get_newly_eligible_age_18_users
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
from pcapi.scripts.beneficiary.import_dms_accepted_applications import import_dms_accepted_applications
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_individual_bookings
from pcapi.scripts.payment.user_recredit import recredit_underage_users
from pcapi.tasks import batch_tasks
from pcapi.utils.blueprint import Blueprint
from pcapi.workers.push_notification_job import send_today_stock_notification


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

# FIXME (jsdupuis, 2022-03-15) : every @cron in this module functions are to be deleted
#  when cron will be managed by the infrastructure rather than by the app

DMS_OLD_PROCEDURE_ID = 44623


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
    import_dms_accepted_applications(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


# FIXME (xordoquy, 2021-06-16): This clock must be removed once every application from procedure
#  defined in 44623 has been treated
@cron_context
@log_cron_with_transaction
def pc_import_dms_users_beneficiaries_from_old_dms() -> None:
    if not settings.IS_PROD:
        return
    procedure_id = DMS_OLD_PROCEDURE_ID
    import_dms_accepted_applications(procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@cron_context
@log_cron_with_transaction
def pc_import_beneficiaries_from_dms_v3() -> None:
    procedure_id = settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING
    import_dms_accepted_applications(procedure_id)
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
        import_dms_accepted_applications(procedure_id)
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
    if not settings.IS_PROD and not settings.IS_TESTING and not settings.IS_DEV:
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
def pc_send_yesterday_event_offers_notifications() -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    for educational_booking in find_educational_bookings_done_yesterday():
        send_eac_satisfaction_study_email_to_pro(educational_booking)


@cron_context
@log_cron_with_transaction
def pc_send_today_events_notifications_metropolitan_france() -> None:
    """
    Find bookings (grouped by stocks) that occur today in metropolitan
    France but not the morning (11h UTC -> 12h/13h local time), and
    send notification to all the user to remind them of the event.
    """
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=11))
    stock_ids = find_today_event_stock_ids_metropolitan_france(today_min)

    for stock_id in stock_ids:
        send_today_stock_notification.delay(stock_id)


@cron_context
@log_cron_with_transaction
def pc_send_email_reminder_7days_before_event() -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    stocks = find_event_stocks_happening_in_x_days(7).options(sqla_orm.joinedload(Stock.offer).joinedload(Offer.venue))
    for stock in stocks:
        send_reminder_7_days_before_event_to_pro(stock)


@cron_context
@log_cron_with_transaction
def pc_clean_past_draft_offers() -> None:
    delete_past_draft_offers()
    delete_past_draft_collective_offers()


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
    last_day = datetime.date.today() - datetime.timedelta(days=1)
    cutoff = finance_utils.get_cutoff_as_datetime(last_day)
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


# FIXME (jsdupuis, 2022-03-10) : to be deleted when cron will be managed by the infrastructure rather than by the app
@blueprint.cli.command("clock")
def clock() -> None:
    set_tag("pcapi.app_type", "clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", day="*", hour="23")

    scheduler.add_job(synchronize_provider_api, "cron", day="*", hour="1")

    scheduler.add_job(pc_import_dms_users_beneficiaries, "cron", day="*", hour="21", minute="50")

    scheduler.add_job(pc_import_dms_users_beneficiaries_from_old_dms, "cron", day="*", hour="20", minute="50")

    scheduler.add_job(pc_import_beneficiaries_from_dms_v3, "cron", day="*", hour="6")

    scheduler.add_job(pc_import_beneficiaries_from_dms_v4, "cron", day="*", hour="6", minute="20")

    scheduler.add_job(update_booking_used, "cron", day="*", hour="0")

    scheduler.add_job(pc_send_yesterday_event_offers_notifications, "cron", day="*", hour="4", minute="10")

    scheduler.add_job(pc_send_email_reminder_7days_before_event, "cron", day="*", hour="8")

    scheduler.add_job(pc_handle_expired_bookings, "cron", day="*", hour="5")

    scheduler.add_job(pc_notify_soon_to_be_expired_individual_bookings, "cron", day="*", hour="5", minute="30")

    scheduler.add_job(pc_notify_newly_eligible_age_18_users, "cron", day="*", hour="3")

    scheduler.add_job(pc_clean_expired_tokens, "cron", day="*", hour="2")

    scheduler.add_job(pc_check_stock_quantity_consistency, "cron", day="*", hour="1")

    scheduler.add_job(pc_send_today_events_notifications_metropolitan_france, "cron", day="*", hour="8")

    scheduler.add_job(pc_clean_past_draft_offers, "cron", day="*", hour="20")

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
