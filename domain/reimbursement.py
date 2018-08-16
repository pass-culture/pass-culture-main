from decimal import Decimal
from enum import Enum

from repository import booking_queries

MAX_REIMBURSEMENT_FOR_OFFERER_PER_YEAR = 23000


class Reimbursement:
    def __init__(self, is_active=True, rate=Decimal(0), description=''):
        self.is_active = is_active
        self.rate = rate
        self.description = description


class ReimbursementRule(Enum):
    NO_REIMBURSEMENT_OF_DIGITAL_THINGS = Reimbursement(
        description='Pas de remboursement pour les offres digitales'
    )
    FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS = Reimbursement(
        rate=Decimal(1),
        description='Remboursement total pour les offres physiques'
    )
    NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER = Reimbursement(
        description='Pas de remboursement au dessus du plafond de 23 000 € par offreur'
    )


def find_reimbursement_rule(
        booking,
        compute_total_booking_value_of_offerer=booking_queries.compute_total_booking_value_of_offerer):
    if booking.stock.resolvedOffer.eventOrThing.isDigital:
        return ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS

    offerer_id = booking.stock.resolvedOffer.venue.managingOfferer.id
    total_booking_value_of_offerer = compute_total_booking_value_of_offerer(offerer_id)

    eligible_rules = []

    eligible_rules.append(ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS)

    if total_booking_value_of_offerer > MAX_REIMBURSEMENT_FOR_OFFERER_PER_YEAR:
        eligible_rules.append(ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER)

    return _find_least_favorable_rule(eligible_rules)


def _find_least_favorable_rule(eligible_rules):
    return min(eligible_rules, key=lambda r: r.value.rate)
