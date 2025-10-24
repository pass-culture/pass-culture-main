import datetime
import logging
import time

import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import googledrive
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.connectors.entreprise import models as entreprise_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils import siren as siren_utils
from pcapi.utils.urls import build_backoffice_offerer_link


logger = logging.getLogger(__name__)

CLOSED_OFFERER_TAG_NAME = "siren-caduc"


class CheckOffererSirenRequest(BaseModel):
    siren: str
    close_or_tag_when_inactive: bool
    must_fill_in_codir_report: bool = False


@task(settings.GCP_CHECK_OFFERER_SIREN_QUEUE_NAME, "/offerers/check_offerer", task_request_timeout=3 * 60)
def check_offerer_siren_task(payload: CheckOffererSirenRequest) -> None:
    if not siren_utils.is_valid_siren(payload.siren):
        logger.error("Invalid SIREN format in the database", extra={"siren": payload.siren})
        return

    try:
        siren_info = entreprise_api.get_siren_open_data(payload.siren, with_address=False)
    except entreprise_exceptions.EntrepriseException as exc:
        logger.info("Could not fetch info from Entreprise API", extra={"siren": payload.siren, "exc": exc})
        return

    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(siren=payload.siren)
        .options(
            sa_orm.joinedload(offerers_models.Offerer.tags).load_only(
                offerers_models.OffererTag.id, offerers_models.OffererTag.name
            )
        )
        .one_or_none()
    )
    if not offerer:
        # This should not happen, unless has been deleted or its SIREN updated between cron task and this task,
        return

    if siren_info.active:
        for tag in offerer.tags:
            if tag.name == CLOSED_OFFERER_TAG_NAME:
                db.session.query(offerers_models.OffererTagMapping).filter_by(
                    offererId=offerer.id, tagId=tag.id
                ).delete(synchronize_session=False)
                history_api.add_action(
                    history_models.ActionType.INFO_MODIFIED,
                    author=None,
                    offerer=offerer,
                    comment="L'entité juridique est détectée comme active via l'API Entreprise (données INSEE)",
                    modified_info={"tags": {"old_info": tag.label}},
                )
                break
        if not payload.must_fill_in_codir_report:
            # Nothing to do
            return
    if payload.close_or_tag_when_inactive and not siren_info.active:
        # Since we have check_closed_offerer task this should not happen. However we keep it here in case check_closed_offerer fails.
        # This way we make sure to close inactive offerers, even if it's with a delay.
        logger.info(
            "offerer is inactive and has been closed by check_offerer_siren_task instead of in check_closed_offerer, check check_closed_offerer command",
            extra={"offerer_id": offerer.id, "siren": offerer.siren},
        )
        offerers_api.handle_closed_offerer(offerer, closure_date=siren_info.closure_date)

    if offerer.isValidated and payload.must_fill_in_codir_report:
        fill_in_codir_report(offerer, siren_info)
    else:
        # FIXME (prouzet, 2025-01-24) remove this when cloud tasks are replaced:
        # First tasks in the queue every night cause HTTP error 429 on Sirene API because of rate limit (max 30 per minute).
        # https://sentry.passculture.team/organizations/sentry/issues/1616522/
        # The problem only concern the first tasks, before continuous processing on the rate defined on GCP is reached.
        # It does not happen when Codir report is enabled, which takes time to call several APIs.
        # Since cloud tasks will be replaced by something else in a near future, let's try to sleep 2 seconds
        # to ensure that all requested offerers are checked.
        time.sleep(2)


def fill_in_codir_report(offerer: offerers_models.Offerer, siren_info: entreprise_models.SirenInfo) -> None:
    # Unused for now, and since 09/2024. Is used to get reports on offerer's administrative status (up to date on URSSAF etc...)
    try:
        urssaf_status = "OK" if entreprise_api.get_urssaf(siren_info.siren).attestation_delivered else "REFUS"
    except entreprise_exceptions.EntrepriseException as exc:
        urssaf_status = f"Erreur : {str(exc)}"

    if entreprise_api.siren_is_individual_or_public(siren_info):
        dgfip_status = "N/A : Hors périmètre"
    elif siren_info.creation_date and siren_info.creation_date.year >= datetime.date.today().year:
        dgfip_status = "N/A : Entreprise créée dans l'année en cours"
    else:
        try:
            dgfip_status = "OK" if entreprise_api.get_dgfip(siren_info.siren).attestation_delivered else "REFUS"
        except entreprise_exceptions.EntrepriseException as exc:
            dgfip_status = f"Erreur : {str(exc)}"

    googledrive_backend = googledrive.get_backend()
    today = datetime.date.today()
    new_rows: list[list[str | int | float]] = []

    file_name = f"Vérification des structures actives {today.strftime('%Y-%m')}"
    file_id = googledrive_backend.search_file(settings.CODIR_OFFERERS_REPORT_ROOT_FOLDER_ID, file_name)
    if not file_id:
        file_id = googledrive_backend.create_spreadsheet(settings.CODIR_OFFERERS_REPORT_ROOT_FOLDER_ID, file_name)
        new_rows.append(
            [
                "Date de vérification",
                "SIREN",
                "Nom",
                "En activité",
                "Attestation Urssaf",
                "Attestation IS",
                "Forme juridique",
                "Offres réservables",
                f"CA {today.year}",
                "Lien Backoffice",
            ]
        )

    new_rows.append(
        [
            datetime.date.today().strftime("%d/%m/%Y"),
            siren_info.siren,
            siren_info.name,
            "Oui" if siren_info.active else "Non",
            urssaf_status,
            dgfip_status,
            offerers_constants.CODE_TO_CATEGORY_MAPPING.get(int(siren_info.legal_category_code), "Inconnu"),
            _get_total_offers_count(offerer.id),
            float(offerers_api.get_offerer_total_revenue(offerer.id, only_current_year=True)),
            build_backoffice_offerer_link(offerer.id),
        ]
    )

    added_rows = googledrive_backend.append_to_spreadsheet(file_id, new_rows)
    if added_rows != len(new_rows):
        logger.error(
            "Failed to add rows in CODIR offerers report",
            extra={"expected_rows": len(new_rows), "added_rows": added_rows, "offerer_id": offerer.id},
        )


def _get_total_offers_count(offerer_id: int) -> int | str:
    offers_count = offerers_repository.get_number_of_bookable_offers_for_offerer(offerer_id)
    if offers_count < offerers_repository.MAX_OFFERS_PER_OFFERER_FOR_COUNT:
        offers_count += offerers_repository.get_number_of_bookable_collective_offers_for_offerer(offerer_id)

    if offers_count >= offerers_repository.MAX_OFFERS_PER_OFFERER_FOR_COUNT:
        return f"{offerers_repository.MAX_OFFERS_PER_OFFERER_FOR_COUNT}+"

    return offers_count
