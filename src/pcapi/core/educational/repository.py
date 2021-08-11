from datetime import datetime
from decimal import Decimal
from operator import and_
from typing import Optional
from typing import Union

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import EducationalDepositNotFound
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.educational.models import EducationalYear
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
        .filter(and_(Booking.isCancelled.is_(False), Booking.status != BookingStatus.PENDING))
        .options(joinedload(educational_models.EducationalBooking.booking).load_only(Booking.amount, Booking.quantity))
        .all()
    )
    return Decimal(sum([educational_booking.booking.total_amount for educational_booking in educational_bookings]))


def find_educational_booking_by_id(educational_booking_id: int) -> Optional[EducationalBooking]:
    return EducationalBooking.query.filter(EducationalBooking.id == educational_booking_id).join(Booking).one_or_none()


def find_educational_year_by_date(date: datetime) -> EducationalYear:
    return EducationalYear.query.filter(
        date >= EducationalYear.beginningDate,
        date <= EducationalYear.expirationDate,
    ).first()


def find_educational_institution_by_uai_code(uai_code: str) -> EducationalInstitution:
    return EducationalInstitution.query.filter_by(institutionId=uai_code).first()


def find_stock_by_id(stock_id: int) -> Stock:
    return Stock.query.filter_by(id=stock_id).first()


def find_educational_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: Optional[str] = None,
    status: Optional[Union[educational_models.EducationalBookingStatus, BookingStatus]] = None,
) -> list[educational_models.EducationalBooking]:
    educational_bookings_base_query = (
        educational_models.EducationalBooking.query.join(Booking)
        .join(educational_models.EducationalInstitution)
        .join(educational_models.EducationalYear)
        .options(
            joinedload(educational_models.EducationalBooking.booking)
            .joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
        )
        .options(joinedload(educational_models.EducationalBooking.educationalInstitution))
        .filter(educational_models.EducationalInstitution.institutionId == uai_code)
        .filter(educational_models.EducationalYear.adageId == year_id)
    )

    if redactor_email is not None:
        educational_bookings_base_query = educational_bookings_base_query.join(EducationalRedactor).filter(
            EducationalRedactor.email == redactor_email
        )

    if status is not None:
        if status in BookingStatus:
            educational_bookings_base_query = educational_bookings_base_query.filter(Booking.status == status)

        if status in educational_models.EducationalBookingStatus:
            educational_bookings_base_query = educational_bookings_base_query.filter(
                educational_models.EducationalBooking.status == status
            )

    return educational_bookings_base_query.all()


def find_redactor_by_email(redactor_email: str) -> Optional[EducationalRedactor]:
    return EducationalRedactor.query.filter(EducationalRedactor.email == redactor_email).one_or_none()
