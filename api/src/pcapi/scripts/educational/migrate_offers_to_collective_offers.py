import logging
import time
from traceback import format_exc
from typing import Optional
from typing import Union

from sqlalchemy.orm import joinedload

from pcapi.core import search
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offers import models
from pcapi.models import db


# from pcapi.scripts.educational.migrate_offers_to_collective_offers import migrate; migrate()

logger = logging.getLogger(__name__)


def migrate() -> None:
    """Main entry point."""
    start = time.time()
    logger.info("Strating educational offers migration", extra={"script": "migrate_offers_to_collective_offers"})
    _repaire_beginningdatetime()
    logger.info("Data migration done", extra={"script": "migrate_offers_to_collective_offers"})
    _migrate_offers()
    logger.info("Educational offers migration done", extra={"script": "migrate_offers_to_collective_offers"})
    print(f"elapsed time: {time.time() - start} seconds")


def _repaire_beginningdatetime() -> None:
    # update educational stocks without beginningDatetime as they should not exists
    # it's only 4 rows we don't care about speed
    stocks = (
        db.session.query(models.Stock)
        .join(models.Offer, models.Stock.offer)
        .filter(models.Offer.isEducational == True, models.Stock.beginningDatetime.is_(None))
        .all()
    )

    for stock in stocks:
        stock.beginningDatetime = stock.bookingLimitDatetime
        db.session.add(stock)
    db.session.commit()


def _migrate_offers() -> None:

    already_existing_offers_tuple = list(db.session.query(CollectiveOffer.offerId).all())
    already_existing_offers_tuple.extend(list(db.session.query(CollectiveOfferTemplate.offerId).all()))
    already_existing_offers = {offer_id for (offer_id,) in already_existing_offers_tuple}
    already_existing_stocks = {stock_id for (stock_id,) in db.session.query(CollectiveStock.stockId).all()}
    already_existing_bookings = {booking_id for (booking_id,) in db.session.query(CollectiveBooking.bookingId).all()}

    offers_query = db.session.query(models.Offer)
    offers_query = offers_query.filter(models.Offer.isEducational == True)
    offers_query = offers_query.options(
        joinedload(models.Offer.stocks),
        joinedload(models.Offer.stocks).joinedload(models.Stock.bookings),
        joinedload(models.Offer.stocks).joinedload(models.Stock.bookings).joinedload(Booking.educationalBooking),
    )
    offers = offers_query.all()

    templates_ids = []
    offers_ids = []

    for offer in offers:
        try:
            print(".", end="")  # simple progress bar
            stock = _select_stock(offer.stocks)
            if not stock:
                msg = f"Could not select a stock for Offer {offer.id}. This case should be managed manually"
                print("\n" + msg)
                logger.warning(msg, extra={"script": "migrate_offers_to_collective_offers"})
                continue

            if offer.id in already_existing_offers:
                collective_offer = _update_collective_offer(offer, stock)
            else:
                collective_offer = _create_collective_offer(offer, stock)

            db.session.commit()
            if isinstance(collective_offer, CollectiveOfferTemplate):
                templates_ids.append(collective_offer.id)
                continue

            if stock.id in already_existing_stocks:
                collective_stock = _update_collective_stock(stock, collective_offer)
            else:
                collective_stock = _create_collective_stock(stock, collective_offer)
            db.session.commit()
            for booking in stock.bookings:
                if booking.id in already_existing_bookings:
                    _update_collective_booking(booking, collective_stock)
                else:
                    _create_collective_booking(booking, collective_stock)

            db.session.commit()
            offers_ids.append(collective_offer.id)
        except KeyboardInterrupt:
            logger.error("interrupetd by user", extra={"script": "migrate_offers_to_collective_offers"})
            break
        except Exception:  # pylint: disable=broad-except
            msg = f"Error while migrating Offer {offer.id} stack_trace: \n {format_exc()}"
            print("\n" + msg)
            logger.error(msg, extra={"script": "migrate_offers_to_collective_offers"})

    print("done")
    print("indexing in search engine")
    search.async_index_collective_offer_template_ids(templates_ids)
    search.async_index_collective_offer_ids(offers_ids)


def _get_phone_number(offer: models.Offer) -> str:
    extra_data = getattr(offer, "extraData", {}) or {}
    phone = extra_data.get("contactPhone", "").strip()
    if not phone and offer.venue.contact:
        phone = (offer.venue.contact.phone_number or "").strip()
    return phone


def _get_email(offer: models.Offer) -> str:
    extra_data = getattr(offer, "extraData", {}) or {}
    email = extra_data.get("contactEmail", "").strip()
    if not email and offer.venue.contact:
        email = (offer.venue.contact.email or "").strip()
    return email


def _update_collective_offer(
    offer: models.Offer, stock: models.Stock
) -> Union[CollectiveOffer, CollectiveOfferTemplate]:
    is_template = offer.extraData and offer.extraData.get("isShowcase", False)  # type: ignore [union-attr]
    base_class = CollectiveOfferTemplate if is_template else CollectiveOffer
    collective_offer = db.session.query(base_class).filter(base_class.offerId == offer.id).one()  # type: ignore [attr-defined]
    list_of_common_attributes = [
        "isActive",
        "venue",
        "name",
        "description",
        "durationMinutes",
        "dateCreated",
        "subcategoryId",
        "dateUpdated",
        "bookingEmail",
        "lastValidationDate",
        "validation",
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
    ]
    extra_data = getattr(offer, "extraData", {}) or {}
    students = [StudentLevels(x).name for x in extra_data.get("students", [])]  # type: ignore [union-attr]
    for attr_name in list_of_common_attributes:
        attr_value = getattr(offer, attr_name)
        setattr(collective_offer, attr_name, attr_value)

    collective_offer.contactEmail = _get_email(offer)
    collective_offer.contactPhone = _get_phone_number(offer)
    collective_offer.offerVenue = extra_data.get("offerVenue")  # type: ignore [union-attr]
    collective_offer.students = students

    if is_template and offer.stocks:
        collective_offer.priceDetail = stock.educationalPriceDetail

    db.session.add(collective_offer)
    return collective_offer


def _create_collective_offer(
    offer: models.Offer, stock: models.Stock
) -> Union[CollectiveOffer, CollectiveOfferTemplate]:
    is_template = offer.extraData and offer.extraData.get("isShowcase", False)  # type: ignore [union-attr]
    base_class = CollectiveOfferTemplate if is_template else CollectiveOffer

    list_of_common_attributes = [
        "isActive",
        "venue",
        "name",
        "description",
        "durationMinutes",
        "dateCreated",
        "subcategoryId",
        "dateUpdated",
        "bookingEmail",
        "lastValidationDate",
        "validation",
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
    ]
    extra_data = getattr(offer, "extraData", {}) or {}
    offer_mapping = {x: getattr(offer, x) for x in list_of_common_attributes}
    students = [StudentLevels(x).name for x in extra_data.get("students", [])]  # type: ignore [union-attr]
    collective_offer = base_class(
        **offer_mapping,
        offerId=offer.id,
        contactEmail=_get_email(offer),
        contactPhone=_get_phone_number(offer),
        offerVenue=extra_data.get("offerVenue"),  # type: ignore [union-attr]
        students=students,
    )
    if is_template:
        collective_offer.priceDetail = stock.educationalPriceDetail  # type: ignore [attr-defined]
    db.session.add(collective_offer)
    return collective_offer  # type: ignore [return-value]


def _select_stock(stocks: list[models.Stock]) -> Optional[models.Stock]:
    # only one stock easy path, return it

    undeleted_stocks = []
    for stock in stocks:
        if not stock.isSoftDeleted:
            undeleted_stocks.append(stock)

    # if only one undeleted stock
    if len(undeleted_stocks) == 1:
        return undeleted_stocks[0]

    unbooked_stocks = []
    booked_stocks = []
    for stock in undeleted_stocks:
        if not stock.bookings:
            unbooked_stocks.append(stock)

        for booking in stock.bookings:
            if booking.status != BookingStatus.CANCELLED:
                booked_stocks.append(stock)
                break
        else:
            unbooked_stocks.append(stock)

    if len(booked_stocks) == 1:
        return booked_stocks[0]

    if not booked_stocks and unbooked_stocks:
        return sorted(unbooked_stocks, reverse=True, key=lambda x: x.dateCreated)[0]

    # multiple booked stocks or no stocks
    return None  # TODO find which one to return


def _update_collective_stock(stock: models.Stock, collective_offer: CollectiveOffer) -> CollectiveStock:
    collective_stock = db.session.query(CollectiveStock).filter(CollectiveStock.stockId == stock.id).one()
    common_attrs = [
        "dateCreated",
        "dateModified",
        "beginningDatetime",
        "price",
        "bookingLimitDatetime",
        "numberOfTickets",
    ]

    for attr_name in common_attrs:
        attr_value = getattr(stock, attr_name)
        setattr(collective_stock, attr_name, attr_value)

    collective_stock.priceDetail = stock.educationalPriceDetail
    collective_stock.collectiveOffer = collective_offer
    db.session.add(collective_stock)
    return collective_stock


def _create_collective_stock(stock: models.Stock, collective_offer: CollectiveOffer) -> CollectiveStock:
    attrs_mapping = {}
    common_attrs = [
        "dateCreated",
        "dateModified",
        "beginningDatetime",
        "price",
        "bookingLimitDatetime",
        "numberOfTickets",
    ]

    for attr_name in common_attrs:
        attr_value = getattr(stock, attr_name)
        attrs_mapping[attr_name] = attr_value

    attrs_mapping["priceDetail"] = stock.educationalPriceDetail
    attrs_mapping["collectiveOffer"] = collective_offer
    attrs_mapping["stockId"] = stock.id
    collective_stock = CollectiveStock(**attrs_mapping)
    db.session.add(collective_stock)
    return collective_stock


def _update_collective_booking(booking: Booking, collective_stock: CollectiveStock) -> None:
    collective_booking = db.session.query(CollectiveBooking).filter(CollectiveBooking.bookingId == booking.id).one()
    common_attrs = [
        "dateCreated",
        "dateUsed",
        "venue",
        "offerer",
        "cancellationDate",
        "cancellationLimitDate",
        "reimbursementDate",
        "educationalInstitution",
        "educationalYear",
        "confirmationDate",
        "confirmationLimitDate",
        "educationalRedactor",
    ]
    for attr_name in common_attrs:
        try:
            attr_value = getattr(booking, attr_name)
        except AttributeError:
            attr_value = getattr(booking.educationalBooking, attr_name)
        setattr(collective_booking, attr_name, attr_value)
    collective_booking.status = getattr(CollectiveBookingStatus, booking.status.name)  # type: ignore [attr-defined]
    if booking.cancellationReason:
        collective_booking.cancellationReason = getattr(
            CollectiveBookingCancellationReasons, booking.cancellationReason.name  # type: ignore [attr-defined]
        )
    collective_booking.collectiveStock = collective_stock
    db.session.add(collective_booking)


def _create_collective_booking(booking: Booking, collective_stock: CollectiveStock) -> None:
    attrs_mapping = {}
    common_attrs = [
        "dateCreated",
        "dateUsed",
        "venue",
        "offerer",
        "cancellationDate",
        "cancellationLimitDate",
        "reimbursementDate",
        "educationalInstitution",
        "educationalYear",
        "confirmationDate",
        "confirmationLimitDate",
        "educationalRedactor",
    ]
    for attr_name in common_attrs:
        try:
            attr_value = getattr(booking, attr_name)
        except AttributeError:
            attr_value = getattr(booking.educationalBooking, attr_name)
        attrs_mapping[attr_name] = attr_value
    attrs_mapping["status"] = getattr(CollectiveBookingStatus, booking.status.name)  # type: ignore [attr-defined]
    if booking.cancellationReason:
        attrs_mapping["cancellationReason"] = getattr(
            CollectiveBookingCancellationReasons, booking.cancellationReason.name  # type: ignore [attr-defined]
        )
    attrs_mapping["collectiveStock"] = collective_stock
    attrs_mapping["bookingId"] = booking.id
    collective_booking = CollectiveBooking(**attrs_mapping)
    db.session.add(collective_booking)
