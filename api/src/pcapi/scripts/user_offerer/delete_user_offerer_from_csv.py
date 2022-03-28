import csv
import logging
from typing import Iterable

import pcapi.core.offerers.models as offerers_models
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


logger = logging.getLogger(__name__)


FIRST_TITLE = "Lien structure sur le portail PRO"
OFFERER_ID_COLUMN_HEADER = "ID Structure"
USER_ID_COLUMN_HEADER = "ID Utilisateur"


def run(csv_file_path: str) -> None:
    logger.info("[DELETE USER_OFFERERS FROM FILE] START")
    logger.info("[DELETE USER_OFFERERS FROM FILE] STEP 1 - Lecture du fichier CSV")
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        logger.info("[DELETE USER_OFFERERS FROM FILE] STEP 2 - Suppression des user_offerers")
        _delete_user_offerers_from_rows(csv_reader)
    logger.info("[DELETE USER_OFFERERS FROM FILE] END")


def _delete_user_offerers_from_rows(csv_rows: Iterable) -> None:
    user_offerers_successful = []
    user_offerers_in_error = []

    csv_rows_iterable = iter(csv_rows)
    headers = next(csv_rows_iterable)
    for row in csv_rows_iterable:
        if _is_blank_row(row):
            continue

        row = dict(zip(headers, row))
        user_id = row[USER_ID_COLUMN_HEADER]
        offerer_id = row[OFFERER_ID_COLUMN_HEADER]

        user_offerer = offerers_models.UserOfferer.query.filter_by(
            userId=user_id,
            offererId=int(offerer_id),
        ).one_or_none()
        if user_offerer is None:
            continue

        user_offerer_id = user_offerer.id

        logger.info(
            "[DELETE USER_OFFERERS FROM FILE] Suppression du rattachement pour le user d'id %s et l'offerer "
            "d'id %s est lancée",
            user_id,
            offerer_id,
        )

        try:
            repository.delete(user_offerer)
            logger.info(
                "[DELETE USER_OFFERERS FROM FILE] Suppression du rattachement pour le user d'id %s et l'offerer "
                "d'id %s réussie",
                user_id,
                offerer_id,
            )
            user_offerers_successful.append(user_offerer_id)
        except ApiErrors as error:
            logger.exception(
                "[DELETE USER_OFFERERS FROM FILE] %s pour le rattachement avec le user d'id %s et l'offerer d'id %s",
                error.errors,
                user_id,
                offerer_id,
            )
            user_offerers_in_error.append(user_offerer_id)

    logger.info("[DELETE USER_OFFERERS FROM FILE] %i RATTACHEMENT SUPPRIMES", len(user_offerers_successful))
    logger.info("[DELETE USER_OFFERERS FROM FILE] LISTE DES RATTACHEMENT SUPPRIMES")
    logger.info(user_offerers_successful)

    if len(user_offerers_in_error) > 0:
        logger.error("[DELETE USER_OFFERERS FROM FILE] LISTE DES RATTACHEMENTS EN ERREUR")
        logger.error(user_offerers_in_error)


def _is_blank_row(row: list[str]) -> bool:
    return not row or not row[0] or row[0] == FIRST_TITLE
