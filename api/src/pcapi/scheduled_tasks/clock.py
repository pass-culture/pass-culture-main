import datetime
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Blueprint
from sentry_sdk import set_tag

from pcapi import settings
import pcapi.core.bookings.api as bookings_api
import pcapi.core.finance.api as finance_api
from pcapi.core.offerers.repository import get_offerers_by_date_validated
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_offers
from pcapi.core.offers.repository import find_tomorrow_event_stock_ids
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import api as users_api
from pcapi.core.users.repository import get_newly_eligible_users
from pcapi.domain.user_emails import send_newly_eligible_user_email
from pcapi.domain.user_emails import send_withdrawal_terms_to_newly_validated_offerer
from pcapi.local_providers.provider_api import provider_api_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.scripts.beneficiary import archive_dms_applications
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.beneficiary import remote_tag_has_completed
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_individual_bookings
from pcapi.scripts.payment.user_recredit import recredit_underage_users
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
def pc_remote_import_beneficiaries() -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id)
    remote_tag_has_completed.run(import_from_date, procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


# FIXME (xordoquy, 2021-06-16): This clock must be removed once every application from procedure
#  defined in 44623 has been treated
@cron_context
@log_cron_with_transaction
def pc_remote_import_beneficiaries_from_old_dms() -> None:
    if not settings.IS_PROD:
        return
    procedure_id = 44623
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id)
    remote_tag_has_completed.run(import_from_date, procedure_id)
    archive_dms_applications.archive_applications(procedure_id, dry_run=False)


@cron_context
@log_cron_with_transaction
def pc_import_beneficiaries_from_dms_v3() -> None:
    procedure_id = settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id, use_graphql_api=FeatureToggle.ENABLE_DMS_GRAPHQL_API.is_active())
    remote_tag_has_completed.run(import_from_date, procedure_id)
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
        import_from_date = find_most_recent_beneficiary_creation_date_for_source(
            BeneficiaryImportSources.demarches_simplifiees, procedure_id
        )
        remote_import.run(procedure_id, use_graphql_api=FeatureToggle.ENABLE_DMS_GRAPHQL_API.is_active())
        remote_tag_has_completed.run(import_from_date, procedure_id)
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
def pc_notify_newly_eligible_users() -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    for user in get_newly_eligible_users(yesterday):
        send_newly_eligible_user_email(user)


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


@blueprint.cli.command("clock")
def clock() -> None:
    set_tag("pcapi.app_type", "clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", day="*", hour="23")

    scheduler.add_job(synchronize_provider_api, "cron", day="*", hour="1")

    scheduler.add_job(pc_remote_import_beneficiaries, "cron", day="*", hour="21", minute="50")

    scheduler.add_job(pc_remote_import_beneficiaries_from_old_dms, "cron", day="*", hour="20", minute="50")

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

    scheduler.add_job(pc_notify_newly_eligible_users, "cron", day="*", hour="3")

    scheduler.add_job(pc_clean_expired_tokens, "cron", day="*", hour="2")

    scheduler.add_job(pc_check_stock_quantity_consistency, "cron", day="*", hour="1")

    scheduler.add_job(pc_send_tomorrow_events_notifications, "cron", day="*", hour="16")

    scheduler.add_job(pc_clean_past_draft_offers, "cron", day="*", hour="20")

    scheduler.add_job(pc_send_withdrawal_terms_to_offerers_validated_yesterday, "cron", day="*", hour="6")

    scheduler.add_job(pc_recredit_underage_users, "cron", day="*", hour="0")

    scheduler.add_job(price_bookings, "cron", day="*", minute="/10")

    scheduler.start()
