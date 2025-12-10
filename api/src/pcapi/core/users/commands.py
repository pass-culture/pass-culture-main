import datetime
import logging

import click

import pcapi.connectors.big_query.queries as big_query_queries
import pcapi.core.chronicles.api as chronicles_api
import pcapi.core.users.api as users_api
import pcapi.core.users.constants as users_constants
import pcapi.core.users.repository as users_repository
import pcapi.utils.cron as cron_decorators
from pcapi import settings
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.external.automations import pro_user as pro_user_automations
from pcapi.core.external.automations import user as user_automations
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.mails.transactional.users import online_event_reminder
from pcapi.core.users import ds as users_ds
from pcapi.core.users import gdpr_api
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.notifications import push
from pcapi.notifications.push import transactional_notifications
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.transaction_manager import atomic


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("notify_users_before_deletion_of_suspended_account")
@cron_decorators.log_cron_with_transaction
def notify_users_before_deletion_of_suspended_account() -> None:
    users_api.notify_users_before_deletion_of_suspended_account()


@blueprint.cli.command("notify_users_before_online_event")
@cron_decorators.log_cron_with_transaction
def notify_users_before_online_event() -> None:
    online_event_reminder.send_online_event_event_reminder()


@blueprint.cli.command("notify_newly_eligible_age_18_users")
@cron_decorators.log_cron_with_transaction
def notify_newly_eligible_users() -> None:
    if not settings.NOTIFY_NEWLY_ELIGIBLE_USERS:
        return

    # TODO: (tconte-pass, 2025-02-20) https://passculture.atlassian.net/browse/PC-34732
    # Make `get_users_that_had_birthday_since` return a query
    # and join here necessary tables to compute remaining credit later.
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    for user in users_repository.get_users_that_had_birthday_since(yesterday, age=17):
        transactional_mails.send_birthday_age_17_email_to_newly_eligible_user(user)
    for user in users_repository.get_users_that_had_birthday_since(yesterday, age=18):
        transactional_mails.send_birthday_age_18_email_to_newly_eligible_user_v3(user)


@blueprint.cli.command("users_ex_beneficiary_automation")
@cron_decorators.log_cron_with_transaction
def users_ex_beneficiary_automation() -> None:
    """Includes all young users whose credit is expired in "jeunes-ex-benefs" list.
    This command is meant to be called every day."""
    user_automations.users_ex_beneficiary_automation()


@blueprint.cli.command("users_one_year_with_pass_automation")
@cron_decorators.log_cron_with_transaction
def users_one_year_with_pass_automation() -> None:
    """Includes young users who created their PassCulture account in the same month
    (from first to last day) one year earlier in "jeunes-un-an-sur-le-pass" list.
            This command is meant to be called every month."""
    user_automations.users_one_year_with_pass_automation()


@blueprint.cli.command("users_whose_credit_expired_today_automation")
@cron_decorators.log_cron_with_transaction
def users_whose_credit_expired_today_automation() -> None:
    """Updates external attributes for young users whose credit just expired.
    This command is meant to be called every day."""
    user_automations.users_whose_credit_expired_today_automation()


@blueprint.cli.command("pro_no_active_offers_since_40_days_automation")
@cron_decorators.log_cron_with_transaction
def pro_no_active_offers_since_40_days_automation() -> None:
    """Updates the list of pros whose offers are inactive since exactly 40 days ago ("pros-pas-offre-active-40-j" list).
    This command is meant to be called every day."""
    pro_user_automations.pro_no_active_offers_since_40_days_automation()


@blueprint.cli.command("pro_no_bookings_since_40_days_automation")
@cron_decorators.log_cron_with_transaction
def pro_no_bookings_since_40_days_automation() -> None:
    """Updates the list of pros whose offers haven't been booked since exactly 40 days ago ("pros-pas-de-resa-40-j" list).
    This command is meant to be called every day."""
    pro_user_automations.pro_no_bookings_since_40_days_automation()


@blueprint.cli.command("pro_marketing_live_show_email_churned_40_days_ago")
@cron_decorators.log_cron_with_transaction
def pro_marketing_live_show_email_churned_40_days_ago() -> None:
    pro_user_automations.update_pro_contacts_list_for_live_show_churned_40_days_ago()


@blueprint.cli.command("pro_marketing_live_show_email_last_booking_40_days_ago")
@cron_decorators.log_cron_with_transaction
def pro_marketing_live_show_email_last_booking_40_days_ago() -> None:
    pro_user_automations.update_pro_contacts_list_for_live_show_last_booking_40_days_ago()


@blueprint.cli.command("delete_suspended_accounts_after_withdrawal_period")
@cron_decorators.log_cron_with_transaction
def delete_suspended_accounts_after_withdrawal_period() -> None:
    query = users_api.get_suspended_upon_user_request_accounts_since(settings.DELETE_SUSPENDED_ACCOUNTS_SINCE)
    for user in query:
        with atomic():
            users_api.suspend_account(user, reason=users_constants.SuspensionReason.DELETED, actor=None)


@blueprint.cli.command("anonymize_inactive_users")
@click.option(
    "--category",
    type=click.Choice(("pro", "notify_pro", "beneficiary", "internal", "neither", "all"), case_sensitive=False),
    help="""Choose which users to anonymize:
    pro: anonymize pro users 3 years after their last connexion
    notify_pro: notify pro 30 days before their anonymization
    beneficiary: anonymize beneficiary users 3 years after their last connection, starting from the 5 years after the expiration of their deposits; also anonymize deposits 10 years after their expiration
    internal: anonymize people who use to work for the compagny 1 year after their account has been suspended
    neither: anonymize users that have never been pro or beneficiaries 3 years after their last connection
    all: anonymize all the users respecting their time rules
    """,
    required=True,
)
@cron_decorators.log_cron
def anonymize_inactive_users(category: str) -> None:
    if category in ("beneficiary", "all"):
        print("Anonymize beneficiary users after 5 years")
        gdpr_api.anonymize_beneficiary_users()
        gdpr_api.anonymize_user_deposits()
        chronicles_api.anonymize_unlinked_chronicles()
    if category in ("neither", "all"):
        print("Anonymizing users that are neither beneficiaries nor pro 3 years after their last connection")
        gdpr_api.anonymize_non_pro_non_beneficiary_users()
    if category in ("notify_pro", "all"):
        print("Notify pro users 30 days before anonymization")
        gdpr_api.notify_pro_users_before_anonymization()
    if category in ("pro", "all"):
        print("Anonymizing pro users 3 years after their last connection")
        gdpr_api.anonymize_pro_users()
    if category in ("internal", "all"):
        print("Anonymizing internal users 1 year after their user was suspended")
        gdpr_api.anonymize_internal_users()


@blueprint.cli.command("execute_gdpr_extract")
@cron_decorators.log_cron_with_transaction
def execute_gdpr_extract() -> None:
    gdpr_api.extract_beneficiary_data_command()
    db.session.commit()


@blueprint.cli.command("clean_gdpr_extracts")
@cron_decorators.log_cron_with_transaction
def clean_gdpr_extracts() -> None:
    gdpr_api.clean_gdpr_extracts()
    db.session.commit()


@blueprint.cli.command("delete_old_trusted_devices")
@cron_decorators.log_cron_with_transaction
def delete_old_trusted_devices() -> None:
    users_api.delete_old_trusted_devices()


@blueprint.cli.command("delete_old_login_device_history")
@cron_decorators.log_cron_with_transaction
def delete_old_login_device_history() -> None:
    users_api.delete_old_login_device_history()


@blueprint.cli.command("sync_ds_instructor_ids")
@cron_decorators.log_cron_with_transaction
def sync_ds_instructor_ids() -> None:
    if not FeatureToggle.ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS.is_active():
        return

    procedure_ids = [
        settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID,
    ]
    for procedure_id in procedure_ids:
        users_ds.sync_instructor_ids(int(procedure_id))
        db.session.commit()


@blueprint.cli.command("sync_ds_user_account_update_requests")
@click.option(
    "--ignore_previous",
    is_flag=True,
    help="Import all application ignoring previous import date",
)
@click.option(
    "--set-without-continuation",
    is_flag=True,
    help="Set unanswered for 30 days applications to without continuation",
)
@cron_decorators.log_cron_with_transaction
def sync_ds_user_account_update_requests(ignore_previous: bool = False, set_without_continuation: bool = False) -> None:
    if not FeatureToggle.ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS.is_active():
        return

    procedure_ids = [
        settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID,
    ]
    for procedure_id in procedure_ids:
        import_ds_applications(
            int(procedure_id),
            users_ds.sync_user_account_update_requests,
            ignore_previous=ignore_previous,
            set_without_continuation=set_without_continuation,
        )
        db.session.commit()


@blueprint.cli.command("sync_ds_deleted_user_account_update_requests")
@cron_decorators.log_cron_with_transaction
def sync_ds_deleted_user_account_update_requests() -> None:
    if not FeatureToggle.ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS.is_active():
        return

    procedure_ids = [
        settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID,
    ]
    for procedure_id in procedure_ids:
        users_ds.sync_deleted_user_account_update_requests(int(procedure_id))
        db.session.commit()


@blueprint.cli.command("send_notification_favorites_not_booked")
@cron_decorators.log_cron_with_transaction
def send_notification_favorites_not_booked() -> None:
    _send_notification_favorites_not_booked()  # useful for tests


def _send_notification_favorites_not_booked() -> None:
    """
    Find favorites without a booking and send one notification at most
    per user in order to encourage him to book it.

    To narrow the number of calls to the Batch api, group by offer.
    """
    max_length = settings.BATCH_MAX_USERS_PER_TRANSACTIONAL_NOTIFICATION
    rows = big_query_queries.FavoritesNotBooked().execute(max_length)

    for row in rows:
        try:
            notification_data = transactional_notifications.get_favorites_not_booked_notification_data(
                row.offer_id, row.offer_name, row.user_ids
            )

            if notification_data:
                push.send_transactional_notification(notification_data)
        except Exception:
            log_extra = {"offer": row.offer_id, "users": row.user_ids, "count": len(row.user_ids)}
            logger.error("Favorites not booked: failed to send notification", extra=log_extra)


@blueprint.cli.command("delete_expired_sessions")
@cron_decorators.log_cron
@atomic()
def delete_expired_sessions() -> None:
    # TODO (rpa 10/12/2025):  move this code to users/session.py and clean imports
    import sqlalchemy as sa

    from pcapi.core.users import models as users_models

    db.session.query(users_models.UserSession).filter(
        users_models.UserSession.expirationDatetime < sa.func.now()
    ).delete()
