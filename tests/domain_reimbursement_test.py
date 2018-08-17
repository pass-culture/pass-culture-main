from decimal import Decimal

import pytest

from domain.reimbursement import find_reimbursement_rule, ReimbursementRule, find_all_booking_reimbursement, \
    BookingReimbursement
from models import Offerer
from utils.test_utils import create_booking_for_thing, create_booking_for_event


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_no_reimbursement_of_digital_things_if_booking_is_digital():
    # given
    booking = create_booking_for_thing(url='http://truc')

    # when
    reimbursement_rule = find_reimbursement_rule(booking, Decimal(100))

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement pour les offres digitales'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_full_reimbursement_of_physical_offers_if_booking_is_on_a_physical_thing():
    # given
    booking = create_booking_for_thing(url=None)

    # when
    reimbursement_rule = find_reimbursement_rule(booking, Decimal(100))

    # then
    assert reimbursement_rule is ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(1)
    assert reimbursement_rule.value.description == 'Remboursement total pour les offres physiques'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_full_reimbursement_of_physical_offers_if_booking_is_on_a_physical_event():
    # given
    booking = create_booking_for_event()

    # when
    reimbursement_rule = find_reimbursement_rule(booking, Decimal(100))

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

    # when
    reimbursement_rule = find_reimbursement_rule(booking, Decimal(23100))

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement au dessus du plafond de 23 000 € par offreur'


@pytest.mark.standalone
def test_find_reimbursement_rule_returns_no_reimbursement_above_23_000_euros_by_offerer_if_booking_is_on_a_physical_event():
    # given
    booking = create_booking_for_event()

    # when
    reimbursement_rule = find_reimbursement_rule(booking, Decimal(23100))

    # then
    assert reimbursement_rule is ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER
    assert reimbursement_rule.value.is_active is True
    assert reimbursement_rule.value.rate == Decimal(0)
    assert reimbursement_rule.value.description == 'Pas de remboursement au dessus du plafond de 23 000 € par offreur'


@pytest.mark.standalone
def test_find_all_booking_reimbursement_returns_full_reimbursement_for_all_bookings():
    # given
    booking1 = create_booking_for_event(amount=50, quantity=1)
    booking2 = create_booking_for_thing(amount=40, quantity=3)
    booking3 = create_booking_for_event(amount=100, quantity=2)

    bookings = [booking1, booking2, booking3]
    cumulative_booking_values = [50, 170, 370]

    # when
    booking_reimbursements = find_all_booking_reimbursement(bookings, cumulative_booking_values)

    # then
    assert booking_reimbursements == [
        BookingReimbursement(booking1, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS),
        BookingReimbursement(booking2, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS),
        BookingReimbursement(booking3, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS)
    ]


@pytest.mark.standalone
def test_find_all_booking_reimbursement_returns_a_different_reimbursement_for_digital_booking():
    # given
    booking1 = create_booking_for_event(amount=50, quantity=1)
    booking2 = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
    booking3 = create_booking_for_event(amount=100, quantity=2)

    bookings = [booking1, booking2, booking3]
    cumulative_booking_values = [50, 170, 370]

    # when
    booking_reimbursements = find_all_booking_reimbursement(bookings, cumulative_booking_values)

    # then
    assert booking_reimbursements == [
        BookingReimbursement(booking1, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS),
        BookingReimbursement(booking2, ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS),
        BookingReimbursement(booking3, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS)
    ]


@pytest.mark.standalone
def test_find_all_booking_reimbursement_returns_no_reimbursement_above_23000_euros_for_last_booking():
    # given
    booking1 = create_booking_for_event(amount=50, quantity=1)
    booking2 = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
    booking3 = create_booking_for_thing(amount=1000, quantity=23)

    bookings = [booking1, booking2, booking3]
    cumulative_booking_values = [50, 170, 23170]

    # when
    booking_reimbursements = find_all_booking_reimbursement(bookings, cumulative_booking_values)

    # then
    assert booking_reimbursements == [
        BookingReimbursement(booking1, ReimbursementRule.FULL_REIMBURSEMENT_OF_PHYSICAL_OFFERS),
        BookingReimbursement(booking2, ReimbursementRule.NO_REIMBURSEMENT_OF_DIGITAL_THINGS),
        BookingReimbursement(booking3, ReimbursementRule.NO_REIMBURSEMENT_ABOVE_23_000_EUROS_BY_OFFERER)
    ]
