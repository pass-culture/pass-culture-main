import datetime
import json
import logging
import time
import typing

import sqlalchemy.orm as sa_orm
from flask import current_app

from pcapi import settings
from pcapi.connectors import googledrive
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.connectors.entreprise import models as entreprise_models
from pcapi.connectors.entreprise import sirene
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils import siren as siren_utils
from pcapi.utils.repository import transaction
from pcapi.utils.urls import build_backoffice_offerer_link


logger = logging.getLogger(__name__)

CLOSED_OFFERER_TAG_NAME = "siren-caduc"


def _get_scheduled_siren_redis_key(at_date: datetime.date) -> str:
    return f"check_closed_offerers:scheduled:{at_date.isoformat()}"


def get_scheduled_siren_to_check(at_date: datetime.date) -> list[str]:
    key = _get_scheduled_siren_redis_key(at_date)
    data = current_app.redis_client.get(key)
    if not data:
        return []
    return json.loads(data)


def add_scheduled_siren_to_check(siren: str, at_date: datetime.date) -> None:
    siren_list = get_scheduled_siren_to_check(at_date)
    if siren not in siren_list:
        siren_list.append(siren)
        key = _get_scheduled_siren_redis_key(at_date)
        ttl = int((at_date - datetime.date.today() + datetime.timedelta(days=30)).total_seconds())
        current_app.redis_client.set(key, json.dumps(siren_list), ex=ttl)


class CheckOffererSirenRequest(BaseModel):
    siren: str
    close_or_tag_when_inactive: bool
    fill_in_codir_report: bool = False


@task(settings.GCP_CHECK_OFFERER_SIREN_QUEUE_NAME, "/offerers/check_offerer", task_request_timeout=3 * 60)  # type: ignore[arg-type]
def check_offerer_siren_task(payload: CheckOffererSirenRequest) -> None:
    if not siren_utils.is_valid_siren(payload.siren):
        logger.error("Invalid SIREN format in the database", extra={"siren": payload.siren})
        return

    try:
        siren_info = sirene.get_siren(payload.siren, with_address=False, raise_if_non_public=False)
    except entreprise_exceptions.SireneException:
        try:
            siren_info = entreprise_api.get_siren(payload.siren, with_address=False, raise_if_non_public=False)
        except entreprise_exceptions.EntrepriseException as exc:
            logger.info("Could not fetch info from Sirene API", extra={"siren": payload.siren, "exc": exc})
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
        # or between the day it was set in redis and today.
        return

    if siren_info.active:
        if siren_info.closure_date:
            # When siren_info.closure_date is set in the future (still active), schedule a new check on closure date
            logger.warning(
                "Sirene API reports an offerer closed in the future",
                extra={"siren": siren_info.siren, "closure_date": siren_info.closure_date},
            )
            add_scheduled_siren_to_check(siren_info.siren, siren_info.closure_date)

        for tag in offerer.tags:
            if tag.name == CLOSED_OFFERER_TAG_NAME:
                db.session.query(offerers_models.OffererTagMapping).filter_by(
                    offererId=offerer.id, tagId=tag.id
                ).delete(synchronize_session=False)
                history_api.add_action(
                    history_models.ActionType.INFO_MODIFIED,
                    author=None,
                    offerer=offerer,
                    comment="L'entité juridique est détectée comme active via l'API Sirene (INSEE)",
                    modified_info={"tags": {"old_info": tag.label}},
                )
                break

        if not payload.fill_in_codir_report:
            # Nothing to do
            return

    if not siren_info.active:
        logger.info("SIREN is no longer active", extra={"offerer_id": offerer.id, "siren": offerer.siren})

        if payload.close_or_tag_when_inactive:
            action_kwargs: dict[str, typing.Any] = {
                "comment": "L'entité juridique est détectée comme fermée "
                + (siren_info.closure_date.strftime("le %d/%m/%Y ") if siren_info.closure_date else "")
                + "via l'API Sirene (INSEE)",
            }

            with transaction():
                # Offerer may have been tagged in the past, but not closed
                if CLOSED_OFFERER_TAG_NAME not in (tag.name for tag in offerer.tags):
                    # .one() raises an exception if the tag does not exist -- ensures that a potential issue is tracked
                    tag = (
                        db.session.query(offerers_models.OffererTag)
                        .filter(offerers_models.OffererTag.name == CLOSED_OFFERER_TAG_NAME)
                        .one()
                    )
                    action_kwargs["modified_info"] = {"tags": {"new_info": tag.label}}
                    db.session.add(offerers_models.OffererTagMapping(offererId=offerer.id, tagId=tag.id))

                if offerer.isWaitingForValidation:
                    offerers_api.reject_offerer(
                        offerer=offerer,
                        author_user=None,
                        rejection_reason=offerers_models.OffererRejectionReason.CLOSED_BUSINESS,
                        **action_kwargs,
                    )
                elif offerer.isValidated and FeatureToggle.ENABLE_AUTO_CLOSE_CLOSED_OFFERERS.is_active():
                    offerers_api.close_offerer(
                        offerer,
                        closure_date=siren_info.closure_date,
                        author_user=None,
                        **action_kwargs,
                    )
                elif "modified_info" in action_kwargs:
                    history_api.add_action(
                        history_models.ActionType.INFO_MODIFIED,
                        author=None,
                        offerer=offerer,
                        **action_kwargs,
                    )

    if offerer.isValidated and payload.fill_in_codir_report:
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
    # check attestations
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
