import datetime

import typing
from flask_sqlalchemy import BaseQuery

from pcapi.models import db, StockSQLEntity
from pcapi.core.bookings.api import compute_confirmation_date
from pcapi.core.bookings.models import Booking
from pcapi.utils.logger import logger


def fill_missing_confirmation_dates_of_event_bookings_without_confirmation_date_not_cancelled_not_used(
        batch_size: int = 100
) -> None:
    """Run this first: This will update about 8k records"""
    target_bookings_query = _select_event_bookings_without_confirmation_date_not_cancelled_not_used()
    try:
        updated_count = _update_target_bookings(target_bookings_query, batch_size)
        print(f"{updated_count} Bookings had their confirmationDate updated successfully!")
    except Exception as exc:
        logger.exception("Encountered unexpected error while updating confirmationDate: %s", exc)


def fill_missing_confirmation_dates_of_all_event_bookings_without_confirmation_date(batch_size: int = 100) -> None:
    """This will update about 60k records"""
    print(f"[{datetime.datetime.utcnow()}] Starting to update all event bookings bookings...")
    target_bookings_query = _select_all_event_bookings_without_confirmation_date()
    try:
        updated_count = _update_target_bookings(target_bookings_query, batch_size)
        print(f"{updated_count} Bookings had their confirmationDate updated successfully!")
    except Exception as exc:
        logger.exception("Encountered unexpected error while updating confirmationDate: %s", exc)


def get_all_event_bookings_without_confirmation_date_count() -> int:
    return _select_all_event_bookings_without_confirmation_date().count()


def get_event_bookings_without_confirmation_date_not_cancelled_not_used_count() -> int:
    return _select_event_bookings_without_confirmation_date_not_cancelled_not_used().count()


def _select_all_event_bookings_without_confirmation_date() -> BaseQuery:
    """
    récupérer les Bookings d'events passés sans date de confirmation aka
    Bookings qui ont une stock.beginningDatetime non null avec confirmationDate null
    """
    return Booking.query.join(StockSQLEntity). \
        with_entities(Booking.id, StockSQLEntity.beginningDatetime, Booking.dateCreated). \
        filter(Booking.confirmationDate.is_(None)). \
        filter(StockSQLEntity.beginningDatetime.isnot(None))


def _select_event_bookings_without_confirmation_date_not_cancelled_not_used() -> BaseQuery:
    return _select_all_event_bookings_without_confirmation_date(). \
        filter(Booking.isCancelled.is_(False)). \
        filter(Booking.isUsed.is_(False))


def _get_batches(target_bookings_query: list, batch_size: int) -> typing.Generator:
    total_length = len(target_bookings_query)
    for i in range(0, total_length, batch_size):
        yield target_bookings_query[i: i + batch_size]


def _update_target_bookings(target_bookings_query: BaseQuery, batch_size: int) -> int:
    print(f"[{datetime.datetime.utcnow()}] Starting to update target bookings...")
    assert isinstance(batch_size, int)
    batch_number = 1
    updated_count = 0
    batches_count = target_bookings_query.count() // batch_size + (target_bookings_query.count() % batch_size > 0)
    for bookings in _get_batches(target_bookings_query.all(), batch_size):
        start_updating_batch = datetime.datetime.now()
        update_mappings = []

        try:
            for booking_id, event_date, creation_date in bookings:
                confirmation_date = compute_confirmation_date(event_date, creation_date)
                update_mappings.append(
                    {"id": booking_id, "confirmationDate": confirmation_date}
                )

            db.session.bulk_update_mappings(Booking, update_mappings)
            db.session.commit()
            end_updating_batch = datetime.datetime.now()
            updated_count += len(update_mappings)
            duration = f"{(end_updating_batch - start_updating_batch).total_seconds():.2f}"
            print(f"[{datetime.datetime.utcnow()}]  Updated batch {batch_number}/{batches_count} in {duration} seconds")

        except Exception as exc:
            raise exc

        batch_number += 1

    return updated_count
