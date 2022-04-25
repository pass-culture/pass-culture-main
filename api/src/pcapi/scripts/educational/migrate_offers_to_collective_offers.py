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
from pcapi.models.offer_mixin import OfferValidationStatus


# from pcapi.scripts.educational.migrate_offers_to_collective_offers import migrate; migrate()

logger = logging.getLogger(__name__)


def migrate(offer_ids_to_migrate: Optional[list[int]] = None) -> None:
    """Main entry point."""
    start = time.time()
    to_migrate = offer_ids_to_migrate or []
    logger.info("Strating educational offers migration", extra={"script": "migrate_offers_to_collective_offers"})
    _repaire_beginningdatetime()
    logger.info("removing old collective objects", extra={"script": "migrate_offers_to_collective_offers"})
    _clean_database(to_migrate=to_migrate)
    logger.info("Data migration done", extra={"script": "migrate_offers_to_collective_offers"})
    _migrate_offers(to_migrate=to_migrate)
    logger.info("Educational offers migration done", extra={"script": "migrate_offers_to_collective_offers"})
    msg = f"elapsed time: {time.time() - start} seconds"
    print(msg)
    logger.info(msg, extra={"script": "migrate_offers_to_collective_offers"})


def _clean_database(to_migrate: list[int]) -> None:
    # delete bookings
    query = CollectiveBooking.query.filter(CollectiveBooking.bookingId != None)
    if to_migrate:
        subquery = db.session.query(Booking.id)
        subquery = subquery.join(models.Stock, Booking.stock)
        subquery = subquery.filter(models.Stock.offerId.in_(to_migrate))
        query = query.filter(CollectiveBooking.bookingId.in_(subquery))
    query.delete()

    # delete stocks
    query = CollectiveStock.query.filter(CollectiveStock.stockId != None)
    if to_migrate:
        subquery = db.session.query(models.Stock.id).filter(models.Stock.offerId.in_(to_migrate))
        query = query.filter(CollectiveStock.stockId.in_(subquery))
    query.delete()

    # delete offers
    query = db.session.query(CollectiveOffer.id).filter(CollectiveOffer.offerId != None)
    if to_migrate:
        query = query.filter(CollectiveOffer.offerId.in_(to_migrate))
    search.unindex_collective_offer_ids(map(lambda id: id[0], query.all()))
    query = CollectiveOffer.query.filter(CollectiveOffer.offerId != None)
    if to_migrate:
        query = query.filter(CollectiveOffer.offerId.in_(to_migrate))
    query.delete()

    # delete offers template
    query = db.session.query(CollectiveOfferTemplate.id).filter(CollectiveOfferTemplate.offerId != None)
    if to_migrate:
        query = query.filter(CollectiveOfferTemplate.offerId.in_(to_migrate))
    search.unindex_collective_offer_template_ids(map(lambda id: id[0], query.all()))
    query = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.offerId != None)
    if to_migrate:
        query = query.filter(CollectiveOfferTemplate.offerId.in_(to_migrate))
    query.delete()
    db.session.commit()


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


def _migrate_offers(to_migrate: list[int]) -> None:
    failed = []
    not_migrated = []
    query = db.session.query(models.Offer)
    query = query.filter(models.Offer.isEducational == True, models.Offer.validation != OfferValidationStatus.DRAFT)
    if to_migrate:
        query = query.filter(models.Offer.id.in_(to_migrate))
    query = query.options(
        joinedload(models.Offer.stocks),
        joinedload(models.Offer.stocks).joinedload(models.Stock.bookings),
        joinedload(models.Offer.stocks).joinedload(models.Stock.bookings).joinedload(Booking.educationalBooking),
    )
    offers = query.all()

    templates_ids = []
    offers_ids = []

    nb_offers = len(offers)
    i = 0
    for offer in offers:
        try:
            # simple progress bar
            i += 1
            if i % 100 == 0:
                print(i, "/", nb_offers)

            stock = _select_stock(offer.stocks)
            if not stock:
                msg = f"Could not select a stock for Offer {offer.id}. This case should be managed manually"
                print(msg)
                logger.warning(msg, extra={"script": "migrate_offers_to_collective_offers"})
                not_migrated.append(offer.id)
                continue

            collective_offer = _create_collective_offer(offer, stock)

            db.session.commit()
            if isinstance(collective_offer, CollectiveOfferTemplate):
                templates_ids.append(collective_offer.id)
                continue

            collective_stock = _create_collective_stock(stock, collective_offer)
            db.session.commit()
            for booking in stock.bookings:
                _create_collective_booking(booking, collective_stock)

            db.session.commit()
            offers_ids.append(collective_offer.id)
        except KeyboardInterrupt:
            logger.error("interrupetd by user", extra={"script": "migrate_offers_to_collective_offers"})
            break
        except Exception:  # pylint: disable=broad-except
            trace = format_exc()
            msg = f"Error while migrating Offer {offer.id} stack_trace: \n {trace}"
            print(msg)
            failed.append((offer.id, trace))

            logger.error(msg, extra={"script": "migrate_offers_to_collective_offers"})

    logger.info("indexing in search engine", extra={"script": "migrate_offers_to_collective_offers"})
    search.async_index_collective_offer_template_ids(templates_ids)
    search.async_index_collective_offer_ids(offers_ids)
    print("not migrated:")
    print(not_migrated)
    for fail in failed:
        print("failed to migrate", fail[0])
        print(fail[1])


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


def _create_collective_offer(
    offer: models.Offer, stock: Optional[models.Stock]
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
    students = [StudentLevels(x).name for x in extra_data.get("students", [])]
    collective_offer = base_class(
        **offer_mapping,
        offerId=offer.id,
        contactEmail=_get_email(offer),
        contactPhone=_get_phone_number(offer),
        offerVenue=extra_data.get("offerVenue"),
        students=students,
    )
    if is_template and stock is not None:
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

    number_of_tickets = stock.numberOfTickets
    attrs_mapping["priceDetail"] = stock.educationalPriceDetail
    attrs_mapping["collectiveOffer"] = collective_offer
    attrs_mapping["stockId"] = stock.id
    collective_stock = CollectiveStock(**attrs_mapping)
    collective_stock.numberOfTickets = number_of_tickets if number_of_tickets is not None else 0
    db.session.add(collective_stock)
    return collective_stock


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
