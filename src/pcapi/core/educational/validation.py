from decimal import Decimal

from pcapi.core.educational import exceptions
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalYear
from pcapi.core.educational.repository import get_confirmed_educational_bookings_amount
from pcapi.core.offers.models import Stock


def check_institution_fund(
    educational_institution_id: int,
    educational_year_id: str,
    booking_amount: Decimal,
    deposit: EducationalDeposit,
) -> None:
    spent_amount = get_confirmed_educational_bookings_amount(educational_institution_id, educational_year_id)
    total_amount = booking_amount + spent_amount

    deposit.check_has_enough_fund(total_amount)


def check_institution_exists(educational_institution: EducationalInstitution) -> None:
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()


def check_educational_year_exists(educational_year: EducationalYear) -> None:
    if not educational_year:
        raise exceptions.EducationalYearNotFound()


def check_stock_is_bookable(stock: Stock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)
    if not stock.offer.isEducational:
        raise exceptions.OfferIsNotEducational(stock.offer.id)
    if not stock.offer.isEvent:
        raise exceptions.OfferIsNotEvent(stock.offer.id)
