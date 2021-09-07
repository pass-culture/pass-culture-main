from collections import defaultdict
from dataclasses import dataclass
import datetime
from decimal import Decimal
from typing import Optional

from pcapi.core.categories import subcategories
import pcapi.core.payments.models as payments_models
from pcapi.models import Booking
from pcapi.models import Offer


# A new set rules are in effect as of 1 September 2021 (i.e. 31 August 22:00 UTC)
SEPTEMBER_2021 = datetime.datetime(2021, 9, 1) - datetime.timedelta(hours=2)


class DigitalThingsReimbursement(payments_models.ReimbursementRule):
    rate = Decimal(0)
    description = "Pas de remboursement pour les offres digitales"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored") -> bool:
        offer = booking.stock.offer
        return (
            offer.subcategory.reimbursement_rule == subcategories.ReimbursementRuleChoices.NOT_REIMBURSED.value
            and not offer.isEducational
        )


class EducationalOffersReimbursement(payments_models.ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres éducationnelles"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored") -> bool:
        offer = booking.stock.offer
        return offer.isEducational


class PhysicalOffersReimbursement(payments_models.ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres physiques"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored") -> bool:
        return is_relevant_for_gradual_decreasing(booking.stock.offer)


class MaxReimbursementByOfferer(payments_models.ReimbursementRule):
    # This rule is not used anymore.
    rate = Decimal(0)
    description = "Pas de remboursement au dessus du plafond de 20 000 € par acteur culturel"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return cumulative_revenue > 20000


class LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000(payments_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% entre 20 000 € et 40 000 € par lieu"
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return 20000 < cumulative_revenue <= 40000


class LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000(payments_models.ReimbursementRule):
    rate = Decimal("0.85")
    description = "Remboursement à 85% entre 40 000 € et 150 000 € par lieu"
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return 40000 < cumulative_revenue <= 150000


class LegacyPreSeptember2021ReimbursementRateByVenueAbove150000(payments_models.ReimbursementRule):
    rate = Decimal("0.70")
    description = "Remboursement à 70% au dessus de 150 000 € par lieu"
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return cumulative_revenue > 150000


class ReimbursementRateByVenueBetween20000And40000(payments_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% entre 20 000 € et 40 000 € par lieu (>= 2021-09-01)"
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return 20000 < cumulative_revenue <= 40000


class ReimbursementRateByVenueBetween40000And150000(payments_models.ReimbursementRule):
    rate = Decimal("0.92")
    description = "Remboursement à 92% entre 40 000 € et 150 000 € par lieu (>= 2021-09-01)"
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return 40000 < cumulative_revenue <= 150000


class ReimbursementRateByVenueAbove150000(payments_models.ReimbursementRule):
    rate = Decimal("0.90")
    description = "Remboursement à 90% au dessus de 150 000 € par lieu (>= 2021-09-01)"
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if not is_relevant_for_gradual_decreasing(booking.stock.offer):
            return False
        return cumulative_revenue > 150000


class ReimbursementRateForBookAbove20000(payments_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% au dessus de 20 000 € pour les livres"
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        if booking.stock.offer.subcategory.reimbursement_rule != subcategories.ReimbursementRuleChoices.BOOK.value:
            return False
        if booking.stock.offer.isEducational:
            return False
        return cumulative_revenue > 20000


REGULAR_RULES = [
    DigitalThingsReimbursement(),
    EducationalOffersReimbursement(),
    PhysicalOffersReimbursement(),
    LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000(),
    LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000(),
    LegacyPreSeptember2021ReimbursementRateByVenueAbove150000(),
    ReimbursementRateByVenueBetween20000And40000(),
    ReimbursementRateByVenueBetween40000And150000(),
    ReimbursementRateByVenueAbove150000(),
    ReimbursementRateForBookAbove20000(),
]


@dataclass
class BookingReimbursement:
    booking: Booking
    rule: payments_models.ReimbursementRule
    reimbursed_amount: Decimal


class CustomRuleFinder:
    def __init__(self):
        self.rules = payments_models.CustomReimbursementRule.query.all()
        self.rules_by_offer = self._partition_by_field("offerId")
        self.rules_by_offerer = self._partition_by_field("offererId")

    def _partition_by_field(self, field: str):
        cache = {}
        for rule in self.rules:
            cache.setdefault(getattr(rule, field), []).append(rule)
        return cache

    def get_rule(self, booking: Booking) -> Optional[payments_models.CustomReimbursementRule]:
        for rule in self.rules_by_offer.get(booking.stock.offerId, ()):
            if rule.matches(booking):
                return rule
        for rule in self.rules_by_offerer.get(booking.offererId, ()):
            if rule.matches(booking):
                return rule
        return None


def find_all_booking_reimbursements(
    bookings: list[Booking], custom_rule_finder: CustomRuleFinder
) -> list[BookingReimbursement]:
    reimbursements = []
    total_per_year: dict[int, Decimal] = defaultdict(lambda: Decimal(0))

    for booking in bookings:
        year = booking.dateUsed.year

        if is_relevant_for_gradual_decreasing(booking.stock.offer):
            total_per_year[year] += booking.total_amount

        rule = get_reimbursement_rule(booking, custom_rule_finder, total_per_year[year])
        reimbursements.append(BookingReimbursement(booking, rule, reimbursed_amount=rule.apply(booking)))

    return reimbursements


def get_reimbursement_rule(
    booking: Booking, custom_rule_finder: CustomRuleFinder, cumulative_revenue: Decimal
) -> payments_models.ReimbursementRule:
    custom_rule = custom_rule_finder.get_rule(booking)
    if custom_rule:
        return custom_rule

    candidates = []
    for rule in REGULAR_RULES:
        if not rule.matches(booking, cumulative_revenue):
            continue
        if isinstance(rule, ReimbursementRateForBookAbove20000):
            return rule
        candidates.append(rule)

    return min(candidates, key=lambda r: r.apply(booking))


def is_relevant_for_gradual_decreasing(offer: Offer) -> bool:
    return (
        not offer.isEducational
        and offer.subcategory.reimbursement_rule == subcategories.ReimbursementRuleChoices.STANDARD.value
    )
