import logging

import sqlalchemy.orm as sa_orm
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


class CheckOffererSirenRequest(BaseModel):
    siren: str
    close_or_tag_when_inactive: bool


class CheckOffererSirenRequestV2(BaseModelV2):
    siren: str
    close_or_tag_when_inactive: bool


@celery_async_task(
    name="tasks.offerers.default.check_offerer",
    model=CheckOffererSirenRequest,
    max_per_time_window=settings.CHECK_OFFERER_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.CHECK_OFFERER_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def check_offerer_siren_celery_task(payload: CheckOffererSirenRequestV2) -> None:
    check_offerer_siren(payload)


@task(settings.GCP_CHECK_OFFERER_SIREN_QUEUE_NAME, "/offerers/check_offerer", task_request_timeout=3 * 60)
def check_offerer_siren_cloud_task(payload: CheckOffererSirenRequest) -> None:
    check_offerer_siren(payload)


def check_offerer_siren(payload: CheckOffererSirenRequest | CheckOffererSirenRequestV2) -> None:
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
            if tag.name == offerers_constants.CLOSED_OFFERER_TAG_NAME:
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
            return
    if payload.close_or_tag_when_inactive and not siren_info.active:
        # Since we have check_closed_offerer task this should not happen. However we keep it here in case check_closed_offerer fails.
        # This way we make sure to close inactive offerers, even if it's with a delay.
        logger.info(
            "offerer is inactive and has been closed by check_offerer_siren_task instead of in check_closed_offerer, check check_closed_offerer command",
            extra={"offerer_id": offerer.id, "siren": offerer.siren},
        )
        offerers_api.handle_closed_offerer(offerer, closure_date=siren_info.closure_date)


class MatchAcceslibrePayload(BaseModelV2):
    venue_id: int


@celery_async_task(name="tasks.offerers.default.match_acceslibre", model=MatchAcceslibrePayload)
def match_acceslibre_task(payload: MatchAcceslibrePayload) -> None:
    venue = db.session.query(offerers_models.Venue).filter_by(id=payload.venue_id).one_or_none()
    if venue:
        offerers_api.match_acceslibre(venue)
