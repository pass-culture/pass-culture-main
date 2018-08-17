from decimal import Decimal
from enum import Enum
from itertools import accumulate

MAX_REIMBURSEMENT_FOR_OFFERER_PER_YEAR = 23000


class BookingReimbursement:
    def __init__(self, booking, reimbursement):
        self.booking = booking
        self.reimbursement = reimbursement

    def __eq__(self, other):
        return self.booking == other.booking \
               and self.reimbursement == other.reimbursement

    def __repr__(self):
        return repr(self.booking) + repr(self.reimbursement)

    def as_dict(self):
        return {
            'booking': self.booking._asdict(),
            'reimbursement': self.reimbursement.as_dict()
        }


class Reimbursement:
    def __init__(self, is_active=True, rate=Decimal(0), description=''):
        self.is_active = is_active
        self.rate = rate
        self.description = description

    def as_dict(self):
        return {
            'rate': self.rate,
            'description': self.description
        }

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

    def as_dict(self):
        return {
            'name': self.name,
            'rule': self.value.as_dict()
        }

def compute_cumulative_booking_values(bookings):
    booking_values = list(map(compute_booking_reimbursable_value, bookings))
    return list(accumulate(booking_values))


def compute_booking_reimbursable_value(booking):
    return 0 if booking.stock.resolvedOffer.eventOrThing.isDigital else booking.value


def find_all_booking_reimbursement(bookings, cumulative_booking_values):
    booking_reimbursements = []
    for booking, value in zip(bookings, cumulative_booking_values):
        rule = find_reimbursement_rule(booking, value)
        booking_reimbursements.append(BookingReimbursement(booking, rule))
    return booking_reimbursements


def find_reimbursement_rule(
        booking,
        cumulated_booking_value):
    if booking.stock.resolvedOffer.eventOrThing.isDigital:
        return ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS

    eligible_rules = []

    eligible_rules.append(ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS)

    if cumulated_booking_value > MAX_REIMBURSEMENT_FOR_OFFERER_PER_YEAR:
        eligible_rules.append(ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER)

    return _find_least_favorable_rule(eligible_rules)


def _find_least_favorable_rule(eligible_rules):
    return min(eligible_rules, key=lambda r: r.value.rate)
