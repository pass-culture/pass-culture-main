import datetime
from decimal import Decimal

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational.constants import INTERVENTION_AREA
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation


def check_institution_fund(
    educational_institution_id: int,
    educational_year_id: str,
    booking_amount: Decimal,
    deposit: models.EducationalDeposit,
) -> None:
    spent_amount = repository.get_confirmed_collective_bookings_amount(educational_institution_id, educational_year_id)
    total_amount = booking_amount + spent_amount
    deposit.check_has_enough_fund(total_amount)


def check_ministry_fund(
    educational_year_id: str, booking_amount: Decimal, booking_date: datetime.datetime, ministry: str | None
) -> None:
    if booking_date.month < 9:
        return
    spent_amount = repository.get_confirmed_collective_bookings_amount_for_ministry(
        educational_year_id=educational_year_id, ministry=ministry
    )
    total_spent_amount = spent_amount + booking_amount
    yearly_available_amount = repository.get_ministry_budget_for_year(
        educational_year_id=educational_year_id, ministry=ministry
    )
    # on sptember-december period we only have 4/12 of the budget
    available_amount = yearly_available_amount / 3
    if total_spent_amount > available_amount:
        raise exceptions.InsufficientMinistryFund()


def check_institution_exists(educational_institution: models.EducationalInstitution | None) -> None:
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()


def check_educational_year_exists(educational_year: models.EducationalYear | None) -> None:
    if not educational_year:
        raise exceptions.EducationalYearNotFound()


def check_stock_is_bookable(stock: offers_models.Stock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)
    if not stock.offer.isEducational:
        raise exceptions.OfferIsNotEducational(stock.offer.id)
    if not stock.offer.isEvent:
        raise exceptions.OfferIsNotEvent(stock.offer.id)


def check_collective_stock_is_bookable(stock: offers_models.Stock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)


def check_collective_booking_status(collective_booking: models.CollectiveBooking) -> None:
    if collective_booking.status == models.CollectiveBookingStatus.CANCELLED:
        raise exceptions.BookingIsCancelled()


def check_confirmation_limit_date_has_not_passed(booking: models.CollectiveBooking) -> None:
    if booking.has_confirmation_limit_date_passed():
        raise booking_exceptions.ConfirmationLimitDateHasPassed()


def check_collective_stock_is_editable(stock: models.CollectiveStock) -> None:
    offers_validation.check_validation_status(stock.collectiveOffer)  # type: ignore [arg-type]
    offers_validation.check_event_expiration(stock)


def check_collective_booking_status_pending(booking: models.CollectiveBooking) -> None:
    if booking.status is not models.CollectiveBookingStatus.PENDING:
        raise exceptions.CollectiveOfferStockBookedAndBookingNotPending(booking.status, booking.id)


def check_collective_offer_number_of_collective_stocks(  # type: ignore [return]
    collective_offer: models.CollectiveOffer,
) -> exceptions.CollectiveStockAlreadyExists | None:
    if collective_offer.collectiveStock:
        raise exceptions.CollectiveStockAlreadyExists()


def check_user_can_prebook_collective_stock(uai: str, stock: models.CollectiveStock) -> None:
    offer_institution = stock.collectiveOffer.institution
    if offer_institution is not None and offer_institution.institutionId != uai:
        raise exceptions.CollectiveStockNotBookableByUser()


def check_intervention_area(intervention_area: list[str]) -> None:
    if not INTERVENTION_AREA.issuperset(intervention_area):
        errors = []
        for area in intervention_area:
            if area not in INTERVENTION_AREA:
                errors.append(area)
        raise exceptions.InvalidInterventionArea(errors=errors)
