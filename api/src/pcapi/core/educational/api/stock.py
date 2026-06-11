import datetime
import decimal
import logging
from functools import partial

import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational import validation
from pcapi.core.educational.api import shared as api_shared
from pcapi.core.educational.api.offer import notify_educational_redactor_on_collective_offer_or_stock_edit
from pcapi.core.offers import validation as offer_validation
from pcapi.models import db
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.serialization import utils as serialization_utils
from pcapi.utils import date
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


def create_collective_stock(stock_data: CollectiveStockCreationBodyModel) -> models.CollectiveStock:
    offer_id = stock_data.offerId
    start = stock_data.startDatetime
    end = stock_data.endDatetime
    booking_limit_datetime = stock_data.bookingLimitDatetime
    price = decimal.Decimal(stock_data.price)
    service_price = decimal.Decimal(stock_data.servicePrice) if stock_data.servicePrice is not None else None
    number_of_tickets = stock_data.numberOfTickets
    number_of_teachers = stock_data.numberOfTeachers
    price_detail = stock_data.priceDetail

    validation.check_start_and_end_dates_in_same_educational_year(start, end)

    collective_offer = (
        db.session.query(models.CollectiveOffer)
        .filter_by(id=offer_id)
        .options(sa_orm.joinedload(models.CollectiveOffer.collectiveStock))
        .one()
    )

    validation.check_collective_offer_number_of_collective_stocks(collective_offer)
    validation.check_validation_status(collective_offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = start

    collective_stock = models.CollectiveStock(
        collectiveOffer=collective_offer,
        startDatetime=start,
        endDatetime=end,
        bookingLimitDatetime=booking_limit_datetime,
        price=price,
        servicePrice=service_price if service_price is not None else price,
        numberOfTickets=number_of_tickets,
        numberOfTeachers=number_of_teachers if number_of_teachers is not None else 0,
        priceDetail=price_detail,
    )

    if stock_data.additionalFees:
        collective_stock.collectiveAdditionalFees = [
            models.CollectiveAdditionalFee(type=fee.type, label=fee.label, amount=decimal.Decimal(fee.amount))
            for fee in stock_data.additionalFees
        ]

    db.session.add(collective_stock)

    # when we receive priceDetail, also write to offer additionalDetails
    # long term, the priceDetail field will be removed
    if not collective_offer.additionalDetails and price_detail:
        collective_offer.additionalDetails = price_detail

    db.session.flush()

    # we need to refresh the stock to get the correct datetime with a naive datetime
    db.session.refresh(collective_stock)
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

    return collective_stock


def edit_collective_stock(stock: models.CollectiveStock, stock_data: dict) -> None:
    date_fields = ("startDatetime", "endDatetime", "bookingLimitDatetime")
    is_editing_dates = any(field in stock_data for field in date_fields)

    if is_editing_dates:
        validation.check_collective_offer_action_is_allowed(
            stock.collectiveOffer, models.CollectiveOfferAllowedAction.CAN_EDIT_DATES
        )

    start_datetime = stock_data.get("startDatetime")
    start_datetime = serialization_utils.as_utc_without_timezone(start_datetime) if start_datetime else None
    end_datetime = stock_data.get("endDatetime")
    end_datetime = serialization_utils.as_utc_without_timezone(end_datetime) if end_datetime else None

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

    department_code = stock.collectiveOffer.venue.offererAddress.address.departmentCode
    check_start_with_tz = date.utc_datetime_to_department_timezone(check_start, department_code)
    check_booking_limit_datetime_with_tz = date.utc_datetime_to_department_timezone(
        check_booking_limit_datetime, department_code
    )
    should_bypass_check_booking_limit_datetime = (
        check_start_with_tz.date() == check_booking_limit_datetime_with_tz.date()
    )

    current_booking = stock.get_unique_non_cancelled_booking()

    price = updatable_fields["price"]
    if price is not None:
        # for now we set servicePrice=price, until we receive servicePrice
        updatable_fields["servicePrice"] = price

        if price > stock.price:
            validation.check_collective_offer_action_is_allowed(
                stock.collectiveOffer, models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
            )
        else:
            validation.check_collective_offer_action_is_allowed(
                stock.collectiveOffer, models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
            )

    if "numberOfTickets" in stock_data or "priceDetail" in stock_data or "numberOfTeachers" in stock_data:
        validation.check_collective_offer_action_is_allowed(
            stock.collectiveOffer, models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
        )

    if is_editing_dates and not should_bypass_check_booking_limit_datetime:
        offer_validation.check_booking_limit_datetime(stock, check_start, check_booking_limit_datetime)

    # due to check_booking_limit_datetime the only reason start < booking_limit_dt is when they are on the same day
    # in the venue timezone
    if start_datetime is not None and start_datetime < updatable_fields["bookingLimitDatetime"]:
        updatable_fields["bookingLimitDatetime"] = updatable_fields["startDatetime"]

    stock = repository.get_and_lock_collective_stock(stock_id=stock.id)
    for attribute, new_value in updatable_fields.items():
        if new_value is not None and getattr(stock, attribute) != new_value:
            setattr(stock, attribute, new_value)

            # when we receive priceDetail, also write to offer additionalDetails
            # long term, the priceDetail field will be removed
            if attribute == "priceDetail":
                stock.collectiveOffer.additionalDetails = new_value

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


def _extract_updatable_fields_from_stock_data(
    stock: models.CollectiveStock,
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

    price = stock_data.get("price")
    updatable_fields = {
        "startDatetime": start_datetime,
        "endDatetime": end_datetime,
        "bookingLimitDatetime": booking_limit_datetime,
        "price": decimal.Decimal(price) if price is not None else None,
        "numberOfTickets": stock_data.get("numberOfTickets"),
        "numberOfTeachers": stock_data.get("numberOfTeachers"),
        "priceDetail": stock_data.get("priceDetail"),
    }

    return updatable_fields
