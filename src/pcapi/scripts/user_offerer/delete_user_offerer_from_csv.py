import csv
from typing import Iterable
from typing import List

from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_offerer_queries import find_one_or_none_by_user_id_and_offerer_id
from pcapi.utils.logger import logger


FIRST_TITLE = "Lien structure sur le portail PRO"
OFFERER_ID_COLUMN_HEADER = "ID Structure"
USER_ID_COLUMN_HEADER = "ID Utilisateur"


def run(csv_file_path: str) -> None:
    logger.info("[DELETE USER_OFFERERS FROM FILE] START")
    logger.info("[DELETE USER_OFFERERS FROM FILE] STEP 1 - Lecture du fichier CSV")
    csv_file = open(csv_file_path)
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

        user_offerer = find_one_or_none_by_user_id_and_offerer_id(int(user_id), int(offerer_id))
        if user_offerer is None:
            continue

        user_offerer_id = user_offerer.id

        logger.info(
            f"[DELETE USER_OFFERERS FROM FILE] Suppression du rattachement pour le user d'id {user_id} et l'offerer d'id {offerer_id} est lancée"
        )

        try:
            repository.delete(user_offerer)
            logger.info(
                f"[DELETE USER_OFFERERS FROM FILE] Suppression du rattachement pour le user d'id {user_id} et l'offerer d'id {offerer_id} réussie"
            )
            user_offerers_successful.append(user_offerer_id)
        except ApiErrors as error:
            logger.exception(
                f"[DELETE USER_OFFERERS FROM FILE] {error.errors} pour le rattachement avec le user d'id {user_id} et l'offerer d'id {offerer_id}"
            )
            user_offerers_in_error.append(user_offerer_id)

    logger.info(f"[DELETE USER_OFFERERS FROM FILE] {len(user_offerers_successful)} RATTACHEMENT SUPPRIMES")
    logger.info("[DELETE USER_OFFERERS FROM FILE] LISTE DES RATTACHEMENT SUPPRIMES")
    logger.info(user_offerers_successful)

    if len(user_offerers_in_error) > 0:
        logger.error("[DELETE USER_OFFERERS FROM FILE] LISTE DES RATTACHEMENTS EN ERREUR")
        logger.error(user_offerers_in_error)


def _is_blank_row(row: List[str]) -> bool:
    return not row or not row[0] or row[0] == FIRST_TITLE
