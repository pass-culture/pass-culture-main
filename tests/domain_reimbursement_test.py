from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from domain.reimbursement import ReimbursementRules, find_all_booking_reimbursement, ReimbursementRule
from models import Booking, ThingType
from tests.test_utils import create_booking_for_thing, create_booking_for_event


@pytest.mark.standalone
class DigitalThingsReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.DIGITAL_THINGS.value.apply(booking)

        # then
        assert reimbursed_amount == 0

    def test_relevant_for_booking_on_digital_things(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        is_relevant = ReimbursementRules.DIGITAL_THINGS.value.is_relevant(booking)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_physical_things(self):
        # given
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)

        # when
        is_relevant = ReimbursementRules.DIGITAL_THINGS.value.is_relevant(booking)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events(self):
        # given
        booking = create_booking_for_event(amount=50, quantity=1)

        # when
        is_relevant = ReimbursementRules.DIGITAL_THINGS.value.is_relevant(booking)

        # then
        assert is_relevant is False


@pytest.mark.standalone
class PhysicalOffersReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.PHYSICAL_OFFERS.value.apply(booking)

        # then
        assert reimbursed_amount == booking.value

    def test_is_relevant_for_booking_on_physical_things(self):
        # given
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events(self):
        # given
        booking = create_booking_for_event(amount=50, quantity=1)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_digital_things(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is False

    def test_is_relevant_for_booking_on_digital_books(self):
        # given
        booking = create_booking_for_thing(url='http://my.book', amount=40, quantity=3, type=ThingType.LIVRE_EDITION)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is True


@pytest.mark.standalone
class MaxReimbursementByOffererTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.MAX_REIMBURSEMENT.value.apply(booking)

        # then
        assert reimbursed_amount == 0

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_digital_things_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=30, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_below_20000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=30, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False


@pytest.mark.standalone
class ReimbursementRuleIsActiveTest:
    class DummyRule(ReimbursementRule):
        rate = Decimal(10)
        description = 'Dummy rule'
        valid_from = None
        valid_until = None

        def is_relevant(self, booking, **kwargs):
            return True

    booking = Booking()

    def test_is_active_if_valid_from_is_none_and_valid_until_is_none(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = None
        self.DummyRule.valid_until = None

        # then
        assert self.DummyRule().is_active(self.booking) is True

    def test_is_active_if_valid_from_is_past_and_valid_until_is_none(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = datetime.utcnow() - timedelta(weeks=3)
        self.DummyRule.valid_until = None

        # then
        assert self.DummyRule().is_active(self.booking) is True

    def test_is_not_active_if_valid_from_is_future_and_valid_until_is_none(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = datetime.utcnow() + timedelta(weeks=3)
        self.DummyRule.valid_until = None

        # then
        assert self.DummyRule().is_active(self.booking) is False

    def test_is_active_if_valid_from_is_none_and_valid_until_is_future(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = None
        self.DummyRule.valid_until = datetime.utcnow() + timedelta(weeks=3)

        # then
        assert self.DummyRule().is_active(self.booking) is True

    def test_is_not_active_if_valid_from_is_none_and_valid_until_is_past(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = None
        self.DummyRule.valid_until = datetime.utcnow() - timedelta(weeks=3)

        # then
        assert self.DummyRule().is_active(self.booking) is False

    def test_is_active_if_valid_from_is_past_and_valid_until_is_future(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = datetime.utcnow() - timedelta(weeks=3)
        self.DummyRule.valid_until = datetime.utcnow() + timedelta(weeks=3)

        # then
        assert self.DummyRule().is_active(self.booking) is True

    def test_is_not_active_if_valid_from_is_future_and_valid_until_is_future(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = datetime.utcnow() + timedelta(weeks=3)
        self.DummyRule.valid_until = datetime.utcnow() + timedelta(weeks=6)

        # then
        assert self.DummyRule().is_active(self.booking) is False

    def test_is_not_active_if_valid_from_is_past_and_valid_until_is_past(self):
        # given
        self.booking.dateCreated = datetime.utcnow()
        self.DummyRule.valid_from = datetime.utcnow() - timedelta(weeks=3)
        self.DummyRule.valid_until = datetime.utcnow() - timedelta(weeks=6)

        # then
        assert self.DummyRule().is_active(self.booking) is False


@pytest.mark.standalone
class FindAllBookingsReimbursementsTest:
    def test_returns_full_reimbursement_for_all_bookings(self):
        # given
        booking1 = create_booking_for_event(amount=50, quantity=1)
        booking2 = create_booking_for_thing(amount=40, quantity=3)
        booking3 = create_booking_for_event(amount=100, quantity=2)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_total_reimbursement(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

    def test_returns_a_different_reimbursement_for_digital_booking(self):
        # given
        booking1 = create_booking_for_event(amount=50, quantity=1)
        booking2 = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
        booking3 = create_booking_for_event(amount=100, quantity=2)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

    def test_returns_full_reimbursement_for_all_bookings_above_20000_if_rule_is_not_valid_anymore(self):
        # given
        now = datetime.utcnow()
        booking1 = create_booking_for_event(amount=50, quantity=1, date_created=now)
        booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3, date_created=now)
        booking3 = create_booking_for_thing(amount=1995, quantity=10, date_created=now)
        bookings = [booking1, booking2, booking3]
        ReimbursementRules.MAX_REIMBURSEMENT.value.valid_from = now - timedelta(weeks=5)
        ReimbursementRules.MAX_REIMBURSEMENT.value.valid_until = now + timedelta(weeks=5)

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

        # tear down
        ReimbursementRules.MAX_REIMBURSEMENT.value.valid_from = None
        ReimbursementRules.MAX_REIMBURSEMENT.value.valid_until = None

    def test_returns_no_reimbursement_above_20000_euros_for_last_booking(self):
        # given
        booking1 = create_booking_for_event(amount=60, quantity=1)
        booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
        booking3 = create_booking_for_thing(amount=1995, quantity=10)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
        assert_no_reimbursement_beyond_max(booking_reimbursements[2], booking3)


def assert_total_reimbursement(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.PHYSICAL_OFFERS
    assert booking_reimbursement.reimbursed_amount == booking.value


def assert_no_reimbursement_for_digital(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.DIGITAL_THINGS
    assert booking_reimbursement.reimbursed_amount == 0


def assert_no_reimbursement_beyond_max(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.MAX_REIMBURSEMENT
    assert booking_reimbursement.reimbursed_amount == 0
