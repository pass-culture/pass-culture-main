import pytest

from domain.reimbursement import ReimbursementRules, find_all_booking_reimbursement
from utils.test_utils import create_booking_for_thing, create_booking_for_event


@pytest.mark.standalone
class DigitalThingsReimbursementTest:
    def test_is_relevant_for_booking_on_digital_things(self):
        # given
        rule = ReimbursementRules.DIGITAL_THINGS.value
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_physical_things(self):
        # given
        rule = ReimbursementRules.DIGITAL_THINGS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events(self):
        # given
        rule = ReimbursementRules.DIGITAL_THINGS.value
        booking = create_booking_for_event(amount=50, quantity=1)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is False


@pytest.mark.standalone
class PhysicalOffersReimbursementTest:
    def test_is_relevant_for_booking_on_physical_things(self):
        # given
        rule = ReimbursementRules.PHYSICAL_OFFERS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events(self):
        # given
        rule = ReimbursementRules.PHYSICAL_OFFERS.value
        booking = create_booking_for_event(amount=50, quantity=1)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_digital_things(self):
        # given
        rule = ReimbursementRules.PHYSICAL_OFFERS.value
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        is_relevant = rule.apply(booking)

        # then
        assert is_relevant is False


@pytest.mark.standalone
class MaxReimbursementByOffererTest:
    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 23100

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events_with_cumulative_value_above_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 23100

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_of_exactly_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 23000

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events_with_cumulative_value_of_exactly_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 23000

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_digital_things_with_cumulative_value_above_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
        cumulative_booking_value = 23100

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_below_23000(self):
        # given
        rule = ReimbursementRules.MAX_REIMBURSEMENT.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.apply(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False


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
        assert booking_reimbursements[0].booking == booking1
        assert booking_reimbursements[0].reimbursement == ReimbursementRules.PHYSICAL_OFFERS
        assert booking_reimbursements[1].booking == booking2
        assert booking_reimbursements[1].reimbursement == ReimbursementRules.PHYSICAL_OFFERS
        assert booking_reimbursements[2].booking == booking3
        assert booking_reimbursements[2].reimbursement == ReimbursementRules.PHYSICAL_OFFERS

    def test_returns_a_different_reimbursement_for_digital_booking(self):
        # given
        booking1 = create_booking_for_event(amount=50, quantity=1)
        booking2 = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
        booking3 = create_booking_for_event(amount=100, quantity=2)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert booking_reimbursements[0].booking == booking1
        assert booking_reimbursements[0].reimbursement == ReimbursementRules.PHYSICAL_OFFERS
        assert booking_reimbursements[1].booking == booking2
        assert booking_reimbursements[1].reimbursement == ReimbursementRules.DIGITAL_THINGS
        assert booking_reimbursements[2].booking == booking3
        assert booking_reimbursements[2].reimbursement == ReimbursementRules.PHYSICAL_OFFERS

    def test_returns_full_reimbursement_for_all_bookings_above_23000_if_rule_is_deactivated(self):
        # given
        booking1 = create_booking_for_event(amount=50, quantity=1)
        booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
        booking3 = create_booking_for_thing(amount=2295, quantity=10)
        bookings = [booking1, booking2, booking3]
        ReimbursementRules.MAX_REIMBURSEMENT.value.is_active = False

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert booking_reimbursements[0].booking == booking1
        assert booking_reimbursements[0].reimbursement == ReimbursementRules.PHYSICAL_OFFERS
        assert booking_reimbursements[1].booking == booking2
        assert booking_reimbursements[1].reimbursement == ReimbursementRules.DIGITAL_THINGS
        assert booking_reimbursements[2].booking == booking3
        assert booking_reimbursements[2].reimbursement == ReimbursementRules.PHYSICAL_OFFERS

        # tear down
        ReimbursementRules.MAX_REIMBURSEMENT.value.is_active = True

    def test_returns_no_reimbursement_above_23000_euros_for_last_booking(self):
        # given
        booking1 = create_booking_for_event(amount=50, quantity=1)
        booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
        booking3 = create_booking_for_thing(amount=2295, quantity=10)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = find_all_booking_reimbursement(bookings)

        # then
        assert booking_reimbursements[0].booking == booking1
        assert booking_reimbursements[0].reimbursement == ReimbursementRules.PHYSICAL_OFFERS
        assert booking_reimbursements[1].booking == booking2
        assert booking_reimbursements[1].reimbursement == ReimbursementRules.DIGITAL_THINGS
        assert booking_reimbursements[2].booking == booking3
        assert booking_reimbursements[2].reimbursement == ReimbursementRules.MAX_REIMBURSEMENT
