from collections import defaultdict
from dataclasses import dataclass
import datetime
from decimal import Decimal

from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.models import Booking
from pcapi.models import ThingType


MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)


class ReimbursementRule:
    def is_active(self, booking: Booking) -> bool:
        valid_from = self.valid_from or MIN_DATETIME
        valid_until = self.valid_until or MAX_DATETIME
        return valid_from < booking.dateUsed <= valid_until

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        raise NotImplementedError()

    @property
    def rate(self) -> Decimal:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def apply(self, booking: Booking) -> Decimal:
        return Decimal(booking.total_amount * self.rate)


class DigitalThingsReimbursement(ReimbursementRule):
    rate = Decimal(0)
    description = "Pas de remboursement pour les offres digitales"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        offer = booking.stock.offer
        return offer.isDigital and not _is_offer_an_exception_to_reimbursement_rules(offer)


class PhysicalOffersReimbursement(ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres physiques"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs: Decimal) -> bool:
        offer = booking.stock.offer
        return _is_offer_an_exception_to_reimbursement_rules(offer) or not offer.isDigital


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


def find_all_booking_reimbursements(
    bookings: list[Booking], custom_rules: list[ReimbursementRule]
) -> list[BookingReimbursement]:
    reimbursements = []
    total_per_year = defaultdict(lambda: Decimal(0))

    custom_offer_rules = defaultdict(list)
    for rule in custom_rules:
        custom_offer_rules[rule.offerId].append(rule)

    for booking in bookings:
        year = booking.dateUsed.year

        if PhysicalOffersReimbursement().is_relevant(booking):
            total_per_year[year] += booking.total_amount

        rule = get_reimbursement_rule(booking, custom_offer_rules.get(booking.stock.offerId, []), total_per_year[year])
        reimbursements.append(BookingReimbursement(booking, rule, reimbursed_amount=rule.apply(booking)))

    return reimbursements


def get_reimbursement_rule(
    booking: Booking, custom_rules: tuple[ReimbursementRule], total_per_year: Decimal
) -> ReimbursementRule:
    # FIXME (dbaty, 2021-06-07): review this inner import once the
    # code has been moved to the `pcapi.core.payments` package.
    from pcapi.core.payments.models import CustomReimbursementRule  # avoid import loop

    candidates = []
    for rule in custom_rules + REGULAR_RULES:
        if not rule.is_active(booking):
            continue
        if not rule.is_relevant(booking, cumulative_value=total_per_year):
            continue
        if isinstance(rule, CustomReimbursementRule):
            return rule
        if isinstance(rule, ReimbursementRateForBookAbove20000):
            return rule
        candidates.append(rule)

    return min(candidates, key=lambda r: r.apply(booking))


# FIXME (rchaffal, 2021-07-15): temporary workaroud before implementing subcategory reimbursement rules for all offers
def _is_offer_an_exception_to_reimbursement_rules(offer: Offer) -> bool:
    return (
        offer.type in (str(ThingType.CINEMA_CARD), str(ThingType.LIVRE_EDITION))
        or offer.subcategoryId == subcategories.MUSEE_VENTE_DISTANCE.id
    )
