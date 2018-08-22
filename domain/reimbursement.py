from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum


class BookingReimbursement:
    def __init__(self, booking, reimbursement):
        self.booking = booking
        self.reimbursement = reimbursement

    def as_dict(self):
        return {
            'booking': self.booking._asdict(),
            'reimbursement': {
                'name': self.reimbursement.name,
                'description': self.reimbursement.value.description,
                'rate': self.reimbursement.value.rate,
            }
        }


class ReimbursementRule(ABC):
    @abstractmethod
    def apply(self, booking, **kwargs):
        pass


class DigitalThingsReimbursement(ReimbursementRule):
    rate = Decimal(0)
    description = 'Pas de remboursement pour les offres digitales'
    is_active = True

    def apply(self, booking, **kwargs):
        return booking.stock.resolvedOffer.eventOrThing.isDigital


class PhysicalOffersReimbursement(ReimbursementRule):
    rate = Decimal(1)
    description = 'Remboursement total pour les offres physiques'
    is_active = True

    def apply(self, booking, **kwargs):
        return not booking.stock.resolvedOffer.eventOrThing.isDigital


class MaxReimbursementByOfferer(ReimbursementRule):
    rate = Decimal(0)
    description = 'Pas de remboursement au dessus du plafond de 23 000 € par offreur'
    is_active = True

    def apply(self, booking, **kwargs):
        if booking.stock.resolvedOffer.eventOrThing.isDigital:
            return False
        else:
            return kwargs['cumulative_value'] >= 23000


class ReimbursementRules(Enum):
    DIGITAL_THINGS = DigitalThingsReimbursement()
    PHYSICAL_OFFERS = PhysicalOffersReimbursement()
    MAX_REIMBURSEMENT = MaxReimbursementByOfferer()


def find_all_booking_reimbursement(bookings):
    reimbursements = []
    cumulative_bookings_value = 0
    for booking in bookings:
        if ReimbursementRules.PHYSICAL_OFFERS.value.apply(booking):
            cumulative_bookings_value = cumulative_bookings_value + booking.value
        potential_rules = _find_potential_rules(booking, cumulative_bookings_value)
        elected_rule = min(potential_rules, key=lambda r: r.value.rate)
        reimbursements.append(BookingReimbursement(booking, elected_rule))
    return reimbursements


def _find_potential_rules(booking, cumulative_bookings_value):
    relevant_rules = []
    for rule in ReimbursementRules:
        if rule.value.is_active and rule.value.apply(booking, cumulative_value=cumulative_bookings_value):
            relevant_rules.append(rule)
    return relevant_rules
