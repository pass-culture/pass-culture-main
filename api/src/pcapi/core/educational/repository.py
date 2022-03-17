from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from typing import Optional
from typing import Union

from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import extract

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import EducationalDepositNotFound
from pcapi.core.educational.exceptions import EducationalYearNotFound
from pcapi.core.educational.exceptions import StockDoesNotExist
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock


def get_and_lock_educational_deposit(
    educational_institution_id: int, educational_year_id: str
) -> educational_models.EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises EducationalDepositNotFound if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    educational_deposit = (
        educational_models.EducationalDeposit.query.filter_by(
            educationalInstitutionId=educational_institution_id,
            educationalYearId=educational_year_id,
        )
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not educational_deposit:
        raise EducationalDepositNotFound()
    return educational_deposit


def get_confirmed_educational_bookings_amount(
    educational_institution_id: int,
    educational_year_id: str,
) -> Decimal:
    educational_bookings = (
        educational_models.EducationalBooking.query.filter_by(
            educationalInstitutionId=educational_institution_id, educationalYearId=educational_year_id
        )
        .join(Booking)
        .filter(~Booking.status.in_([BookingStatus.CANCELLED, BookingStatus.PENDING]))
        .options(joinedload(educational_models.EducationalBooking.booking).load_only(Booking.amount, Booking.quantity))
        .all()
    )
    return Decimal(sum([educational_booking.booking.total_amount for educational_booking in educational_bookings]))


def find_educational_booking_by_id(
    educational_booking_id: int,
) -> Optional[educational_models.EducationalBooking]:
    return (
        educational_models.EducationalBooking.query.filter(
            educational_models.EducationalBooking.id == educational_booking_id
        )
        .join(Booking)
        .options(
            joinedload(educational_models.EducationalBooking.educationalRedactor).load_only(
                educational_models.EducationalRedactor.email
            )
        )
        .one_or_none()
    )


def find_educational_year_by_date(date_searched: datetime) -> Optional[educational_models.EducationalYear]:
    return educational_models.EducationalYear.query.filter(
        date_searched >= educational_models.EducationalYear.beginningDate,
        date_searched <= educational_models.EducationalYear.expirationDate,
    ).one_or_none()


def find_educational_institution_by_uai_code(uai_code: str) -> Optional[educational_models.EducationalInstitution]:
    return educational_models.EducationalInstitution.query.filter_by(institutionId=uai_code).one_or_none()


def find_all_educational_institution() -> list[educational_models.EducationalInstitution]:
    return educational_models.EducationalInstitution.query.all()


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> Optional[educational_models.EducationalDeposit]:
    return educational_models.EducationalDeposit.query.filter(
        educational_models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
        educational_models.EducationalDeposit.educationalYearId == educational_year_id,
    ).one_or_none()


def get_educational_year_beginning_at_given_year(year: int) -> educational_models.EducationalYear:
    educational_year = educational_models.EducationalYear.query.filter(
        extract("year", educational_models.EducationalYear.beginningDate) == year
    ).one_or_none()
    if educational_year is None:
        raise EducationalYearNotFound()
    return educational_year


def find_educational_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: Optional[str] = None,
    status: Optional[Union[educational_models.EducationalBookingStatus, BookingStatus]] = None,
) -> list[educational_models.EducationalBooking]:

    educational_bookings_base_query = (
        educational_models.EducationalBooking.query.join(educational_models.EducationalBooking.booking)
        .options(
            contains_eager(educational_models.EducationalBooking.booking)
            .joinedload(Booking.stock, innerjoin=True)
            .joinedload(Stock.offer, innerjoin=True)
            .options(
                joinedload(Offer.venue, innerjoin=True),
            )
        )
        .join(educational_models.EducationalInstitution)
        .join(educational_models.EducationalRedactor)
        .join(educational_models.EducationalYear)
        .options(contains_eager(educational_models.EducationalBooking.educationalInstitution))
        .options(contains_eager(educational_models.EducationalBooking.educationalRedactor))
        .filter(educational_models.EducationalInstitution.institutionId == uai_code)
        .filter(educational_models.EducationalYear.adageId == year_id)
    )

    if redactor_email is not None:
        educational_bookings_base_query = educational_bookings_base_query.filter(
            educational_models.EducationalRedactor.email == redactor_email
        )

    if status is not None:
        if status in BookingStatus:
            educational_bookings_base_query = educational_bookings_base_query.filter(Booking.status == status)

        if status in educational_models.EducationalBookingStatus:
            educational_bookings_base_query = educational_bookings_base_query.filter(
                educational_models.EducationalBooking.status == status
            )

    return educational_bookings_base_query.all()


def find_redactor_by_email(redactor_email: str) -> Optional[educational_models.EducationalRedactor]:
    return educational_models.EducationalRedactor.query.filter(
        educational_models.EducationalRedactor.email == redactor_email
    ).one_or_none()


def find_active_educational_booking_by_offer_id(
    offer_id: Union[int, str]
) -> Optional[educational_models.EducationalBooking]:
    return (
        educational_models.EducationalBooking.query.join(Booking)
        .filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))
        .join(Stock)
        .filter(Stock.offerId == offer_id, Stock.isSoftDeleted.is_(False))
        .options(
            contains_eager(educational_models.EducationalBooking.booking)
            .contains_eager(Booking.stock)
            .joinedload(Stock.offer, innerjoin=True)
            .joinedload(Offer.venue, innerjoin=True)
        )
        .options(joinedload(educational_models.EducationalBooking.educationalInstitution, innerjoin=True))
        .options(joinedload(educational_models.EducationalBooking.educationalRedactor, innerjoin=True))
        .one_or_none()
    )


def find_active_collective_booking_by_offer_id(
    collective_offer_id: int,
) -> Optional[educational_models.CollectiveBooking]:
    return (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.status.in_(
                [
                    educational_models.CollectiveBookingStatus.CONFIRMED,
                    educational_models.CollectiveBookingStatus.PENDING,
                ]
            )
        )
        .join(educational_models.CollectiveStock)
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer_id,
        )
        .options(
            contains_eager(educational_models.CollectiveBooking.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
        )
        .options(joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True))
        .one_or_none()
    )


def get_bookings_for_educational_year(educational_year_id: str) -> list[educational_models.EducationalBooking]:
    return (
        educational_models.EducationalBooking.query.filter(
            educational_models.EducationalBooking.educationalYearId == educational_year_id
        )
        .options(
            joinedload(educational_models.EducationalBooking.educationalRedactor, innerjoin=True).load_only(
                educational_models.EducationalRedactor.email
            )
        )
        .options(
            joinedload(educational_models.EducationalBooking.booking, innerjoin=True)
            .load_only(Booking.amount, Booking.stockId, Booking.status, Booking.quantity)
            .joinedload(Booking.stock, innerjoin=True)
            .load_only(Stock.beginningDatetime, Stock.offerId)
            .joinedload(Stock.offer, innerjoin=True)
            .load_only(Offer.name)
            .joinedload(Offer.venue, innerjoin=True)
            .load_only(offerers_models.Venue.managingOffererId, offerers_models.Venue.departementCode)
            .joinedload(offerers_models.Venue.managingOfferer, innerjoin=True)
            .load_only(offerers_models.Offerer.postalCode)
        )
        .options(joinedload(educational_models.EducationalBooking.educationalInstitution, innerjoin=True))
        .all()
    )


def get_expired_collective_offers(interval: list[datetime]) -> Query:
    """Return a query of collective offers whose latest booking limit occurs within
    the given interval.

    Inactive or deleted offers are ignored.
    """

    # FIXME (cgaunet, 2022-03-08): This query could be optimized by returning offers
    # that do not have bookings because booking a collective offer will unindex it.
    return (
        educational_models.CollectiveOffer.query.join(educational_models.CollectiveStock)
        .filter(
            educational_models.CollectiveOffer.isActive.is_(True),
        )
        .having(func.max(educational_models.CollectiveStock.bookingLimitDatetime).between(*interval))
        .group_by(educational_models.CollectiveOffer.id)
        .order_by(educational_models.CollectiveOffer.id)
    )


def find_expiring_collective_bookings_query() -> Query:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return CollectiveBooking.query.filter(
        CollectiveBooking.status == CollectiveBookingStatus.PENDING,
        CollectiveBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expiring_collective_booking_ids_from_query(query: Query) -> Query:
    return query.order_by(CollectiveBooking.id).with_entities(CollectiveBooking.id)


def get_and_lock_collective_stock(stock_id: int) -> educational_models.CollectiveStock:
    """Returns `stock_id` stock with a FOR UPDATE lock
    Raises StockDoesNotExist if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    # Use `with_for_update()` to make sure we lock the stock while perfoming
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurent acces
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    stock = (
        educational_models.CollectiveStock.query.filter_by(id=stock_id)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not stock:
        raise StockDoesNotExist()
    return stock


def get_collective_stock_from_stock_id(stock_id: Union[int, str]) -> Optional[educational_models.CollectiveStock]:
    return educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.stockId == stock_id
    ).one_or_none()
