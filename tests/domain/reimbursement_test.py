from datetime import datetime, timedelta
from decimal import Decimal

from freezegun import freeze_time

from domain.reimbursement import ReimbursementRules, find_all_booking_reimbursements, ReimbursementRule, CURRENT_RULES, \
    NEW_RULES
from models import BookingSQLEntity, ThingType
from model_creators.specific_creators import create_booking_for_thing, create_booking_for_event


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

    def test_is_not_relevant_for_digital_books(self):
        # given
        booking = create_booking_for_thing(url='http://my.book', amount=40, quantity=3, product_type=ThingType.LIVRE_EDITION)

        # when
        is_relevant = ReimbursementRules.DIGITAL_THINGS.value.is_relevant(booking)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_cinema_cards(self):
        # given
        booking = create_booking_for_thing(url='http://cinema.card', amount=40, quantity=3, product_type=ThingType.CINEMA_CARD)

        # when
        is_relevant = ReimbursementRules.DIGITAL_THINGS.value.is_relevant(booking)

        # then
        assert is_relevant is False


class PhysicalOffersReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.PHYSICAL_OFFERS.value.apply(booking)

        # then
        assert reimbursed_amount == booking.total_amount

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
        booking = create_booking_for_thing(url='http://my.book', amount=40, quantity=3, product_type=ThingType.LIVRE_EDITION)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_cinema_cards(self):
        # given
        booking = create_booking_for_thing(url='http://cinema.card', amount=40, quantity=2, product_type=ThingType.CINEMA_CARD)

        # when
        is_relevant = ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking)

        # then
        assert is_relevant is True


class ReimbursementRateByVenueBetween20000And40000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value.apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.95) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_relevant_for_booking_on_events_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_digital_things_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_thing(url='http://truc', amount=40, quantity=3)
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=30, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_below_20000(self):
        # given
        rule = ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value
        booking = create_booking_for_event(amount=30, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False


class ReimbursementRateByVenueBetween40000And150000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.BETWEEN_40000_AND_150000_EUROS.value.apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.85) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_40000(self):
        # given
        rule = ReimbursementRules.BETWEEN_40000_AND_150000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 40100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_40000(self):
        # given
        rule = ReimbursementRules.BETWEEN_40000_AND_150000_EUROS.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 40000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_40000(self):
        # given
        rule = ReimbursementRules.BETWEEN_40000_AND_150000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=30, quantity=3)
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False


class ReimbursementRateByVenueAbove150000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.ABOVE_150000_EUROS.value.apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.7) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_150000(self):
        # given
        rule = ReimbursementRules.ABOVE_150000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=40, quantity=3)
        cumulative_booking_value = 150100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_150000(self):
        # given
        rule = ReimbursementRules.ABOVE_150000_EUROS.value
        booking = create_booking_for_event(amount=40, quantity=3)
        cumulative_booking_value = 150000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_150000(self):
        # given
        rule = ReimbursementRules.ABOVE_150000_EUROS.value
        booking = create_booking_for_thing(url=None, amount=30, quantity=3)
        cumulative_booking_value = 149000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False


class ReimbursementRateForBookAbove20000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(product_type=ThingType.LIVRE_EDITION, url=None, amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.BOOK_REIMBURSEMENT.value.apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.95) * 40 * 3

    def test_is_relevant_for_booking_on_book_with_cumulative_value_below_20000(self):
        # given
        rule = ReimbursementRules.BOOK_REIMBURSEMENT.value
        booking = create_booking_for_thing(product_type=ThingType.LIVRE_EDITION, url=None, amount=40, quantity=3)
        cumulative_booking_value = 100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_not_relevant_for_booking_on_book_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = ReimbursementRules.BOOK_REIMBURSEMENT.value
        booking = create_booking_for_thing(product_type=ThingType.LIVRE_EDITION, url=None, amount=40, quantity=3)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is False

    def test_is_relevant_for_booking_on_book_with_cumulative_value_above_20000(self):
        # given
        rule = ReimbursementRules.BOOK_REIMBURSEMENT.value
        booking = create_booking_for_thing(product_type=ThingType.LIVRE_EDITION, url=None, amount=40, quantity=3)
        cumulative_booking_value = 55000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant is True


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


class ReimbursementRuleIsActiveTest:
    class DummyRule(ReimbursementRule):
        rate = Decimal(10)
        description = 'Dummy rule'
        valid_from = None
        valid_until = None

        def is_relevant(self, booking, **kwargs):
            return True

    booking = BookingSQLEntity()

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


class FindAllBookingsReimbursementsTest:
    class UsingCurrentReimbursementRulesTest:
        def test_returns_full_reimbursement_for_all_bookings(self):
            # given
            booking1 = create_booking_for_event(amount=50, quantity=1)
            booking2 = create_booking_for_thing(amount=40, quantity=3)
            booking3 = create_booking_for_event(amount=100, quantity=2)
            bookings = [booking1, booking2, booking3]

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, CURRENT_RULES)

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
            booking_reimbursements = find_all_booking_reimbursements(bookings, CURRENT_RULES)

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
            booking_reimbursements = find_all_booking_reimbursements(bookings, CURRENT_RULES)

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
            booking_reimbursements = find_all_booking_reimbursements(bookings, CURRENT_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
            assert_no_reimbursement_beyond_max(booking_reimbursements[2], booking3)

    class UsingNewReimbursementRulesTest:
        def test_returns_full_reimbursement_for_all_bookings(self):
            # given
            booking1 = create_booking_for_event(amount=50, quantity=1)
            booking2 = create_booking_for_thing(amount=40, quantity=3)
            booking3 = create_booking_for_event(amount=100, quantity=2)
            bookings = [booking1, booking2, booking3]

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

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
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[2], booking3)
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        def test_returns_full_reimbursement_when_cumulative_value_is_20000(self):
            # given
            booking1 = create_booking_for_event(amount=19990, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=10, quantity=1)
            bookings = [booking1, booking2, booking3]
            cumulative_value_for_bookings_1_and_3 = booking1.amount * booking1.quantity + \
                                                    booking3.amount * booking3.quantity

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_total_reimbursement(booking_reimbursements[2], booking3)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        def test_returns_95_reimbursement_rate_between_20000_and_40000_euros_for_most_recent_booking(self):
            # given
            booking1 = create_booking_for_event(amount=19990, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=20, quantity=1)
            bookings = [booking1, booking2, booking3]
            cumulative_value_for_bookings_1_and_3 = booking1.amount * booking1.quantity + \
                                                    booking3.amount * booking3.quantity

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        def test_returns_95_reimbursement_rate_between_20000_and_40000_when_cumulative_value_is_40000(self):
            # given
            booking1 = create_booking_for_event(amount=19000, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=19000, quantity=1)
            booking4 = create_booking_for_thing(amount=2000, quantity=1)
            bookings = [booking1, booking2, booking3, booking4]
            cumulative_value_for_bookings_1_and_3_and_4 = booking1.amount * booking1.quantity + \
                                                          booking3.amount * booking3.quantity + \
                                                          booking4.amount * booking4.quantity

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3,
                                            cumulative_value_for_bookings_1_and_3_and_4)
            assert_degressive_reimbursement(booking_reimbursements[3], booking4,
                                            cumulative_value_for_bookings_1_and_3_and_4)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        def test_returns_85_reimbursement_rate_between_40000_and_150000_euros_for_most_recent_booking(self):
            # given
            booking1 = create_booking_for_event(amount=19000, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=2000, quantity=12)
            bookings = [booking1, booking2, booking3]
            cumulative_value_for_bookings_1_and_3 = booking1.amount * booking1.quantity + \
                                                    booking3.amount * booking3.quantity

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        def test_returns_85_reimbursement_rate_between_40000_and_150000_when_cumulative_value_is_150000(self):
            # given
            booking1 = create_booking_for_event(amount=19000, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=19000, quantity=4)
            booking4 = create_booking_for_thing(amount=5000, quantity=1)
            bookings = [booking1, booking2, booking3, booking4]
            cumulative_value_for_bookings_1_and_3_and_4 = booking1.amount * booking1.quantity + \
                                                          booking3.amount * booking3.quantity + \
                                                          booking4.amount * booking4.quantity

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3,
                                            cumulative_value_for_bookings_1_and_3_and_4)
            assert_degressive_reimbursement(booking_reimbursements[3], booking4,
                                            cumulative_value_for_bookings_1_and_3_and_4)

        def test_returns_65_reimbursement_rate_above_150000_euros_for_last_booking(self):
            # given
            booking1 = create_booking_for_event(amount=19000, quantity=1)
            booking2 = create_booking_for_thing(url='http://truc', amount=50, quantity=3)
            booking3 = create_booking_for_thing(amount=2000, quantity=120)
            bookings = [booking1, booking2, booking3]

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3, 430000)
            assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

        @freeze_time('2019-02-14')
        def test_returns_full_reimbursement_for_all_bookings_for_new_civil_year(self):
            # given
            booking1 = create_booking_for_event(amount=10000, quantity=1, date_created=datetime(2018, 1, 1))
            booking2 = create_booking_for_thing(amount=10000, quantity=1, date_created=datetime(2018, 1, 1))
            booking3 = create_booking_for_event(amount=200, quantity=2, date_created=datetime(2019, 1, 1))
            bookings = [booking1, booking2, booking3]

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_total_reimbursement(booking_reimbursements[1], booking2)
            assert_total_reimbursement(booking_reimbursements[2], booking3)

        @freeze_time('2019-02-14')
        def test_returns_85_reimbursement_rate_between_20000_and_40000_euros_for_this_civil_year(self):
            # given
            booking1 = create_booking_for_event(amount=20000, quantity=1, date_created=datetime(2018, 1, 1))
            booking2 = create_booking_for_thing(amount=25000, quantity=1, date_created=datetime(2019, 1, 1))
            booking3 = create_booking_for_thing(amount=2000, quantity=1, date_created=datetime(2019, 1, 1))
            bookings = [booking1, booking2, booking3]

            # when
            booking_reimbursements = find_all_booking_reimbursements(bookings, NEW_RULES)

            # then
            assert_total_reimbursement(booking_reimbursements[0], booking1)
            assert_degressive_reimbursement(booking_reimbursements[1], booking2, 25000)
            assert_degressive_reimbursement(booking_reimbursements[2], booking3, 27000)


def assert_total_reimbursement(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.PHYSICAL_OFFERS
    assert booking_reimbursement.reimbursed_amount == booking.total_amount


def assert_no_reimbursement_for_digital(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.DIGITAL_THINGS
    assert booking_reimbursement.reimbursed_amount == 0


def assert_no_reimbursement_beyond_max(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert booking_reimbursement.reimbursement == ReimbursementRules.MAX_REIMBURSEMENT
    assert booking_reimbursement.reimbursed_amount == 0


def assert_degressive_reimbursement(booking_reimbursement, booking, total_amount):
    assert booking_reimbursement.booking == booking
    if 20000 < total_amount <= 40000:
        assert booking_reimbursement.reimbursement == ReimbursementRules.BETWEEN_20000_AND_40000_EUROS
        assert booking_reimbursement.reimbursed_amount == ReimbursementRules.BETWEEN_20000_AND_40000_EUROS.value.rate \
               * booking.total_amount
    elif 40000 < total_amount <= 150000:
        assert booking_reimbursement.reimbursement == ReimbursementRules.BETWEEN_40000_AND_150000_EUROS
        assert booking_reimbursement.reimbursed_amount == ReimbursementRules.BETWEEN_40000_AND_150000_EUROS.value.rate \
               * booking.total_amount
    elif total_amount > 150000:
        assert booking_reimbursement.reimbursement == ReimbursementRules.ABOVE_150000_EUROS
        assert booking_reimbursement.reimbursed_amount == ReimbursementRules.ABOVE_150000_EUROS.value.rate * booking.total_amount
    else:
        assert False
