from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
import datetime
from decimal import Decimal

from pcapi.models import Booking
from pcapi.models import ThingType


MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)


class ReimbursementRule(ABC):
    def is_active(self, booking: Booking) -> bool:
        valid_from = self.valid_from or MIN_DATETIME
        valid_until = self.valid_until or MAX_DATETIME
        return valid_from < booking.dateCreated <= valid_until

    @abstractmethod
    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        pass

    @property
    @abstractmethod
    def rate(self) -> Decimal:
        pass

    @property
    @abstractmethod
    def valid_from(self) -> None:
        pass

    @property
    @abstractmethod
    def valid_until(self) -> None:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    def apply(self, booking: Booking) -> Decimal:
        return Decimal(booking.total_amount * self.rate)


class DigitalThingsReimbursement(ReimbursementRule):
    rate = Decimal(0)
    description = "Pas de remboursement pour les offres digitales"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        offer = booking.stock.offer
        book_offer = offer.type == str(ThingType.LIVRE_EDITION)
        cinema_card_offer = offer.type == str(ThingType.CINEMA_CARD)
        offer_is_an_exception = book_offer or cinema_card_offer
        return offer.isDigital and not offer_is_an_exception


class PhysicalOffersReimbursement(ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres physiques"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        offer = booking.stock.offer
        book_offer = offer.type == str(ThingType.LIVRE_EDITION)
        cinema_card_offer = offer.type == str(ThingType.CINEMA_CARD)
        offer_is_an_exception = book_offer or cinema_card_offer
        return offer_is_an_exception or not offer.isDigital


class MaxReimbursementByOfferer(ReimbursementRule):
    # This rule is not used anymore.
    rate = Decimal(0)
    description = "Pas de remboursement au dessus du plafond de 20 000 € par acteur culturel"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        if booking.stock.offer.product.isDigital:
            return False
        return kwargs["cumulative_value"] > 20000


class ReimbursementRateByVenueBetween20000And40000(ReimbursementRule):
    rate = Decimal(0.95)
    description = "Remboursement à 95% entre 20 000 € et 40 000 € par lieu"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        if booking.stock.offer.product.isDigital:
            return False
        return 20000 < kwargs["cumulative_value"] <= 40000


class ReimbursementRateByVenueBetween40000And150000(ReimbursementRule):
    rate = Decimal(0.85)
    description = "Remboursement à 85% entre 40 000 € et 150 000 € par lieu"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        if booking.stock.offer.product.isDigital:
            return False
        return 40000 < kwargs["cumulative_value"] <= 150000


class ReimbursementRateByVenueAbove150000(ReimbursementRule):
    rate = Decimal(0.7)
    description = "Remboursement à 70% au dessus de 150 000 € par lieu"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        if booking.stock.offer.product.isDigital:
            return False
        return kwargs["cumulative_value"] > 150000


class ReimbursementRateForBookAbove20000(ReimbursementRule):
    rate = Decimal(0.95)
    description = "Remboursement à 95% au dessus de 20 000 € pour les livres"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        if not booking.stock.offer.type == str(ThingType.LIVRE_EDITION):
            return False
        return kwargs["cumulative_value"] > 20000


REGULAR_RULES = [
    DigitalThingsReimbursement(),
    PhysicalOffersReimbursement(),
    ReimbursementRateByVenueBetween20000And40000(),
    ReimbursementRateByVenueBetween40000And150000(),
    ReimbursementRateByVenueAbove150000(),
    ReimbursementRateForBookAbove20000(),
]


@dataclass
class BookingReimbursement:
    booking: Booking
    rule: ReimbursementRule
    reimbursed_amount: Decimal


def find_all_booking_reimbursements(bookings: list[Booking]) -> list[BookingReimbursement]:
    reimbursements = []
    total_per_year = defaultdict(lambda: Decimal(0))

    for booking in bookings:
        year = booking.dateCreated.year

        if PhysicalOffersReimbursement().is_relevant(booking):
            total_per_year[year] += booking.total_amount

        rule = get_reimbursement_rule(booking, total_per_year[year])
        reimbursements.append(BookingReimbursement(booking, rule, reimbursed_amount=rule.apply(booking)))

    return reimbursements


def get_reimbursement_rule(booking: Booking, total_per_year: Decimal) -> ReimbursementRule:
    candidates = []
    for rule in REGULAR_RULES:
        if not rule.is_active(booking):
            continue
        if not rule.is_relevant(booking, cumulative_value=total_per_year):
            continue
        if isinstance(rule, ReimbursementRateForBookAbove20000):
            return rule
        candidates.append(rule)

    return min(candidates, key=lambda r: r.apply(booking))
