from decimal import Decimal
from unittest.mock import Mock

import pytest

from domain.reimbursement import find_reimbursement_rule, ReimbursementRule
from models import Offerer, Venue
from utils.test_utils import create_booking_for_thing, create_booking_for_event

mocked_compute_total_booking_value = Mock()


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_no_reimbursement_of_digital_things_if_booking_is_digital():
    # given
    offerer = Offerer()
    offerer.id = 123
    booking = create_booking_for_thing(url='http://truc')
    booking.stock.resolvedOffer.venue = Venue()
    booking.stock.resolvedOffer.venue.managingOfferer = offerer

    mocked_compute_total_booking_value.return_value = Decimal(100)

    # when
    reimbursement_rule = find_reimbursement_rule(booking,
                                                 compute_total_booking_value_of_offerer=mocked_compute_total_booking_value)

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement pour les offres digitales'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_full_reimbursement_of_physical_offers_if_booking_is_on_a_physical_thing():
    # given
    offerer = Offerer()
    offerer.id = 123
    booking = create_booking_for_thing(url=None)
    booking.stock.resolvedOffer.venue = Venue()
    booking.stock.resolvedOffer.venue.managingOfferer = offerer

    mocked_compute_total_booking_value.return_value = Decimal(100)

    # when
    reimbursement_rule = find_reimbursement_rule(booking,
                                                 compute_total_booking_value_of_offerer=mocked_compute_total_booking_value)

    # then
    assert reimbursement_rule is ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(1)
    assert reimbursement_rule.value.description == 'Remboursement total pour les offres physiques'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_full_reimbursement_of_physical_offers_if_booking_is_on_a_physical_event():
    # given
    offerer = Offerer()
    offerer.id = 123
    booking = create_booking_for_event()
    booking.stock.resolvedOffer.venue = Venue()
    booking.stock.resolvedOffer.venue.managingOfferer = offerer

    mocked_compute_total_booking_value.return_value = Decimal(100)

    # when
    reimbursement_rule = find_reimbursement_rule(booking,
                                                 compute_total_booking_value_of_offerer=mocked_compute_total_booking_value)

    # then
    assert reimbursement_rule is ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(1)
    assert reimbursement_rule.value.description == 'Remboursement total pour les offres physiques'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_no_reimbursement_above_23_000_euros_by_offerer_if_booking_is_on_a_physical_thing():
    # given
    offerer = Offerer()
    offerer.id = 123
    booking = create_booking_for_thing()
    booking.stock.resolvedOffer.venue = Venue()
    booking.stock.resolvedOffer.venue.managingOfferer = offerer

    mocked_compute_total_booking_value.return_value = Decimal(23100)

    # when
    reimbursement_rule = find_reimbursement_rule(booking,
                                                 compute_total_booking_value_of_offerer=mocked_compute_total_booking_value)

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement au dessus du plafond de 23 000 € par offreur'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_no_reimbursement_above_23_000_euros_by_offerer_if_booking_is_on_a_physical_event():
    # given
    offerer = Offerer()
    offerer.id = 123
    booking = create_booking_for_event()
    booking.stock.resolvedOffer.venue = Venue()
    booking.stock.resolvedOffer.venue.managingOfferer = offerer

    mocked_compute_total_booking_value.return_value = Decimal(23100)

    # when
    reimbursement_rule = find_reimbursement_rule(booking,
                                                 compute_total_booking_value_of_offerer=mocked_compute_total_booking_value)

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement au dessus du plafond de 23 000 € par offreur'
