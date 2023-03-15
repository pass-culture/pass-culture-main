import logging

from pcapi import settings
from pcapi.core import search
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api.adage import synchronize_adage_ids_on_venues
from pcapi.core.educational.api.dms import import_dms_applications
from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)


@blueprint.cli.command("reindex_all_collective_offers")
def reindex_all_collective_offers() -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    search.unindex_all_collective_offers()
    search.unindex_all_collective_offer_templates()
    search.index_all_collective_offers_and_templates()


@blueprint.cli.command("generate_fake_adage_token")
def generate_fake_adage_token() -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    token = create_adage_jwt_fake_valid_token()
    print(f"Adage localhost URL: http://localhost:3002/?token={token}")


@blueprint.cli.command("synchronize_venues_from_adage_cultural_partners")
def synchronize_venues_from_adage_cultural_partners() -> None:
    synchronize_adage_ids_on_venues()


@blueprint.cli.command("eac_notify_pro_one_day")
@log_cron_with_transaction
def notify_pro_users_one_day() -> None:
    """Notify pro users 1 day before EAC event."""
    educational_api_booking.notify_pro_users_one_day()


@blueprint.cli.command("eac_handle_pending_collective_booking_j3")
@log_cron_with_transaction
def handle_pending_collective_booking_j3() -> None:
    """Triggers email to be sent for events with pending booking and booking limit date in 3 days"""
    educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()


@blueprint.cli.command("import_eac_dms_application")
@log_cron_with_transaction
def import_eac_dms_application() -> None:
    """Import procedures from dms."""
    procedures = [
        settings.DMS_EAC_PROCEDURE_INDEPENDANTS_CANDIDATE_ID,
        settings.DMS_EAC_PROCEDURE_STRUCTURE_CANDIDATE_ID,
        settings.DMS_EAC_PROCEDURE_MENJS_CANDIDATE_ID,
    ]
    for procedure_number in procedures:
        import_dms_applications(procedure_number=procedure_number)
