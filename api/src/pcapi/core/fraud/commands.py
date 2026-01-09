import datetime
import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi import settings
from pcapi.core.subscription.dms import api as dms_api
from pcapi.core.subscription.ubble.api import recover_pending_ubble_applications
from pcapi.core.subscription.ubble.archive_past_identification_pictures import archive_past_identification_pictures
from pcapi.utils import date as date_utils
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.transaction_manager import atomic


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("archive_already_processed_dms_applications")
@cron_decorators.log_cron_with_transaction
def archive_already_processed_dms_applications() -> None:
    procedures = [
        ("v4_FR", settings.DMS_ENROLLMENT_PROCEDURE_ID_FR),
        ("v4_ET", settings.DMS_ENROLLMENT_PROCEDURE_ID_ET),
    ]

    for procedure_name, procedure_id in procedures:
        if not procedure_id:
            logger.info("Skipping DMS %s because procedure id is empty", procedure_name)
            continue
        dms_api.archive_applications(procedure_id, dry_run=False)


@blueprint.cli.command("import_all_updated_dms_applications")
@click.option(
    "--since",
    help="Force previous import date to this date. Format: YYYY-MM-DD. Example: 2025-01-01. Default: None.",
    type=str,
)
@cron_decorators.log_cron_with_transaction
def import_all_updated_dms_applications(since: str | None = None) -> None:
    forced_since = datetime.datetime.fromisoformat(since) if since else None
    for procedure_name, procedure_id in (
        ("v4_FR", settings.DMS_ENROLLMENT_PROCEDURE_ID_FR),
        ("v4_ET", settings.DMS_ENROLLMENT_PROCEDURE_ID_ET),
    ):
        if not procedure_id:
            logger.info("Skipping DMS %s because procedure id is empty", procedure_name)
            continue
        with atomic():
            dms_api.import_all_updated_dms_applications(procedure_id, forced_since=forced_since)


@blueprint.cli.command("handle_inactive_dms_applications_cron")
@cron_decorators.log_cron_with_transaction
def handle_inactive_dms_applications_cron() -> None:
    dms_api.handle_inactive_dms_applications(
        settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
        with_never_eligible_applicant_rule=settings.DMS_NEVER_ELIGIBLE_APPLICANT,
    )
    dms_api.handle_inactive_dms_applications(
        settings.DMS_ENROLLMENT_PROCEDURE_ID_ET,
        with_never_eligible_applicant_rule=settings.DMS_NEVER_ELIGIBLE_APPLICANT,
    )


@blueprint.cli.command("handle_deleted_dms_applications_cron")
@cron_decorators.log_cron_with_transaction
def handle_deleted_dms_applications_cron() -> None:
    procedures = [
        settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
        settings.DMS_ENROLLMENT_PROCEDURE_ID_ET,
    ]
    for procedure_id in procedures:
        try:
            dms_api.handle_deleted_dms_applications(procedure_id)
        except Exception:
            logger.exception("Failed to handle deleted DMS applications for procedure %s", procedure_id)


@blueprint.cli.command("update_pending_ubble_applications_cron")
@cron_decorators.log_cron_with_transaction
def update_pending_ubble_applications_cron() -> None:
    recover_pending_ubble_applications(dry_run=False)


@blueprint.cli.command("archive_past_identifications_automation")
def ubble_archive_past_identifications_automation() -> None:
    # call the archive function on the last 6 months for the statuses "None"
    # (the archive process has never been executed)
    # and "False" (the archive process has executed but failed)
    end_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=186)
    archive_past_identification_pictures(start_date, end_date, picture_storage_status=None)
    archive_past_identification_pictures(start_date, end_date, picture_storage_status=False)
