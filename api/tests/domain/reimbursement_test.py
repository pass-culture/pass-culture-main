from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.payments.models as payments_models
import pcapi.core.users.factories as users_factories
from pcapi.domain import reimbursement


def create_non_digital_thing_booking(quantity=1, price=10, user=None, date_used=None, product_subcategory_id=None):
    booking_kwargs = {}
    if user:
        booking_kwargs["user"] = user
    booking_kwargs["dateUsed"] = date_used or datetime.utcnow()
    offer_kwargs = {}
    if product_subcategory_id:
        offer_kwargs = {"product__subcategoryId": product_subcategory_id}
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.ThingOfferFactory(**offer_kwargs),
    )
    return bookings_factories.UsedBookingFactory(stock=stock, quantity=quantity, **booking_kwargs)


def create_digital_booking(quantity=1, price=10, user=None, product_subcategory_id=None):
    user = user or users_factories.BeneficiaryGrant18Factory()
    product_kwargs = {}
    if product_subcategory_id:
        product_kwargs = {"subcategoryId": product_subcategory_id}
    product = offers_factories.DigitalProductFactory(**product_kwargs)
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.ThingOfferFactory(product=product),
    )
    return bookings_factories.UsedBookingFactory(user=user, stock=stock, quantity=quantity, dateUsed=datetime.utcnow())


def create_event_booking(quantity=1, price=10, user=None, date_used=None):
    booking_kwargs = {}
    if user:
        booking_kwargs["user"] = user
    booking_kwargs["dateUsed"] = date_used or datetime.utcnow()
    user = user or users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.EventOfferFactory(),
    )
    return bookings_factories.UsedBookingFactory(stock=stock, quantity=quantity, **booking_kwargs)


@pytest.mark.usefixtures("db_session")
class DigitalThingsReimbursementTest:
    def test_apply(self):
        booking = create_digital_booking()
        rule = reimbursement.DigitalThingsReimbursement()
        assert rule.apply(booking) == 0

    def test_relevancy(self):
        rule = reimbursement.DigitalThingsReimbursement()

        assert rule.is_relevant(create_digital_booking())
        digital_book_booking = create_digital_booking(product_subcategory_id=subcategories.LIVRE_PAPIER.id)
        assert not rule.is_relevant(digital_book_booking)
        cinema_card_booking = create_digital_booking(product_subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)
        assert not rule.is_relevant(cinema_card_booking)
        assert not rule.is_relevant(create_non_digital_thing_booking())
        assert not rule.is_relevant(create_event_booking())


@pytest.mark.usefixtures("db_session")
class EducationalOffersReimbursement:
    def test_apply(self):
        booking = educational_factories.CollectiveBookingFactory(amount=3000, quantity=2)
        rule = reimbursement.EducationalOffersReimbursement()
        assert rule.apply(booking) == booking.collectiveStock.price

    def test_relevancy(self):
        rule = reimbursement.EducationalOffersReimbursement()

        assert rule.is_relevant(educational_factories.CollectiveBookingFactory)
        assert not rule.is_relevant(bookings_factories.BookingFactory())


@pytest.mark.usefixtures("db_session")
class PhysicalOffersReimbursementTest:
    def test_apply(self):
        booking = create_non_digital_thing_booking(price=10, quantity=2)
        rule = reimbursement.PhysicalOffersReimbursement()
        assert rule.apply(booking) == 10 * 2

    def test_relevancy(self):
        rule = reimbursement.PhysicalOffersReimbursement()

        assert rule.is_relevant(create_non_digital_thing_booking())
        assert rule.is_relevant(create_event_booking())
        assert not rule.is_relevant(create_digital_booking())
        digital_book_booking = create_digital_booking(product_subcategory_id=subcategories.LIVRE_NUMERIQUE.id)
        assert not rule.is_relevant(digital_book_booking)
        cinema_card_booking = create_digital_booking(product_subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)
        assert rule.is_relevant(cinema_card_booking)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000Test:

    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.95") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 20000)
        assert self.rule.is_relevant(booking, 20001)
        assert self.rule.is_relevant(booking, 40000)
        assert not self.rule.is_relevant(booking, 40001)

    def test_relevancy_depending_on_offer_subcategory(self):
        revenue = 20001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000Test:
    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.85") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 40000)
        assert self.rule.is_relevant(booking, 40001)
        assert self.rule.is_relevant(booking, 150000)
        assert not self.rule.is_relevant(booking, 150001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 40001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueAbove150000Test:
    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueAbove150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.7") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 150000)
        assert self.rule.is_relevant(booking, 150001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 150001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween20000And40000Test:

    rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.95") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 20000)
        assert self.rule.is_relevant(booking, 20001)
        assert self.rule.is_relevant(booking, 40000)
        assert not self.rule.is_relevant(booking, 40001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween40000And150000Test:
    rule = reimbursement.ReimbursementRateByVenueBetween40000And150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.92") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 40000)
        assert self.rule.is_relevant(booking, 40001)
        assert self.rule.is_relevant(booking, 150000)
        assert not self.rule.is_relevant(booking, 150001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 40001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueAbove150000Test:
    rule = reimbursement.ReimbursementRateByVenueAbove150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == Decimal("0.90") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 150000)
        assert self.rule.is_relevant(booking, 150001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 150001
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateForBookBelow20000Test:
    rule = reimbursement.ReimbursementRateForBookBelow20000()

    @property
    def book_booking(self):
        return create_non_digital_thing_booking(
            product_subcategory_id=subcategories.LIVRE_PAPIER.id, price=40, quantity=2
        )

    def test_apply(self):
        assert self.rule.apply(self.book_booking) == Decimal(1) * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        assert self.rule.is_relevant(self.book_booking, 20000)
        assert not self.rule.is_relevant(self.book_booking, 20001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20000
        assert self.rule.is_relevant(self.book_booking, revenue)
        assert not self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert not self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)
        assert self.rule.is_relevant(
            create_digital_booking(product_subcategory_id=subcategories.LIVRE_NUMERIQUE.id), revenue
        )


@pytest.mark.usefixtures("db_session")
class ReimbursementRateForBookAbove20000Test:
    rule = reimbursement.ReimbursementRateForBookAbove20000()

    @property
    def book_booking(self):
        return create_non_digital_thing_booking(
            product_subcategory_id=subcategories.LIVRE_PAPIER.id, price=40, quantity=2
        )

    def test_apply(self):
        assert self.rule.apply(self.book_booking) == Decimal("0.95") * 40 * 2

    def test_relevancy_depending_on_revenue(self):
        assert not self.rule.is_relevant(self.book_booking, 20000)
        assert self.rule.is_relevant(self.book_booking, 20001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20001
        assert self.rule.is_relevant(self.book_booking, revenue)
        assert not self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert not self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)
        assert self.rule.is_relevant(
            create_digital_booking(product_subcategory_id=subcategories.LIVRE_NUMERIQUE.id), revenue
        )


class ReimbursementRuleIsActiveTest:
    class DummyRule(payments_models.ReimbursementRule):
        rate = Decimal(10)
        description = "Dummy rule"

        def __init__(self, valid_from=None, valid_until=None):
            self.valid_from = valid_from
            self.valid_until = valid_until

        def is_relevant(self, booking, cumulative_revenue):
            return True

        @property
        def group(self):
            return None

    booking = Booking(dateCreated=datetime.utcnow() + timedelta(days=365), dateUsed=datetime.utcnow())

    def test_is_active_if_rule_has_no_start_nor_end(self):
        rule = self.DummyRule(None, None)
        assert rule.is_active(self.booking)

    def test_is_active_if_valid_since_yesterday_without_end_date(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        rule = self.DummyRule(valid_from=yesterday)
        assert rule.is_active(self.booking)

    def test_is_active_if_valid_since_yesterday_with_end_date(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        rule = self.DummyRule(valid_from=yesterday, valid_until=tomorrow)
        assert rule.is_active(self.booking)

    def test_is_not_active_if_not_yet_valid_without_end_date(self):
        future = datetime.utcnow() + timedelta(weeks=3)
        rule = self.DummyRule(valid_from=future)
        assert not rule.is_active(self.booking)

    def test_is_not_active_if_not_yet_valid_with_end_date(self):
        future = datetime.utcnow() + timedelta(weeks=3)
        far_future = datetime.utcnow() + timedelta(weeks=5)
        rule = self.DummyRule(valid_from=future, valid_until=far_future)
        assert not rule.is_active(self.booking)

    def test_is_active_if_no_start_date_and_until_later(self):
        future = datetime.utcnow() + timedelta(weeks=3)
        rule = self.DummyRule(valid_until=future)
        assert rule.is_active(self.booking)

    def test_is_not_active_if_rule_is_not_valid_anymore_with_no_start_date(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        rule = self.DummyRule(valid_until=yesterday)
        assert not rule.is_active(self.booking)

    def test_is_not_active_if_rule_is_not_valid_anymore_with_start_date(self):
        a_month_ago = datetime.utcnow() - timedelta(days=30)
        yesterday = datetime.utcnow() - timedelta(days=1)
        rule = self.DummyRule(valid_from=a_month_ago, valid_until=yesterday)
        assert not rule.is_active(self.booking)


@pytest.mark.usefixtures("db_session")
class CustomRuleFinderTest:
    def test_offer_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        booking1 = bookings_factories.UsedBookingFactory()
        offer = booking1.stock.offer
        booking2 = bookings_factories.UsedBookingFactory(stock=booking1.stock, dateUsed=far_in_the_past)
        booking3 = bookings_factories.UsedBookingFactory()
        rule = payments_factories.CustomReimbursementRuleFactory(offer=offer, timespan=(yesterday, None))

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(booking1) == rule
        assert finder.get_rule(booking2) is None  # outside `rule.timespan`
        assert finder.get_rule(booking3) is None  # no rule for this offer

    def test_offerer_without_category_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        booking1 = bookings_factories.UsedBookingFactory()
        offerer = booking1.offerer
        booking2 = bookings_factories.UsedBookingFactory(offerer=offerer, dateUsed=far_in_the_past)
        booking3 = bookings_factories.UsedBookingFactory()
        rule = payments_factories.CustomReimbursementRuleFactory(offerer=offerer, timespan=(yesterday, None))

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(booking1) == rule
        assert finder.get_rule(booking2) is None  # outside `rule.timespan`
        assert finder.get_rule(booking3) is None  # no rule for this offerer

    def test_offerer_with_category_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        booking1 = bookings_factories.UsedBookingFactory(stock__offer__subcategoryId=subcategories.FESTIVAL_CINE.id)
        offerer = booking1.offerer
        booking2 = bookings_factories.UsedBookingFactory(
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id, stock__offer__venue__managingOfferer=offerer
        )
        booking3 = bookings_factories.UsedBookingFactory(
            offerer=offerer, stock__offer__subcategoryId=subcategories.FESTIVAL_CINE.id, dateUsed=far_in_the_past
        )
        booking4 = bookings_factories.UsedBookingFactory()
        rule = payments_factories.CustomReimbursementRuleFactory(
            offerer=offerer, subcategories=[subcategories.FESTIVAL_CINE.id], timespan=(yesterday, None)
        )

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(booking1) == rule
        assert finder.get_rule(booking2) is None  # wrong category
        assert finder.get_rule(booking3) is None  # outside `rule.timespan`
        assert finder.get_rule(booking4) is None  # no rule for this offerer


def assert_total_reimbursement(booking_reimbursement, rule, booking):
    assert booking_reimbursement.booking == booking
    assert isinstance(booking_reimbursement.rule, rule)
    assert booking_reimbursement.reimbursed_amount == booking.total_amount


def assert_no_reimbursement_for_digital(booking_reimbursement, booking):
    assert booking_reimbursement.booking == booking
    assert isinstance(booking_reimbursement.rule, reimbursement.DigitalThingsReimbursement)
    assert booking_reimbursement.reimbursed_amount == 0


def assert_partial_reimbursement(booking_reimbursement, booking, rule, amount):
    assert booking_reimbursement.booking == booking
    assert isinstance(booking_reimbursement.rule, rule)
    assert booking_reimbursement.reimbursed_amount == amount
    assert booking_reimbursement.reimbursed_amount < booking.amount
