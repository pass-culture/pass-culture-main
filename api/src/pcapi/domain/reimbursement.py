import datetime
from decimal import Decimal

from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.finance import utils as finance_utils
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.offers.models import Offer


# A new set rules are in effect as of 1 September 2021 (i.e. 31 August 22:00 UTC)
SEPTEMBER_2021 = datetime.datetime(2021, 9, 1) - datetime.timedelta(hours=2)


class DigitalThingsReimbursement(finance_models.ReimbursementRule):
    rate = Decimal(0)
    description = "Pas de remboursement pour les offres digitales"
    group = finance_models.RuleGroup.NOT_REIMBURSED
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        offer = booking.stock.offer
        return offer.subcategory.reimbursement_rule == subcategories.ReimbursementRuleChoices.NOT_REIMBURSED.value


class EducationalOffersReimbursement(finance_models.ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres éducationnelles"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking | CollectiveBooking, cumulative_revenue: int) -> bool:
        return isinstance(booking, CollectiveBooking)

    def apply(self, booking: CollectiveBooking, custom_total_amount: int | None = None) -> int:
        base = custom_total_amount or finance_utils.to_eurocents(booking.collectiveStock.price)
        return int(base * self.rate)


class CommercialGestureReimbursementRule(finance_models.ReimbursementRule):
    # This rule is used to allow full reimbursement of commercial gesture regardless of the cancelled related bookings
    rate = Decimal(1)
    description = "Remboursement total pour les gestes commerciaux"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        return False


class PhysicalOffersReimbursement(finance_models.ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement total pour les offres physiques"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        return is_relevant_for_standard_reimbursement_rule(booking.stock.offer)


class MaxReimbursementByOfferer(finance_models.ReimbursementRule):
    # This rule is not used anymore.
    rate = Decimal(0)
    description = "Pas de remboursement au dessus du plafond de 20 000 € par acteur culturel"
    group = finance_models.RuleGroup.DEPRECATED
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return cumulative_revenue > (20_000 * 100)  # eurocents


class LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000(finance_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% entre 20 000 € et 40 000 € par lieu"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return (20_000 * 100) < cumulative_revenue <= (40_000 * 100)  # eurocents


class LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000(finance_models.ReimbursementRule):
    rate = Decimal("0.85")
    description = "Remboursement à 85% entre 40 000 € et 150 000 € par lieu"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return (40_000 * 100) < cumulative_revenue <= (150_000 * 100)  # eurocents


class LegacyPreSeptember2021ReimbursementRateByVenueAbove150000(finance_models.ReimbursementRule):
    rate = Decimal("0.70")
    description = "Remboursement à 70% au dessus de 150 000 € par lieu"
    group = finance_models.RuleGroup.STANDARD
    valid_from = None
    valid_until = SEPTEMBER_2021

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return cumulative_revenue > (150_000 * 100)  # eurocents


class ReimbursementRateByVenueBetween20000And40000(finance_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% entre 20 000 € et 40 000 € par lieu (>= 2021-09-01)"
    group = finance_models.RuleGroup.STANDARD
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return (20_000 * 100) < cumulative_revenue <= (40_000 * 100)  # eurocents


class ReimbursementRateByVenueBetween40000And150000(finance_models.ReimbursementRule):
    rate = Decimal("0.92")
    description = "Remboursement à 92% entre 40 000 € et 150 000 € par lieu (>= 2021-09-01)"
    group = finance_models.RuleGroup.STANDARD
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return (40_000 * 100) < cumulative_revenue <= (150_000 * 100)  # eurocents


class ReimbursementRateByVenueAbove150000(finance_models.ReimbursementRule):
    rate = Decimal("0.90")
    description = "Remboursement à 90% au dessus de 150 000 € par lieu (>= 2021-09-01)"
    group = finance_models.RuleGroup.STANDARD
    valid_from = SEPTEMBER_2021
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if not is_relevant_for_standard_reimbursement_rule(booking.stock.offer):
            return False
        return cumulative_revenue > (150_000 * 100)  # eurocents


class ReimbursementRateForBookBelow20000(finance_models.ReimbursementRule):
    rate = Decimal(1)
    description = "Remboursement à 100% jusqu'à 20 000 € pour les livres"
    group = finance_models.RuleGroup.BOOK
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if booking.stock.offer.subcategory.reimbursement_rule != subcategories.ReimbursementRuleChoices.BOOK.value:
            return False
        return cumulative_revenue <= (20_000 * 100)  # eurocents


class ReimbursementRateForBookAbove20000(finance_models.ReimbursementRule):
    rate = Decimal("0.95")
    description = "Remboursement à 95% au dessus de 20 000 € pour les livres"
    group = finance_models.RuleGroup.BOOK
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, cumulative_revenue: int) -> bool:
        if booking.stock.offer.subcategory.reimbursement_rule != subcategories.ReimbursementRuleChoices.BOOK.value:
            return False
        return cumulative_revenue > (20_000 * 100)  # eurocents


REGULAR_RULES = [
    DigitalThingsReimbursement(),
    EducationalOffersReimbursement(),
    PhysicalOffersReimbursement(),
    CommercialGestureReimbursementRule(),
    LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000(),
    LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000(),
    LegacyPreSeptember2021ReimbursementRateByVenueAbove150000(),
    ReimbursementRateByVenueBetween20000And40000(),
    ReimbursementRateByVenueBetween40000And150000(),
    ReimbursementRateByVenueAbove150000(),
    ReimbursementRateForBookBelow20000(),
    ReimbursementRateForBookAbove20000(),
]

# A description must be unique and should never be modified, or it will break Invoice generation
assert [r.description for r in REGULAR_RULES] == [
    "Pas de remboursement pour les offres digitales",
    "Remboursement total pour les offres éducationnelles",
    "Remboursement total pour les offres physiques",
    "Remboursement total pour les gestes commerciaux",
    "Remboursement à 95% entre 20 000 € et 40 000 € par lieu",
    "Remboursement à 85% entre 40 000 € et 150 000 € par lieu",
    "Remboursement à 70% au dessus de 150 000 € par lieu",
    "Remboursement à 95% entre 20 000 € et 40 000 € par lieu (>= 2021-09-01)",
    "Remboursement à 92% entre 40 000 € et 150 000 € par lieu (>= 2021-09-01)",
    "Remboursement à 90% au dessus de 150 000 € par lieu (>= 2021-09-01)",
    "Remboursement à 100% jusqu'à 20 000 € pour les livres",
    "Remboursement à 95% au dessus de 20 000 € pour les livres",
]


class CustomRuleFinder:
    def __init__(self) -> None:
        self.rules = finance_models.CustomReimbursementRule.query.all()
        self.rules_by_offer = self._partition_by_field("offerId")
        self.rules_by_venue = self._partition_by_field("venueId")
        self.rules_by_offerer = self._partition_by_field("offererId")

    def _partition_by_field(self, field: str) -> dict:
        cache: dict[int, list[finance_models.CustomReimbursementRule]] = {}
        for rule in self.rules:
            cache.setdefault(getattr(rule, field), []).append(rule)
        return cache

    def get_rule(self, booking: Booking) -> finance_models.CustomReimbursementRule | None:
        for rule in self.rules_by_offer.get(booking.stock.offerId, ()):
            if rule.matches(booking, cumulative_revenue=0):  # cumulative revenue is ignored
                return rule
        for rule in self.rules_by_venue.get(finance_api.get_pricing_point_link(booking).pricingPointId, ()):
            if rule.matches(booking, cumulative_revenue=0):  # cumulative revenue is ignored
                return rule
        for rule in self.rules_by_offerer.get(booking.offererId, ()):
            if rule.matches(booking, cumulative_revenue=0):  # cumulative revenue is ignored
                return rule
        return None


def get_reimbursement_rule(
    booking: Booking | CollectiveBooking,
    custom_rule_finder: CustomRuleFinder,
    cumulative_revenue: int,
) -> finance_models.ReimbursementRule:
    if isinstance(booking, CollectiveBooking):
        return EducationalOffersReimbursement()

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


def is_relevant_for_standard_reimbursement_rule(offer: Offer) -> bool:
    return offer.subcategory.reimbursement_rule == subcategories.ReimbursementRuleChoices.STANDARD.value
