from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.payments.models as payments_models
import pcapi.core.users.factories as users_factories
from pcapi.domain import reimbursement
from pcapi.models import Booking
from pcapi.repository import repository


def create_non_digital_thing_booking(quantity=1, price=10, user=None, date_created=None, product_subcategory_id=None):
    booking_kwargs = {}
    if user:
        booking_kwargs["user"] = user
    if date_created:
        booking_kwargs["dateCreated"] = date_created
    offer_kwargs = {}
    if product_subcategory_id:
        offer_kwargs = {"product__subcategoryId": product_subcategory_id}
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.ThingOfferFactory(**offer_kwargs),
    )
    return bookings_factories.BookingFactory(stock=stock, quantity=quantity, **booking_kwargs)


def create_digital_booking(quantity=1, price=10, user=None, product_subcategory_id=None):
    user = user or users_factories.BeneficiaryFactory()
    product_kwargs = {}
    if product_subcategory_id:
        product_kwargs = {"subcategoryId": product_subcategory_id}
    product = offers_factories.DigitalProductFactory(**product_kwargs)
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.ThingOfferFactory(product=product),
    )
    return bookings_factories.BookingFactory(user=user, stock=stock, quantity=quantity)


def create_event_booking(quantity=1, price=10, user=None, date_created=None):
    booking_kwargs = {}
    if user:
        booking_kwargs["user"] = user
    if date_created:
        booking_kwargs["dateCreated"] = date_created
    user = user or users_factories.BeneficiaryFactory()
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.EventOfferFactory(),
    )
    return bookings_factories.BookingFactory(stock=stock, quantity=quantity, **booking_kwargs)


def create_rich_user(total_deposit):
    # Some tests need to have a large amount of bookings. We could do
    # that by creating many bookings, or creating a very big booking
    # (that would exceed the usual 300/500 euros limitation). We do
    # the latter for simplicity's sake.
    user = users_factories.BeneficiaryFactory()
    user.deposit.amount = total_deposit
    repository.save(user.deposit)
    return user


@pytest.mark.usefixtures("db_session")
class DigitalThingsReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_digital_booking()

        # when
        reimbursed_amount = reimbursement.DigitalThingsReimbursement().apply(booking)

        # then
        assert reimbursed_amount == 0

    def test_relevant_for_booking_on_digital_things(self):
        # given
        booking = create_digital_booking()

        # when
        is_relevant = reimbursement.DigitalThingsReimbursement().is_relevant(booking)

        # then
        assert is_relevant

    def test_is_not_relevant_for_booking_on_physical_things(self):
        # given
        booking = create_non_digital_thing_booking()

        # when
        is_relevant = reimbursement.DigitalThingsReimbursement().is_relevant(booking)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_events(self):
        # given
        booking = create_event_booking()

        # when
        is_relevant = reimbursement.DigitalThingsReimbursement().is_relevant(booking)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_digital_books(self):
        # given
        booking = create_digital_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)

        # when
        is_relevant = reimbursement.DigitalThingsReimbursement().is_relevant(booking)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_cinema_cards(self):
        # given
        booking = create_digital_booking(product_subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)

        # when
        is_relevant = reimbursement.DigitalThingsReimbursement().is_relevant(booking)

        # then
        assert not is_relevant


@pytest.mark.usefixtures("db_session")
class PhysicalOffersReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_non_digital_thing_booking()

        # when
        reimbursed_amount = reimbursement.PhysicalOffersReimbursement().apply(booking)

        # then
        assert reimbursed_amount == booking.total_amount

    def test_is_relevant_for_booking_on_physical_things(self):
        # given
        booking = create_non_digital_thing_booking()

        # when
        is_relevant = reimbursement.PhysicalOffersReimbursement().is_relevant(booking)

        # then
        assert is_relevant

    def test_is_relevant_for_booking_on_events(self):
        # given
        booking = create_event_booking()

        # when
        is_relevant = reimbursement.PhysicalOffersReimbursement().is_relevant(booking)

        # then
        assert is_relevant

    def test_is_not_relevant_for_booking_on_digital_things(self):
        # given
        booking = create_digital_booking()

        # when
        is_relevant = reimbursement.PhysicalOffersReimbursement().is_relevant(booking)

        # then
        assert not is_relevant

    def test_is_relevant_for_booking_on_digital_books(self):
        # given
        booking = create_digital_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)

        # when
        is_relevant = reimbursement.PhysicalOffersReimbursement().is_relevant(booking)

        # then
        assert is_relevant

    def test_is_relevant_for_booking_on_cinema_cards(self):
        # given
        booking = create_digital_booking(product_subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)

        # when
        is_relevant = reimbursement.PhysicalOffersReimbursement().is_relevant(booking)

        # then
        assert is_relevant


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween20000And40000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_digital_booking(price=40, quantity=3)

        # when
        reimbursed_amount = reimbursement.ReimbursementRateByVenueBetween20000And40000().apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.95) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant

    def test_is_relevant_for_booking_on_events_with_cumulative_value_above_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_event_booking()
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_event_booking()
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_digital_things_with_cumulative_value_above_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_digital_booking()
        cumulative_booking_value = 20100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_below_20000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()
        booking = create_event_booking()
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween40000And150000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_digital_booking(price=40, quantity=3)

        # when
        reimbursed_amount = reimbursement.ReimbursementRateByVenueBetween40000And150000().apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.85) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_40000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween40000And150000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 40100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_40000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween40000And150000()
        booking = create_event_booking()
        cumulative_booking_value = 40000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_40000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueBetween40000And150000()
        booking = create_event_booking()
        cumulative_booking_value = 19000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueAbove150000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_digital_booking(price=40, quantity=3)

        # when
        reimbursed_amount = reimbursement.ReimbursementRateByVenueAbove150000().apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.7) * 40 * 3

    def test_is_relevant_for_booking_on_physical_things_with_cumulative_value_above_150000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueAbove150000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 150100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant

    def test_is_not_relevant_for_booking_on_events_with_cumulative_value_of_exactly_150000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueAbove150000()
        booking = create_event_booking()
        cumulative_booking_value = 150000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_physical_things_with_cumulative_value_below_150000(self):
        # given
        rule = reimbursement.ReimbursementRateByVenueAbove150000()
        booking = create_non_digital_thing_booking()
        cumulative_booking_value = 149000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant


@pytest.mark.usefixtures("db_session")
class ReimbursementRateForBookAbove20000Test:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_non_digital_thing_booking(
            product_subcategory_id=subcategories.LIVRE_PAPIER.id, price=40, quantity=3
        )

        # when
        reimbursed_amount = reimbursement.ReimbursementRateForBookAbove20000().apply(booking)

        # then
        assert reimbursed_amount == Decimal(0.95) * 40 * 3

    def test_is_relevant_for_booking_on_book_with_cumulative_value_below_20000(self):
        # given
        rule = reimbursement.ReimbursementRateForBookAbove20000()
        booking = create_non_digital_thing_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)
        cumulative_booking_value = 100

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_not_relevant_for_booking_on_book_with_cumulative_value_of_exactly_20000(self):
        # given
        rule = reimbursement.ReimbursementRateForBookAbove20000()
        booking = create_non_digital_thing_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)
        cumulative_booking_value = 20000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert not is_relevant

    def test_is_relevant_for_booking_on_book_with_cumulative_value_above_20000(self):
        # given
        rule = reimbursement.ReimbursementRateForBookAbove20000()
        booking = create_non_digital_thing_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)
        cumulative_booking_value = 55000

        # when
        is_relevant = rule.is_relevant(booking, cumulative_value=cumulative_booking_value)

        # then
        assert is_relevant


class ReimbursementRuleIsActiveTest:
    class DummyRule(reimbursement.ReimbursementRule):
        rate = Decimal(10)
        description = "Dummy rule"
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


@pytest.mark.usefixtures("db_session")
class FindAllBookingsReimbursementsTest:
    def test_returns_full_reimbursement_for_all_bookings(self):
        # given
        booking1 = create_event_booking()
        booking2 = create_non_digital_thing_booking()
        booking3 = create_non_digital_thing_booking()
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_total_reimbursement(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

    def test_returns_a_different_reimbursement_for_digital_booking(self):
        # given
        booking1 = create_event_booking()
        booking2 = create_digital_booking()
        booking3 = create_event_booking()
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

    def test_returns_full_reimbursement_when_cumulative_value_is_20000(self):
        # given
        booking1 = create_event_booking()
        booking2 = create_digital_booking()
        booking3 = create_non_digital_thing_booking()
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_total_reimbursement(booking_reimbursements[2], booking3)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

    def test_returns_95_reimbursement_rate_between_20000_and_40000_euros_for_most_recent_booking(self):
        # given
        user = create_rich_user(20000)
        booking1 = create_event_booking(user=user, price=19990)
        booking2 = create_digital_booking()
        booking3 = create_non_digital_thing_booking(price=20)
        bookings = [booking1, booking2, booking3]
        cumulative_value_for_bookings_1_and_3 = (
            booking1.amount * booking1.quantity + booking3.amount * booking3.quantity
        )

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_degressive_reimbursement(booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

    def test_returns_95_reimbursement_rate_between_20000_and_40000_when_cumulative_value_is_40000(self):
        # given
        user = create_rich_user(50000)
        booking1 = create_event_booking(user=user, price=19000)
        booking2 = create_digital_booking(price=50)
        booking3 = create_non_digital_thing_booking(user=user, price=19000)
        booking4 = create_non_digital_thing_booking(user=user, price=2000)
        bookings = [booking1, booking2, booking3, booking4]
        cumulative_value_for_bookings_1_and_3_and_4 = (
            booking1.amount * booking1.quantity
            + booking3.amount * booking3.quantity
            + booking4.amount * booking4.quantity
        )

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_degressive_reimbursement(
            booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3_and_4
        )
        assert_degressive_reimbursement(
            booking_reimbursements[3], booking4, cumulative_value_for_bookings_1_and_3_and_4
        )
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

    def test_returns_85_reimbursement_rate_between_40000_and_150000_euros_for_most_recent_booking(self):
        # given
        user = create_rich_user(50000)
        booking1 = create_event_booking(user=user, price=19000)
        booking2 = create_digital_booking(price=50, quantity=3)
        booking3 = create_non_digital_thing_booking(user=user, price=2000, quantity=12)
        bookings = [booking1, booking2, booking3]
        cumulative_value_for_bookings_1_and_3 = (
            booking1.amount * booking1.quantity + booking3.amount * booking3.quantity
        )

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_degressive_reimbursement(booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

    def test_returns_85_reimbursement_rate_between_40000_and_150000_when_cumulative_value_is_150000(self):
        # given
        user = create_rich_user(150000)
        booking1 = create_event_booking(user=user, price=19000)
        booking2 = create_digital_booking(price=50, quantity=3)
        booking3 = create_non_digital_thing_booking(user=user, price=19000, quantity=4)
        booking4 = create_non_digital_thing_booking(user=user, price=5000)
        bookings = [booking1, booking2, booking3, booking4]
        cumulative_value_for_bookings_1_and_3_and_4 = (
            booking1.amount * booking1.quantity
            + booking3.amount * booking3.quantity
            + booking4.amount * booking4.quantity
        )

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)
        assert_degressive_reimbursement(
            booking_reimbursements[2], booking3, cumulative_value_for_bookings_1_and_3_and_4
        )
        assert_degressive_reimbursement(
            booking_reimbursements[3], booking4, cumulative_value_for_bookings_1_and_3_and_4
        )

    def test_returns_65_reimbursement_rate_above_150000_euros_for_last_booking(self):
        # given
        user = create_rich_user(300000)
        booking1 = create_event_booking(user=user, price=19000)
        booking2 = create_digital_booking(price=50, quantity=3)
        booking3 = create_non_digital_thing_booking(user=user, price=2000, quantity=120)
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_degressive_reimbursement(booking_reimbursements[2], booking3, 430000)
        assert_no_reimbursement_for_digital(booking_reimbursements[1], booking2)

    def test_returns_full_reimbursement_for_all_bookings_for_new_civil_year(self):
        # given
        user = create_rich_user(30000)
        booking1 = create_event_booking(user=user, price=10000, date_created=datetime(2018, 1, 1))
        booking2 = create_non_digital_thing_booking(user=user, price=10000, date_created=datetime(2018, 1, 1))
        booking3 = create_event_booking(user=user, price=200, quantity=2, date_created=datetime(2019, 1, 1))
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_total_reimbursement(booking_reimbursements[1], booking2)
        assert_total_reimbursement(booking_reimbursements[2], booking3)

    def test_returns_85_reimbursement_rate_between_20000_and_40000_euros_for_this_civil_year(self):
        # given
        user = create_rich_user(50000)
        booking1 = create_event_booking(user=user, price=20000, date_created=datetime(2018, 1, 1))
        booking2 = create_non_digital_thing_booking(user=user, price=25000, date_created=datetime(2019, 1, 1))
        booking3 = create_non_digital_thing_booking(user=user, price=2000, date_created=datetime(2019, 1, 1))
        bookings = [booking1, booking2, booking3]

        # when
        booking_reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules=[])

        # then
        assert_total_reimbursement(booking_reimbursements[0], booking1)
        assert_degressive_reimbursement(booking_reimbursements[1], booking2, 25000)
        assert_degressive_reimbursement(booking_reimbursements[2], booking3, 27000)

    @pytest.mark.usefixtures("db_session")
    def test_select_custom_reimbursement_rule_if_applicable(self):
        offer1 = offers_factories.DigitalOfferFactory()
        booking1 = bookings_factories.BookingFactory(stock__offer=offer1)
        offer2 = offers_factories.DigitalOfferFactory()
        booking2 = bookings_factories.BookingFactory(stock__offer=offer2)
        rule1 = payments_factories.CustomReimbursementRuleFactory(offer=offer1, amount=5)
        rule2 = payments_factories.CustomReimbursementRuleFactory(
            offer=offer2, timespan=[booking2.dateCreated + timedelta(days=2), None]
        )
        print(rule2)

        bookings = [booking1, booking2]
        custom_rules = payments_models.CustomReimbursementRule.query.all()
        reimbursements = reimbursement.find_all_booking_reimbursements(bookings, custom_rules)

        assert reimbursements[0].booking == booking1
        assert reimbursements[0].rule == rule1
        assert reimbursements[0].reimbursed_amount == 5
        assert_no_reimbursement_for_digital(reimbursements[1], booking2)


def assert_total_reimbursement(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert isinstance(booking_reimbursement.rule, reimbursement.PhysicalOffersReimbursement)
    assert booking_reimbursement.reimbursed_amount == booking.total_amount


def assert_no_reimbursement_for_digital(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert isinstance(booking_reimbursement.rule, reimbursement.DigitalThingsReimbursement)
    assert booking_reimbursement.reimbursed_amount == 0


def assert_degressive_reimbursement(booking_reimbursement, booking, total_amount):
    assert booking_reimbursement.booking == booking
    if 20000 < total_amount <= 40000:
        assert isinstance(booking_reimbursement.rule, reimbursement.ReimbursementRateByVenueBetween20000And40000)
        assert (
            booking_reimbursement.reimbursed_amount
            == reimbursement.ReimbursementRateByVenueBetween20000And40000().rate * booking.total_amount
        )
    elif 40000 < total_amount <= 150000:
        assert isinstance(booking_reimbursement.rule, reimbursement.ReimbursementRateByVenueBetween40000And150000)
        assert (
            booking_reimbursement.reimbursed_amount
            == reimbursement.ReimbursementRateByVenueBetween40000And150000().rate * booking.total_amount
        )
    elif total_amount > 150000:
        assert isinstance(booking_reimbursement.rule, reimbursement.ReimbursementRateByVenueAbove150000)
        assert (
            booking_reimbursement.reimbursed_amount
            == reimbursement.ReimbursementRateByVenueAbove150000().rate * booking.total_amount
        )
    else:
        assert False
