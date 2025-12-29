import dataclasses
import datetime
import logging
import os
from decimal import Decimal
from pathlib import Path

import click

from pcapi.core import search
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational.api import adage as adage_api
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api import institution as institution_api
from pcapi.core.educational.api import playlists as playlists_api
from pcapi.core.educational.api.dms import import_dms_applications_for_all_eac_procedures
from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.models import db
from pcapi.utils import cron as cron_decorators
from pcapi.utils import date as date_utils
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.transaction_manager import atomic


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
@click.option("--uai", type=str, help="UAI of the institution. Will take the default value if not given.")
def generate_fake_adage_token(readonly: bool, cannot_prebook: bool, uai: str | None) -> None:
    """
    TO BE USED IN LOCAL ENV
    """
    token = create_adage_jwt_fake_valid_token(readonly=readonly, can_prebook=not cannot_prebook, uai=uai)
    print(f"Adage localhost URL: http://localhost:3001/adage-iframe?token={token}")


@blueprint.cli.command("import_deposit_csv")
@click.option(
    "--year",
    type=int,
    required=True,
    help="Year of start of the edcational year (example: 2023 for educational year 2023-2024).",
)
@click.option(
    "--ministry",
    type=click.Choice([m.name for m in models.Ministry]),
    required=True,
    help="Ministry for this deposit.",
)
@click.option(
    "--period-option",
    type=click.Choice([p.name for p in institution_api.ImportDepositPeriodOption]),
    required=True,
    help="""
        Deposit period option
        - EDUCATIONAL_YEAR_FULL: period = full educational year
        - EDUCATIONAL_YEAR_FIRST_PERIOD: period = educational year first period (september start -> december end)
        - EDUCATIONAL_YEAR_SECOND_PERIOD: period = educational year second period (january start -> august end)
    """,
)
@click.option(
    "--credit-update",
    type=click.Choice(("add", "replace")),
    default="replace",
    help="If an existing deposit is found, 'replace' will overwrite the previous credit and 'add' will add the imported amount.",
)
@click.option("--filename", type=str, required=True, help="Name of the CSV to import.")
@click.option(
    "--ministry-conflict",
    type=click.Choice(("keep", "replace")),
    default="keep",
    help="If an existing deposit is found with a different ministry, 'replace' will overwrite the previous ministry and 'keep' will keep the previous one.",
)
@click.option(
    "--educational-program-name",
    type=click.Choice([models.PROGRAM_MARSEILLE_EN_GRAND]),
    help="Link the institutions to a program, if given.",
)
@click.option("--final", is_flag=True, help="Flag deposits as final.")
@click.option("--not-dry", is_flag=True, help="Do not commit the changes.")
def import_deposit_csv(
    *,
    year: int,
    ministry: str,
    period_option: str,
    credit_update: institution_api.CreditUpdateOption,
    filename: str,
    ministry_conflict: institution_api.MinistryConflictOption,
    educational_program_name: str,
    final: bool,
    not_dry: bool = False,
) -> None:
    """
    Import CSV deposits and update institution according to adage data
    """
    args = f"{year=}, {ministry=}, {period_option=}, {credit_update=}, {filename=}, {ministry_conflict=}, {educational_program_name=}, {final=}, {not_dry=}"
    logger.info("Starting import deposit csv with args %s", args)

    # A flask command that we run via a github action copy the input file to pcapi/scripts/flask
    import pcapi

    path = Path(pcapi.__file__).parent / "scripts" / "flask"
    file_path = f"{path}/{filename}"

    output = institution_api.import_deposit_institution_csv(
        path=file_path,
        year=year,
        ministry=models.Ministry[ministry],
        period_option=institution_api.ImportDepositPeriodOption[period_option],
        credit_update=credit_update,
        ministry_conflict=ministry_conflict,
        program_name=educational_program_name,
        final=final,
    )

    output_dir = os.environ.get("OUTPUT_DIRECTORY")
    if output_dir:
        with open(f"{output_dir}/total_amount.txt", "w", encoding="utf8") as f:
            lines = (f"{field} = {value}\n" for field, value in dataclasses.asdict(output).items())
            f.writelines(lines)

    if not_dry:
        logger.info("Finished import deposit csv, committing")
        db.session.commit()
    else:
        logger.info("Finished dry run for import budget, rollback")
        db.session.rollback()


@blueprint.cli.command("check_deposit_csv")
@click.option("--path", type=str, required=True, help="Path to the CSV to check.")
def check_deposit_csv(path: str) -> None:
    data = institution_api.get_import_deposit_data(path)
    logger.info("CSV is valid, found %s UAIs for a total amount of %s", len(data.keys()), sum(data.values()))


@blueprint.cli.command("synchronize_venues_from_adage_cultural_partners")
@click.option(
    "--debug",
    is_flag=True,
    help="Activate debugging (add logs)",
)
@click.option("--with-timestamp", is_flag=True, help="Add timestamp (couple days ago)")
@cron_decorators.log_cron
def synchronize_venues_from_adage_cultural_partners(debug: bool = False, with_timestamp: bool = False) -> None:
    since_date = date_utils.get_naive_utc_now() - datetime.timedelta(days=2)
    adage_cultural_partners = adage_api.get_cultural_partners(since_date=since_date)

    adage_api.synchronize_adage_ids_on_venues(adage_cultural_partners)


@blueprint.cli.command("synchronize_offerers_from_adage_cultural_partners")
@click.option("--with-timestamp", is_flag=True, help="Add timestamp (couple days ago)")
@cron_decorators.log_cron
def synchronize_offerers_from_adage_cultural_partners(with_timestamp: bool = False) -> None:
    # TODO (jcicurel): the Adage cultural partner endpoint has its dateModificationMin parameter required
    # set a distant past date until the synchronize logic is updated
    since_date = datetime.datetime(year=1970, month=1, day=1)
    adage_cultural_partners = adage_api.get_cultural_partners(since_date=since_date)

    with atomic():
        adage_api.synchronize_adage_ids_on_offerers(adage_cultural_partners.partners)


@blueprint.cli.command("eac_notify_pro_one_day_before")
@cron_decorators.log_cron_with_transaction
def notify_pro_users_one_day_before() -> None:
    """Notify pro users 1 day before EAC event."""
    educational_api_booking.notify_pro_users_one_day_before()


@blueprint.cli.command("eac_notify_pro_one_day_after")
@cron_decorators.log_cron_with_transaction
def notify_pro_users_one_day_after() -> None:
    """Notify pro users 1 day after EAC event."""
    educational_api_booking.notify_pro_users_one_day_after()


@blueprint.cli.command("eac_handle_pending_collective_booking_j3")
@cron_decorators.log_cron_with_transaction
def handle_pending_collective_booking_j3() -> None:
    """Triggers email to be sent for events with pending booking and booking limit date in 3 days"""
    educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()


@blueprint.cli.command("import_eac_dms_application")
@click.option(
    "--ignore_previous",
    is_flag=True,
    help="Import all application ignoring previous import date",
)
@cron_decorators.log_cron_with_transaction
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
    collective_booking = repository.find_collective_booking_by_id(booking_id)
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
@cron_decorators.log_cron
def synchronise_rurality_level() -> None:
    institution_api.synchronise_rurality_level()


@blueprint.cli.command("synchronise_collective_classroom_playlist")
@cron_decorators.log_cron
def synchronise_collective_playlist() -> None:
    playlists_api.synchronize_collective_playlist(models.PlaylistType.CLASSROOM)


@blueprint.cli.command("synchronise_collective_new_offer_playlist")
@cron_decorators.log_cron
def synchronise_collective_new_offer_playlist() -> None:
    playlists_api.synchronize_collective_playlist(models.PlaylistType.NEW_OFFER)


@blueprint.cli.command("synchronise_collective_local_offerers_playlist")
@cron_decorators.log_cron
def synchronise_collective_local_offerer_playlist() -> None:
    playlists_api.synchronize_collective_playlist(models.PlaylistType.LOCAL_OFFERER)


@blueprint.cli.command("synchronise_collective_new_offerers_playlist")
@cron_decorators.log_cron
def synchronise_collective_new_offerers_playlist() -> None:
    playlists_api.synchronize_collective_playlist(models.PlaylistType.NEW_OFFERER)
