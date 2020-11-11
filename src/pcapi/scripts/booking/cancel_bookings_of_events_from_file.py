import csv
from typing import Iterable
from typing import List

from pcapi.models import ApiErrors
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import StockSQLEntity
from pcapi.repository import repository
from pcapi.utils.logger import logger


FIRST_TITLE = "id offre"
OFFER_ID_COLUMN_INDEX = 0
OFFER_NAME_COLUMN_INDEX = 3
CANCELATION_FLAG_COLUMN_INDEX = 6
NO_FLAG = "Non"
BOOKINGS_TOKEN_NOT_TO_UPDATE = ["2QLYYA", "BMTUME", "LUJ9AM", "DA8YLU", "Q46YHM"]


def run(csv_file_path: str) -> None:
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] START")
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] STEP 1 - Lecture du fichier CSV")
    csv_file = open(csv_file_path)
    csv_reader = csv.reader(csv_file)
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] STEP 2 - Annulation des réservations")
    _cancel_bookings_of_offers_from_rows(csv_reader)
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] END")


def _cancel_bookings_of_offers_from_rows(csv_rows: Iterable) -> None:
    offers_successful = []
    offers_in_error = []

    for row in csv_rows:
        if _is_header_or_blank_row(row):
            continue

        if _is_not_flagged_for_cancellation(row):
            continue

        offer_id = row[OFFER_ID_COLUMN_INDEX]
        offer_name = row[OFFER_NAME_COLUMN_INDEX]
        bookings_to_cancel = _get_bookings_from_offer(int(offer_id))

        logger.info(
            f"[CANCEL BOOKINGS OF EVENTS FROM FILE] Annulation des réservations de l'offre '{offer_name}' d'id {offer_id} lancée"
        )

        for booking in bookings_to_cancel:
            booking.isCancelled = True
            booking.isUsed = False
            booking.dateUsed = None

        try:
            repository.save(*bookings_to_cancel)
            logger.info(
                f"[CANCEL BOOKINGS OF EVENTS FROM FILE] Annulation des réservations de l'offre '{offer_name}' d'id {offer_id} réussie"
            )
            offers_successful.append(offer_id)
        except ApiErrors as error:
            logger.exception(f"[CANCEL BOOKINGS OF EVENTS FROM FILE] {error.errors} pour l'offre d'id {offer_id}")
            offers_in_error.append(offer_id)

    logger.info(f"[CANCEL BOOKINGS OF EVENTS FROM FILE] {len(offers_successful)} OFFRES ANNULÉES")
    logger.info(f"[CANCEL BOOKINGS OF EVENTS FROM FILE] LISTE DES OFFRES MISES À JOUR")
    logger.info(offers_successful)

    if len(offers_in_error) > 0:
        logger.error(f"[CANCEL BOOKINGS OF EVENTS FROM FILE] LISTE DES OFFRES EN ERREUR")
        logger.error(offers_in_error)


def _is_header_or_blank_row(row: List[str]) -> bool:
    return not row or not row[0] or row[0] == FIRST_TITLE


def _is_not_flagged_for_cancellation(row: List[str]) -> bool:
    return row[CANCELATION_FLAG_COLUMN_INDEX] == NO_FLAG


def _get_bookings_from_offer(offer_id: int) -> List[Booking]:
    return (
        Booking.query.filter(Booking.token.notin_(BOOKINGS_TOKEN_NOT_TO_UPDATE))
        .join(StockSQLEntity, StockSQLEntity.id == Booking.stockId)
        .join(Offer, Offer.id == StockSQLEntity.offerId)
        .filter(Offer.id == offer_id)
        .all()
    )
