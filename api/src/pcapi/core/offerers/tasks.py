import logging

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class CheckOffererSirenRequest(BaseModel):
    siren: str
    tag_when_inactive: bool


@task(settings.GCP_CHECK_OFFERER_SIREN_QUEUE_NAME, "/offerers/check_offerer_is_active", task_request_timeout=3 * 60)  # type: ignore [arg-type]
def check_offerer_siren_task(payload: CheckOffererSirenRequest) -> None:
    try:
        siren_info = sirene.get_siren(payload.siren, with_address=False, raise_if_non_public=False)
    except sirene.SireneException as exc:
        logger.info("Could not fetch info from Sirene API", extra={"siren": payload.siren, "exc": exc})
        return

    if siren_info.active:
        return

    offerer = offerers_repository.find_offerer_by_siren(payload.siren)
    if not offerer:
        # This should not happen, unless offerer has been deleted between cron task and this task
        return

    logger.info("SIREN is no longer active", extra={"offerer_id": offerer.id, "siren": offerer.siren})

    if payload.tag_when_inactive:
        # .one() raises an exception if the tag does not exist -- this will ensure that a potential issue is tracked
        tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == "siren-caduc").one()

        with transaction():
            db.session.add(offerers_models.OffererTagMapping(offererId=offerer.id, tagId=tag.id))
            if offerer.isWaitingForValidation:
                offerers_api.reject_offerer(
                    offerer=offerer,
                    author_user=None,
                    comment="La structure est détectée comme inactive via l'API Sirene (INSEE)",
                    modified_info={"tags": {"new_info": tag.label}},
                )
            else:
                history_api.add_action(
                    history_models.ActionType.INFO_MODIFIED,
                    None,
                    offerer=offerer,
                    comment="La structure est détectée comme inactive via l'API Sirene (INSEE)",
                    modified_info={"tags": {"new_info": tag.label}},
                )
