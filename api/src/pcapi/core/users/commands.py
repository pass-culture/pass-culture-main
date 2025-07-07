import logging

import click

import pcapi.core.chronicles.api as chronicles_api
import pcapi.core.users.api as users_api
import pcapi.core.users.constants as users_constants
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi import settings
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.mails.transactional.users import online_event_reminder
from pcapi.core.users import ds as users_ds
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


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


@blueprint.cli.command("delete_suspended_accounts_after_withdrawal_period")
@cron_decorators.log_cron_with_transaction
def delete_suspended_accounts_after_withdrawal_period() -> None:
    query = users_api.get_suspended_upon_user_request_accounts_since(settings.DELETE_SUSPENDED_ACCOUNTS_SINCE)
    for user in query:
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
        users_api.anonymize_beneficiary_users()
        users_api.anonymize_user_deposits()
        chronicles_api.anonymize_unlinked_chronicles()
    if category in ("neither", "all"):
        print("Anonymizing users that are neither beneficiaries nor pro 3 years after their last connection")
        users_api.anonymize_non_pro_non_beneficiary_users()
    if category in ("notify_pro", "all"):
        print("Notify pro users 30 days before anonymization")
        users_api.notify_pro_users_before_anonymization()
    if category in ("pro", "all"):
        print("Anonymizing pro users 3 years after their last connection")
        users_api.anonymize_pro_users()
    if category in ("internal", "all"):
        print("Anonymizing internal users 1 year after their user was suspended")
        users_api.anonymize_internal_users()


@blueprint.cli.command("execute_gdpr_extract")
@cron_decorators.log_cron_with_transaction
def execute_gdpr_extract() -> None:
    users_api.extract_beneficiary_data_command()
    db.session.commit()


@blueprint.cli.command("clean_gdpr_extracts")
@cron_decorators.log_cron_with_transaction
def clean_gdpr_extracts() -> None:
    users_api.clean_gdpr_extracts()
    db.session.commit()


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
