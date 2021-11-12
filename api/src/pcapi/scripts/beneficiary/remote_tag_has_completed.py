from datetime import datetime
import logging
from typing import Callable

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import get_application_details
from pcapi.core.users.models import User
from pcapi.domain.demarches_simplifiees import get_received_application_ids_for_demarche_simplifiee
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email


logger = logging.getLogger(__name__)


def run(
    process_applications_updated_after: datetime,
    procedure_id: int,
    get_all_applications_ids: Callable[..., list[int]] = get_received_application_ids_for_demarche_simplifiee,
    get_details: Callable[..., dict] = get_application_details,
    already_existing_user: Callable[..., User] = find_user_by_email,
) -> None:
    logger.info(
        "[BATCH][REMOTE TAG HAS COMPLETED] Start tagging from Démarches Simplifiées for " "procedure %s",
        procedure_id,
    )
    received_application_ids = get_all_applications_ids(
        procedure_id, settings.DMS_TOKEN, process_applications_updated_after
    )
    for application_id in received_application_ids:
        details = get_details(application_id, procedure_id, settings.DMS_TOKEN)

        user = already_existing_user(details["dossier"]["email"])

        if user:
            if user.has_beneficiary_role:
                logger.warning(
                    "[BATCH][REMOTE TAG HAS COMPLETED] User is already beneficiary",
                    extra={"user": user.id, "procedure": procedure_id},
                )
            elif user.hasCompletedIdCheck:
                logger.warning(
                    "[BATCH][REMOTE TAG HAS COMPLETED] User has already completed id check",
                    extra={"user": user.id, "procedure": procedure_id},
                )
            else:
                user.hasCompletedIdCheck = True
                repository.save(user)
        else:
            logger.warning("[BATCH][REMOTE TAG HAS COMPLETED] No user found", extra={"procedure": procedure_id})

    logger.info("[BATCH][REMOTE TAG HAS COMPLETED] End tagging from Démarches Simplifiées - Procedure %s", procedure_id)
