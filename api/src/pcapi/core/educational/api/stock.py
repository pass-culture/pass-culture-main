import datetime
import logging

import sqlalchemy as sa

from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational import validation
from pcapi.core.educational.api.offer import notify_educational_redactor_on_collective_offer_or_stock_edit
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.serialization import utils as serialization_utils


logger = logging.getLogger(__name__)


def create_collective_stock(
    stock_data: CollectiveStockCreationBodyModel,
    user: User,
    *,
    offer_id: int | None = None,
) -> educational_models.CollectiveStock | None:
    offer_id = offer_id or stock_data.offer_id
    beginning = stock_data.beginning_datetime
    start = stock_data.start_datetime
    end = stock_data.end_datetime
    booking_limit_datetime = stock_data.booking_limit_datetime
    total_price = stock_data.total_price
    number_of_tickets = stock_data.number_of_tickets
    educational_price_detail = stock_data.educational_price_detail

    assert beginning or (start and end)

    if not beginning:
        assert start and end  # helps mypy
        beginning = start

        _check_start_and_end_dates_in_same_educational_year(start, end)

    if not start or not end:
        assert beginning  # helps mypy
        start, end = beginning, beginning

    collective_offer = (
        educational_models.CollectiveOffer.query.filter_by(id=offer_id)
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock))
        .one()
    )

    validation.check_collective_offer_number_of_collective_stocks(collective_offer)
    offer_validation.check_validation_status(collective_offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = beginning

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=beginning,
        startDatetime=start,
        endDatetime=end,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        priceDetail=educational_price_detail,
    )
    db.session.add(collective_stock)
    db.session.commit()
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

    return collective_stock


def edit_collective_stock(
    stock: educational_models.CollectiveStock, stock_data: dict
) -> educational_models.CollectiveStock:
    validation.check_if_offer_is_not_public_api(stock.collectiveOffer)
    beginning = stock_data.get("beginningDatetime")
    beginning = serialization_utils.as_utc_without_timezone(beginning) if beginning else None
    start_datetime = stock_data.get("startDatetime")
    start_datetime = serialization_utils.as_utc_without_timezone(start_datetime) if start_datetime else None
    end_datetime = stock_data.get("endDatetime")
    end_datetime = serialization_utils.as_utc_without_timezone(end_datetime) if end_datetime else None

    assert not (beginning and start_datetime)

    if not beginning and start_datetime:
        beginning = start_datetime

    if not start_datetime and beginning:
        start_datetime = beginning

    if not end_datetime and beginning:
        end_datetime = beginning

    if start_datetime or end_datetime:
        after_update_start_datetime = start_datetime or stock.startDatetime
        after_update_end_datetime = end_datetime or stock.endDatetime

        _check_start_and_end_dates_in_same_educational_year(after_update_end_datetime, after_update_start_datetime)

    booking_limit = stock_data.get("bookingLimitDatetime")
    booking_limit = serialization_utils.as_utc_without_timezone(booking_limit) if booking_limit else None

    updatable_fields = _extract_updatable_fields_from_stock_data(
        stock, stock_data, beginning, start_datetime, end_datetime, booking_limit
    )

    check_beginning = beginning
    check_booking_limit_datetime = booking_limit

    if beginning is None:
        check_beginning = stock.beginningDatetime
    if booking_limit is None:
        check_booking_limit_datetime = stock.bookingLimitDatetime

    current_booking = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.collectiveStockId == stock.id,
        sa.sql.elements.not_(
            educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CANCELLED
        ),
    ).one_or_none()

    if (
        "beginningDatetime" not in stock_data
        and "startDatetime" not in stock_data
        and "bookingLimitDatetime" not in stock_data
    ):
        price = updatable_fields.get("price")
        if current_booking and current_booking.status == CollectiveBookingStatus.CONFIRMED:
            if price is not None:
                validation.check_if_edition_lower_price_possible(stock, price)
        else:
            if current_booking:
                validation.check_collective_booking_status_pending(current_booking)
            validation.check_collective_stock_is_editable(stock)
    else:
        validation.check_collective_stock_is_editable(stock)
        offer_validation.check_booking_limit_datetime(stock, check_beginning, check_booking_limit_datetime)
        if current_booking:
            validation.check_collective_booking_status_pending(current_booking)

    if current_booking:
        current_booking.confirmationLimitDate = updatable_fields["bookingLimitDatetime"]

        if beginning:
            _update_educational_booking_cancellation_limit_date(current_booking, beginning)
            _update_educational_booking_educational_year_id(current_booking, beginning)

        if stock_data.get("price"):
            current_booking.amount = stock_data.get("price")

    # due to check_booking_limit_datetime the only reason beginning < booking_limit_dt is when they are on the same day
    # in the venue timezone
    if beginning is not None and beginning < updatable_fields["bookingLimitDatetime"]:
        updatable_fields["bookingLimitDatetime"] = updatable_fields["beginningDatetime"]

    with transaction():
        stock = educational_repository.get_and_lock_collective_stock(stock_id=stock.id)
        for attribute, new_value in updatable_fields.items():
            if new_value is not None and getattr(stock, attribute) != new_value:
                setattr(stock, attribute, new_value)
        db.session.add(stock)
        db.session.commit()

    logger.info("Stock has been updated", extra={"stock": stock.id})

    notify_educational_redactor_on_collective_offer_or_stock_edit(
        stock.collectiveOffer.id,
        list(stock_data.keys()),
    )

    db.session.refresh(stock)
    return stock


def get_collective_stock(collective_stock_id: int) -> educational_models.CollectiveStock | None:
    return educational_repository.get_collective_stock(collective_stock_id)


def _check_start_and_end_dates_in_same_educational_year(
    end_datetime: datetime.datetime, start_datetime: datetime.datetime
) -> None:
    start_year = educational_repository.find_educational_year_by_date(start_datetime)
    if not start_year:
        raise exceptions.StartEducationalYearMissing()

    end_year = educational_repository.find_educational_year_by_date(end_datetime)
    if not end_year:
        raise exceptions.EndEducationalYearMissing()

    if start_year.id != end_year.id:
        raise exceptions.StartAndEndEducationalYearDifferent()


def _extract_updatable_fields_from_stock_data(
    stock: educational_models.CollectiveStock,
    stock_data: dict,
    beginning: datetime.datetime | None,
    start_datetime: datetime.datetime | None,
    end_datetime: datetime.datetime | None,
    booking_limit_datetime: datetime.datetime | None,
) -> dict:
    # if booking_limit_datetime is provided but null, set it to default value which is event datetime
    if "bookingLimitDatetime" in stock_data.keys() and booking_limit_datetime is None:
        booking_limit_datetime = beginning if beginning else stock.beginningDatetime

    if "bookingLimitDatetime" not in stock_data.keys():
        booking_limit_datetime = stock.bookingLimitDatetime

    updatable_fields = {
        "beginningDatetime": beginning,
        "startDatetime": start_datetime,
        "endDatetime": end_datetime,
        "bookingLimitDatetime": booking_limit_datetime,
        "price": stock_data.get("price"),
        "numberOfTickets": stock_data.get("numberOfTickets"),
        "priceDetail": stock_data.get("educationalPriceDetail"),
    }

    return updatable_fields


def _update_educational_booking_educational_year_id(
    booking: educational_models.CollectiveBooking,
    new_beginning_datetime: datetime.datetime,
) -> None:
    educational_year = educational_repository.find_educational_year_by_date(new_beginning_datetime)
    if educational_year is None:
        raise exceptions.EducationalYearNotFound()

    booking.educationalYear = educational_year


def _update_educational_booking_cancellation_limit_date(
    booking: educational_models.CollectiveBooking, new_beginning_datetime: datetime.datetime
) -> None:
    booking.cancellationLimitDate = educational_utils.compute_educational_booking_cancellation_limit_date(
        new_beginning_datetime, datetime.datetime.utcnow()
    )
