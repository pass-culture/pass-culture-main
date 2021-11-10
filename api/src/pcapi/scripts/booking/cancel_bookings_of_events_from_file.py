import csv
import logging
from typing import Iterable

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.models import ApiErrors
from pcapi.models import Offer
from pcapi.models import Stock


logger = logging.getLogger(__name__)


FIRST_TITLE = "id offre"
OFFER_ID_COLUMN_INDEX = 0
OFFER_NAME_COLUMN_INDEX = 3
CANCELATION_FLAG_COLUMN_INDEX = 6
NO_FLAG = "Non"
BOOKINGS_TOKEN_NOT_TO_UPDATE = ["2QLYYA", "BMTUME", "LUJ9AM", "DA8YLU", "Q46YHM"]


def run(csv_file_path: str, cancellation_reason: BookingCancellationReasons) -> None:
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] START")
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] STEP 1 - Lecture du fichier CSV")
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] STEP 2 - Annulation des réservations")
        _cancel_bookings_of_offers_from_rows(csv_reader, cancellation_reason)
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] END")


def _cancel_bookings_of_offers_from_rows(csv_rows: Iterable, reason: BookingCancellationReasons) -> None:
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
            "[CANCEL BOOKINGS OF EVENTS FROM FILE] Annulation des réservations de l'offre '%s' d'id %s lancée",
            offer_name,
            offer_id,
        )

        for booking in bookings_to_cancel:
            if booking.isUsed:
                bookings_api.mark_as_unused(booking)
            bookings_api._cancel_booking(booking, reason)

        try:
            logger.info(
                "[CANCEL BOOKINGS OF EVENTS FROM FILE] Annulation des réservations de l'offre '%s' d'id %s réussie",
                offer_name,
                offer_id,
            )
            offers_successful.append(offer_id)
        except ApiErrors as error:
            logger.exception("[CANCEL BOOKINGS OF EVENTS FROM FILE] %s pour l'offre d'id %s", error.errors, offer_id)
            offers_in_error.append(offer_id)

    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] %i OFFRES ANNULÉES", len(offers_successful))
    logger.info("[CANCEL BOOKINGS OF EVENTS FROM FILE] LISTE DES OFFRES MISES À JOUR")
    logger.info(offers_successful)

    if len(offers_in_error) > 0:
        logger.error("[CANCEL BOOKINGS OF EVENTS FROM FILE] LISTE DES OFFRES EN ERREUR")
        logger.error(offers_in_error)


def _is_header_or_blank_row(row: list[str]) -> bool:
    return not row or not row[0] or row[0] == FIRST_TITLE


def _is_not_flagged_for_cancellation(row: list[str]) -> bool:
    return row[CANCELATION_FLAG_COLUMN_INDEX] == NO_FLAG


def _get_bookings_from_offer(offer_id: int) -> list[Booking]:
    return (
        Booking.query.filter(Booking.token.notin_(BOOKINGS_TOKEN_NOT_TO_UPDATE))
        .join(Stock, Stock.id == Booking.stockId)
        .join(Offer, Offer.id == Stock.offerId)
        .filter(Offer.id == offer_id)
        .all()
    )
