import datetime
import logging
from decimal import Decimal

import click

import pcapi.core.educational.api.adage as adage_api
import pcapi.core.educational.api.institution as institution_api
import pcapi.core.educational.api.playlists as playlists_api
import pcapi.core.educational.models as educational_models
from pcapi.core import search
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api.dms import import_dms_applications_for_all_eac_procedures
from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)


@blueprint.cli.command("reindex_all_collective_offers")
def reindex_all_collective_offers() -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    search.unindex_all_collective_offer_templates()
    search.index_all_collective_offers_and_templates()


@blueprint.cli.command("generate_fake_adage_token")
@click.option("--readonly", is_flag=True, help="Generate a readonly token.")
@click.option("--cannot-prebook", is_flag=True, help="Generate a token that cannot prebook.")
def generate_fake_adage_token(readonly: bool, cannot_prebook: bool) -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    token = create_adage_jwt_fake_valid_token(readonly=readonly, can_prebook=not cannot_prebook)
    print(f"Adage localhost URL: http://localhost:3001/adage-iframe?token={token}")


@blueprint.cli.command("import_deposit_csv")
@click.option(
    "--year",
    type=int,
    help="Year of start of the edcational year (example: 2023 for educational year 2023-2024).",
    required=True,
)
@click.option(
    "--ministry",
    type=click.Choice([m.name for m in educational_models.Ministry], case_sensitive=False),
    help="Ministry for this deposit.",
    required=True,
)
@click.option("--path", type=str, required=True, help="Path to the CSV to import.")
@click.option(
    "--conflict",
    type=click.Choice(("keep", "replace"), case_sensitive=False),
    default="keep",
    help="Overide previous ministry if needed.",
)
@click.option("--final", is_flag=True, help="Flag deposits as final.")
@click.option("--not-dry", is_flag=True, help="Do not commit the changes.")
def import_deposit_csv(
    *, path: str, year: int, ministry: str, conflict: str, final: bool, not_dry: bool = False
) -> None:
    """
    import CSV deposits and update institution according to adage data.

    CSV format change every time we try to work with it.
    """
    institution_api.import_deposit_institution_csv(
        path=path, year=year, ministry=ministry, conflict=conflict, final=final, program_name=None
    )
    if not_dry:
        db.session.commit()


@blueprint.cli.command("synchronize_venues_from_adage_cultural_partners")
@click.option(
    "--debug",
    is_flag=True,
    help="Activate debugging (add logs)",
)
@click.option("--with-timestamp", is_flag=True, help="Add timestamp (couple days ago)")
@log_cron_with_transaction
def synchronize_venues_from_adage_cultural_partners(debug: bool = False, with_timestamp: bool = False) -> None:
    # Change to use datetime arithmetic
    since_date = datetime.datetime.utcnow() - datetime.timedelta(days=2) if with_timestamp else None
    adage_api.synchronize_adage_ids_on_venues(debug=debug, since_date=since_date)
    # This commit is very much needed at this time.
    # log_cron_with_transaction will only commit IF the session is dirty
    # Since synchronize_adage_ids_on_venues changes are wrapped inside an atomic
    # all the changes are pushed to the DB and the session is cleaned which
    # will NOT trigger the commit
    db.session.commit()


@blueprint.cli.command("synchronize_offerers_from_adage_cultural_partners")
@click.option("--with-timestamp", is_flag=True, help="Add timestamp (couple days ago)")
@log_cron_with_transaction
def synchronize_offerers_from_adage_cultural_partners(with_timestamp: bool = False) -> None:
    # Change to use datetime arithmetic
    since_date = datetime.datetime.utcnow() - datetime.timedelta(days=2) if with_timestamp else None
    with transaction():
        adage_cultural_partners = adage_api.get_cultural_partners(since_date=since_date)
        adage_api.synchronize_adage_ids_on_offerers(adage_cultural_partners.partners)


@blueprint.cli.command("eac_notify_pro_one_day_before")
@log_cron_with_transaction
def notify_pro_users_one_day_before() -> None:
    """Notify pro users 1 day before EAC event."""
    educational_api_booking.notify_pro_users_one_day_before()


@blueprint.cli.command("eac_notify_pro_one_day_after")
@log_cron_with_transaction
def notify_pro_users_one_day_after() -> None:
    """Notify pro users 1 day after EAC event."""
    educational_api_booking.notify_pro_users_one_day_after()


@blueprint.cli.command("eac_handle_pending_collective_booking_j3")
@log_cron_with_transaction
def handle_pending_collective_booking_j3() -> None:
    """Triggers email to be sent for events with pending booking and booking limit date in 3 days"""
    educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()


@blueprint.cli.command("import_eac_dms_application")
@click.option(
    "--ignore_previous",
    is_flag=True,
    help="Import all application ignoring previous import date",
)
@log_cron_with_transaction
def import_eac_dms_application(ignore_previous: bool = False) -> None:
    """Import procedures from dms."""
    import_dms_applications_for_all_eac_procedures(ignore_previous=ignore_previous)


@blueprint.cli.command("notify_reimburse_collective_booking")
@click.option(
    "--booking_id",
    type=int,
    help="Id of the collective booking to reimburse",
    required=True,
)
@click.option(
    "--reason",
    type=click.Choice(("MISSING_PEOPLE", "MISSING_DATE", "NO_EVENT"), case_sensitive=False),
    help="Reason of the reimbursement.",
    required=True,
)
@click.option(
    "--value",
    type=Decimal,
    default=None,
    help="Value reimbursed. It must be lower than the booking value. If omitted it is set to the booking value.",
)
@click.option(
    "--details",
    type=str,
    default="",
    help="Free text with details about the reimbursement.",
)
def notify_reimburse_collective_booking(booking_id: int, reason: str, value: Decimal, details: str) -> None:
    collective_booking = educational_repository.find_collective_booking_by_id(booking_id)
    if not collective_booking:
        print(f"Collective booking {booking_id} not found")
        return
    educational_api_booking.notify_reimburse_collective_booking(
        collective_booking=collective_booking, reason=reason.upper(), value=value, details=details
    )


@blueprint.cli.command("synchronise_institutions_geolocation")
@click.option(
    "--adage-year-id",
    type=str,
    default=None,
    help="The adage year id. If not provided, the current year will be used.",
    required=False,
)
@click.option("--not-dry", is_flag=True, help="Do not commit the changes.")
def synchronise_institutions_geolocation(adage_year_id: str | None, not_dry: bool = False) -> None:
    institution_api.synchronise_institutions_geolocation(adage_year_id=adage_year_id)

    if not_dry:
        db.session.commit()


@blueprint.cli.command("synchronise_rurality_level")
@log_cron_with_transaction
def synchronise_rurality_level() -> None:
    institution_api.synchronise_rurality_level()


@blueprint.cli.command("synchronise_collective_classroom_playlist")
@log_cron_with_transaction
def synchronise_collective_playlist() -> None:
    playlists_api.synchronize_collective_playlist(educational_models.PlaylistType.CLASSROOM)


@blueprint.cli.command("synchronise_collective_new_offer_playlist")
@log_cron_with_transaction
def synchronise_collective_new_offer_playlist() -> None:
    playlists_api.synchronize_collective_playlist(educational_models.PlaylistType.NEW_OFFER)


@blueprint.cli.command("synchronise_collective_local_offerers_playlist")
@log_cron_with_transaction
def synchronise_collective_local_offerer_playlist() -> None:
    playlists_api.synchronize_collective_playlist(educational_models.PlaylistType.LOCAL_OFFERER)


@blueprint.cli.command("synchronise_collective_new_offerers_playlist")
@log_cron_with_transaction
def synchronise_collective_new_offerers_playlist() -> None:
    playlists_api.synchronize_collective_playlist(educational_models.PlaylistType.NEW_OFFERER)
