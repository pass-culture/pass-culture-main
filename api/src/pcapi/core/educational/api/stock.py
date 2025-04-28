import datetime
from functools import partial
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
from pcapi.core.educational.api import shared as api_shared
from pcapi.core.educational.api.offer import notify_educational_redactor_on_collective_offer_or_stock_edit
from pcapi.core.offers import validation as offer_validation
from pcapi.models import db
from pcapi.repository.session_management import on_commit
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.serialization import utils as serialization_utils
from pcapi.utils import date


logger = logging.getLogger(__name__)


def create_collective_stock(stock_data: CollectiveStockCreationBodyModel) -> educational_models.CollectiveStock | None:
    offer_id = stock_data.offer_id
    start = stock_data.start_datetime
    end = stock_data.end_datetime
    booking_limit_datetime = stock_data.booking_limit_datetime
    total_price = stock_data.total_price
    number_of_tickets = stock_data.number_of_tickets
    educational_price_detail = stock_data.educational_price_detail

    if end:
        validation.check_start_and_end_dates_in_same_educational_year(start, end)
    else:
        end = start

    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter_by(id=offer_id)
        .options(sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock))
        .one()
    )

    validation.check_collective_offer_number_of_collective_stocks(collective_offer)
    offer_validation.check_validation_status(collective_offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = start

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        startDatetime=start,
        endDatetime=end,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        priceDetail=educational_price_detail,
    )
    db.session.add(collective_stock)
    db.session.flush()

    # we need to refresh the stock to get the correct datetime with a naive datetime
    db.session.refresh(collective_stock)
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

    return collective_stock


def edit_collective_stock(
    stock: educational_models.CollectiveStock, stock_data: dict
) -> educational_models.CollectiveStock:
    date_fields = ("startDatetime", "endDatetime", "bookingLimitDatetime")
    is_editing_dates = any(field in stock_data for field in date_fields)

    if is_editing_dates:
        validation.check_collective_offer_action_is_allowed(
            stock.collectiveOffer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DATES
        )

    start_datetime = stock_data.get("startDatetime")
    start_datetime = serialization_utils.as_utc_without_timezone(start_datetime) if start_datetime else None
    end_datetime = stock_data.get("endDatetime")
    end_datetime = serialization_utils.as_utc_without_timezone(end_datetime) if end_datetime else None

    if start_datetime and not end_datetime:
        end_datetime = start_datetime

    if start_datetime or end_datetime:
        after_update_start_datetime = start_datetime or stock.startDatetime
        after_update_end_datetime = end_datetime or stock.endDatetime

        validation.check_start_and_end_dates_in_same_educational_year(
            after_update_start_datetime, after_update_end_datetime
        )

        validation.check_start_is_before_end(
            start_datetime=after_update_start_datetime, end_datetime=after_update_end_datetime
        )

    booking_limit = stock_data.get("bookingLimitDatetime")
    booking_limit = serialization_utils.as_utc_without_timezone(booking_limit) if booking_limit else None

    updatable_fields = _extract_updatable_fields_from_stock_data(
        stock,
        stock_data,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        booking_limit_datetime=booking_limit,
    )

    check_start = start_datetime or stock.startDatetime
    check_booking_limit_datetime = booking_limit or stock.bookingLimitDatetime

    # bypass check because when start and booking_limit_datetime are on the
    # same day, booking_limit_datetime is set to start
    should_bypass_check_booking_limit_datetime = False

    if stock.collectiveOffer.venue.departementCode is not None:
        check_start_with_tz = date.utc_datetime_to_department_timezone(
            check_start, stock.collectiveOffer.venue.departementCode
        )
        check_booking_limit_datetime_with_tz = date.utc_datetime_to_department_timezone(
            check_booking_limit_datetime, stock.collectiveOffer.venue.departementCode
        )
        should_bypass_check_booking_limit_datetime = (
            check_start_with_tz.date() == check_booking_limit_datetime_with_tz.date()
        )

    current_booking = stock.get_unique_non_cancelled_booking()

    price = updatable_fields["price"]
    if price is not None:
        if price > stock.price:
            validation.check_collective_offer_action_is_allowed(
                stock.collectiveOffer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
            )
        else:
            validation.check_collective_offer_action_is_allowed(
                stock.collectiveOffer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
            )

    if "numberOfTickets" in stock_data or "educationalPriceDetail" in stock_data:
        validation.check_collective_offer_action_is_allowed(
            stock.collectiveOffer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
        )

    if is_editing_dates and not should_bypass_check_booking_limit_datetime:
        offer_validation.check_booking_limit_datetime(stock, check_start, check_booking_limit_datetime)

    # due to check_booking_limit_datetime the only reason start < booking_limit_dt is when they are on the same day
    # in the venue timezone
    if start_datetime is not None and start_datetime < updatable_fields["bookingLimitDatetime"]:
        updatable_fields["bookingLimitDatetime"] = updatable_fields["startDatetime"]

    stock = educational_repository.get_and_lock_collective_stock(stock_id=stock.id)
    for attribute, new_value in updatable_fields.items():
        if new_value is not None and getattr(stock, attribute) != new_value:
            setattr(stock, attribute, new_value)
    db.session.add(stock)

    api_shared.update_collective_stock_booking(
        stock=stock,
        current_booking=current_booking,
        start_datetime_has_changed="startDatetime" in stock_data,
    )

    db.session.flush()
    logger.info("Stock has been updated", extra={"stock": stock.id})

    on_commit(
        partial(
            notify_educational_redactor_on_collective_offer_or_stock_edit,
            stock.collectiveOfferId,
            list(stock_data.keys()),
        )
    )

    return stock


def get_collective_stock(collective_stock_id: int) -> educational_models.CollectiveStock | None:
    return educational_repository.get_collective_stock(collective_stock_id)


def _extract_updatable_fields_from_stock_data(
    stock: educational_models.CollectiveStock,
    stock_data: dict,
    *,
    start_datetime: datetime.datetime | None,
    end_datetime: datetime.datetime | None,
    booking_limit_datetime: datetime.datetime | None,
) -> dict:
    # if booking_limit_datetime is provided but null, set it to default value which is event datetime
    if "bookingLimitDatetime" in stock_data.keys() and booking_limit_datetime is None:
        booking_limit_datetime = start_datetime if start_datetime else stock.startDatetime

    if "bookingLimitDatetime" not in stock_data.keys():
        booking_limit_datetime = stock.bookingLimitDatetime

    updatable_fields = {
        "startDatetime": start_datetime,
        "endDatetime": end_datetime,
        "bookingLimitDatetime": booking_limit_datetime,
        "price": stock_data.get("price"),
        "numberOfTickets": stock_data.get("numberOfTickets"),
        "priceDetail": stock_data.get("educationalPriceDetail"),
    }

    return updatable_fields
