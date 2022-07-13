from decimal import Decimal

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational.exceptions import CollectiveStockAlreadyExists
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalYear
from pcapi.core.educational.repository import get_confirmed_collective_bookings_amount
from pcapi.core.offers import validation as offers_validation
from pcapi.core.offers.models import Stock


def check_institution_fund(
    educational_institution_id: int,
    educational_year_id: str,
    booking_amount: Decimal,
    deposit: EducationalDeposit,
) -> None:
    spent_amount = get_confirmed_collective_bookings_amount(educational_institution_id, educational_year_id)
    total_amount = booking_amount + spent_amount
    deposit.check_has_enough_fund(total_amount)


def check_institution_exists(educational_institution: EducationalInstitution | None) -> None:
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()


def check_educational_year_exists(educational_year: EducationalYear | None) -> None:
    if not educational_year:
        raise exceptions.EducationalYearNotFound()


def check_stock_is_bookable(stock: Stock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)
    if not stock.offer.isEducational:
        raise exceptions.OfferIsNotEducational(stock.offer.id)
    if not stock.offer.isEvent:
        raise exceptions.OfferIsNotEvent(stock.offer.id)


def check_collective_stock_is_bookable(stock: Stock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)


def check_collective_booking_status(collective_booking: CollectiveBooking) -> None:
    if collective_booking.status == CollectiveBookingStatus.CANCELLED:
        raise exceptions.BookingIsCancelled()


def check_confirmation_limit_date_has_not_passed(booking: CollectiveBooking) -> None:
    if booking.has_confirmation_limit_date_passed():
        raise booking_exceptions.ConfirmationLimitDateHasPassed()


def check_collective_stock_is_editable(stock: CollectiveStock) -> None:
    offers_validation.check_validation_status(stock.collectiveOffer)
    offers_validation.check_event_expiration(stock)


def check_collective_booking_status_pending(booking: CollectiveBooking) -> Exception | None:
    if booking.status is not CollectiveBookingStatus.PENDING:
        raise exceptions.CollectiveOfferStockBookedAndBookingNotPending(booking.status, booking.id)


def check_collective_offer_number_of_collective_stocks(  # type: ignore [return]
    collective_offer: CollectiveOffer,
) -> CollectiveStockAlreadyExists | None:
    if collective_offer.collectiveStock:
        raise exceptions.CollectiveStockAlreadyExists()


def check_user_can_prebook_collective_stock(uai: str, stock: CollectiveStock) -> None:
    offer_institution = stock.collectiveOffer.institution
    if offer_institution is not None and offer_institution.institutionId != uai:
        raise exceptions.CollectiveStockNotBookableByUser()
