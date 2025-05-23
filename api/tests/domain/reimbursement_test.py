from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.domain import reimbursement


def create_non_digital_thing_booking(quantity=1, price=10, user=None, date_used=None, subcategory_id=None):
    booking_kwargs = {}
    if user:
        booking_kwargs["user"] = user
    booking_kwargs["dateUsed"] = date_used or datetime.utcnow()
    offer_kwargs = {}
    if subcategory_id:
        offer_kwargs = {"subcategoryId": subcategory_id}
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.ThingOfferFactory(**offer_kwargs),
    )
    return bookings_factories.UsedBookingFactory(stock=stock, quantity=quantity, **booking_kwargs)


def create_digital_booking(quantity=1, price=10, user=None, subcategory_id=None):
    user = user or users_factories.BeneficiaryGrant18Factory()
    subcategory_kwargs = {}
    if subcategory_id:
        subcategory_kwargs = {"subcategoryId": subcategory_id}
    stock = offers_factories.StockFactory(
        price=price,
        offer=offers_factories.DigitalOfferFactory(**subcategory_kwargs),
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

        assert rule.is_relevant(create_digital_booking(), cumulative_revenue=0)
        digital_book_booking = create_digital_booking(subcategory_id=subcategories.LIVRE_PAPIER.id)
        assert not rule.is_relevant(digital_book_booking, cumulative_revenue=0)
        cinema_card_booking = create_digital_booking(subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)
        assert not rule.is_relevant(cinema_card_booking, cumulative_revenue=0)
        assert not rule.is_relevant(create_non_digital_thing_booking(), cumulative_revenue=0)
        assert not rule.is_relevant(create_event_booking(), cumulative_revenue=0)


@pytest.mark.usefixtures("db_session")
class EducationalOffersReimbursementTest:
    def test_apply(self):
        booking = educational_factories.CollectiveBookingFactory(collectiveStock__price=1234)
        rule = reimbursement.EducationalOffersReimbursement()
        assert rule.apply(booking) == 123400  # eurocents

    def test_relevancy(self):
        rule = reimbursement.EducationalOffersReimbursement()
        collective_booking = educational_factories.CollectiveBookingFactory()
        individual_booking = bookings_factories.BookingFactory()

        assert rule.is_relevant(collective_booking, cumulative_revenue=0)
        assert not rule.is_relevant(individual_booking, cumulative_revenue=0)


@pytest.mark.usefixtures("db_session")
class PhysicalOffersReimbursementTest:
    def test_apply(self):
        booking = create_non_digital_thing_booking(price=10, quantity=2)
        rule = reimbursement.PhysicalOffersReimbursement()
        assert rule.apply(booking) == 2000  # eurocents

    def test_relevancy(self):
        rule = reimbursement.PhysicalOffersReimbursement()

        assert rule.is_relevant(create_non_digital_thing_booking(), cumulative_revenue=0)
        assert rule.is_relevant(create_event_booking(), cumulative_revenue=0)
        assert not rule.is_relevant(create_digital_booking(), cumulative_revenue=0)
        digital_book_booking = create_digital_booking(subcategory_id=subcategories.LIVRE_NUMERIQUE.id)
        assert not rule.is_relevant(digital_book_booking, cumulative_revenue=0)
        cinema_card_booking = create_digital_booking(subcategory_id=subcategories.CINE_VENTE_DISTANCE.id)
        assert rule.is_relevant(cinema_card_booking, cumulative_revenue=0)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000Test:
    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueBetween20000And40000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 7600  # 0.95 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 20_000 * 100)
        assert self.rule.is_relevant(booking, 20_001 * 100)
        assert self.rule.is_relevant(booking, 40_000 * 100)
        assert not self.rule.is_relevant(booking, 40_001 * 100)

    def test_relevancy_depending_on_offer_subcategory(self):
        revenue = 20_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000Test:
    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueBetween40000And150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 6800  # 0.85 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 40_000 * 100)
        assert self.rule.is_relevant(booking, 40_001 * 100)
        assert self.rule.is_relevant(booking, 150_000 * 100)
        assert not self.rule.is_relevant(booking, 150_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 40_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class LegacyPreSeptember2021ReimbursementRateByVenueAbove150000Test:
    rule = reimbursement.LegacyPreSeptember2021ReimbursementRateByVenueAbove150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 5600  # 0.7 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 150_000 * 100)
        assert self.rule.is_relevant(booking, 150_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 150_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween20000And40000Test:
    rule = reimbursement.ReimbursementRateByVenueBetween20000And40000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 7600  # 0.95 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 20_000 * 100)
        assert self.rule.is_relevant(booking, 20_001 * 100)
        assert self.rule.is_relevant(booking, 40_000 * 100)
        assert not self.rule.is_relevant(booking, 40001)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueBetween40000And150000Test:
    rule = reimbursement.ReimbursementRateByVenueBetween40000And150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 7360  # 0.92 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 40_000 * 100)
        assert self.rule.is_relevant(booking, 40_001 * 100)
        assert self.rule.is_relevant(booking, 150_000 * 100)
        assert not self.rule.is_relevant(booking, 150_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 40_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateByVenueAbove150000Test:
    rule = reimbursement.ReimbursementRateByVenueAbove150000()

    def test_apply(self):
        booking = create_event_booking(price=40, quantity=2)
        assert self.rule.apply(booking) == 7200  # 0.90 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        booking = create_event_booking()

        assert not self.rule.is_relevant(booking, 150_000 * 100)
        assert self.rule.is_relevant(booking, 150_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 150_001 * 100
        assert self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateForBookBelow20000Test:
    rule = reimbursement.ReimbursementRateForBookBelow20000()

    @property
    def book_booking(self):
        return create_non_digital_thing_booking(subcategory_id=subcategories.LIVRE_PAPIER.id, price=40, quantity=2)

    def test_apply(self):
        assert self.rule.apply(self.book_booking) == 8000  # 1 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        assert self.rule.is_relevant(self.book_booking, 20_000)
        assert not self.rule.is_relevant(self.book_booking, 20_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20_000 * 100
        assert self.rule.is_relevant(self.book_booking, revenue)
        assert not self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert not self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)
        assert self.rule.is_relevant(create_digital_booking(subcategory_id=subcategories.LIVRE_NUMERIQUE.id), revenue)


@pytest.mark.usefixtures("db_session")
class ReimbursementRateForBookAbove20000Test:
    rule = reimbursement.ReimbursementRateForBookAbove20000()

    @property
    def book_booking(self):
        return create_non_digital_thing_booking(subcategory_id=subcategories.LIVRE_PAPIER.id, price=40, quantity=2)

    def test_apply(self):
        assert self.rule.apply(self.book_booking) == 7600  # 0.95 * 40 * 2 * 100 (eurocents)

    def test_relevancy_depending_on_revenue(self):
        assert not self.rule.is_relevant(self.book_booking, 20_000 * 100)
        assert self.rule.is_relevant(self.book_booking, 20_001 * 100)

    def test_relevancy_depending_on_offer_type(self):
        revenue = 20_001 * 100
        assert self.rule.is_relevant(self.book_booking, revenue)
        assert not self.rule.is_relevant(create_non_digital_thing_booking(), revenue)
        assert not self.rule.is_relevant(create_event_booking(), revenue)
        assert not self.rule.is_relevant(create_digital_booking(), revenue)
        assert self.rule.is_relevant(create_digital_booking(subcategory_id=subcategories.LIVRE_NUMERIQUE.id), revenue)


class ReimbursementRuleIsActiveTest:
    class DummyRule(finance_models.ReimbursementRule):
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
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        offer = booking.stock.offer
        old_booking = bookings_factories.UsedBookingFactory(stock=booking.stock, dateUsed=far_in_the_past)
        unrelated_booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        rule = finance_factories.CustomReimbursementRuleFactory(offer=offer, timespan=(yesterday, None))
        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(booking) == rule
        assert finder.get_rule(old_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(unrelated_booking) is None  # no rule for this bookings's offer

    def test_venue_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        pricing_point = offerers_factories.VenueFactory(pricing_point="self")
        linked_venue = offerers_factories.VenueFactory(pricing_point=pricing_point)

        pricing_point_booking = bookings_factories.UsedBookingFactory(stock__offer__venue=pricing_point)
        related_booking = bookings_factories.UsedBookingFactory(stock__offer__venue=linked_venue)
        old_booking = bookings_factories.UsedBookingFactory(stock=pricing_point_booking.stock, dateUsed=far_in_the_past)
        unrelated_booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        rule = finance_factories.CustomReimbursementRuleFactory(venue=pricing_point, timespan=(yesterday, None))

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(pricing_point_booking) == rule
        assert finder.get_rule(related_booking) == rule
        assert finder.get_rule(old_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(unrelated_booking) is None  # no rule for this bookings's venue

    def test_offerer_without_category_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        offerer = booking.offerer
        old_booking = bookings_factories.UsedBookingFactory(
            offerer=offerer, stock__offer__venue__pricing_point=booking.venue, dateUsed=far_in_the_past
        )
        unrelated_booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        rule = finance_factories.CustomReimbursementRuleFactory(offerer=offerer, timespan=(yesterday, None))

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(booking) == rule
        assert finder.get_rule(old_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(unrelated_booking) is None  # no rule for this bookings's offerer

    def test_offerer_with_category_rule(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        offerer_booking = bookings_factories.UsedBookingFactory(
            stock__offer__subcategoryId=subcategories.FESTIVAL_CINE.id, stock__offer__venue__pricing_point="self"
        )
        offerer = offerer_booking.offerer
        other_subcategory_booking = bookings_factories.UsedBookingFactory(
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__venue__managingOfferer=offerer,
            stock__offer__venue=offerer_booking.venue,
        )
        old_booking = bookings_factories.UsedBookingFactory(
            offerer=offerer,
            stock__offer__venue=offerer_booking.venue,
            stock__offer__subcategoryId=subcategories.FESTIVAL_CINE.id,
            dateUsed=far_in_the_past,
        )
        unrelated_booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")
        rule = finance_factories.CustomReimbursementRuleFactory(
            offerer=offerer, subcategories=[subcategories.FESTIVAL_CINE.id], timespan=(yesterday, None)
        )

        finder = reimbursement.CustomRuleFinder()
        assert finder.get_rule(offerer_booking) == rule
        assert finder.get_rule(other_subcategory_booking) is None  # wrong category
        assert finder.get_rule(old_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(unrelated_booking) is None  # no rule for this bookings's offerer

    def test_rule_priorities(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        far_in_the_past = datetime.utcnow() - timedelta(days=800)
        pricing_point = offerers_factories.VenueFactory(pricing_point="self")
        offerer = pricing_point.managingOfferer
        yesterday_booking = bookings_factories.UsedBookingFactory(stock__offer__venue=pricing_point)
        ancient_booking = bookings_factories.UsedBookingFactory(stock=yesterday_booking.stock, dateUsed=far_in_the_past)
        another_booking = bookings_factories.UsedBookingFactory(stock__offer__venue__pricing_point="self")

        venue_rule = finance_factories.CustomReimbursementRuleFactory(venue=pricing_point, timespan=(yesterday, None))
        _offerer_rule = finance_factories.CustomReimbursementRuleFactory(offerer=offerer, timespan=(yesterday, None))

        finder = reimbursement.CustomRuleFinder()

        # Custom rule on Venue has priority over rule on Offerer
        assert finder.get_rule(yesterday_booking) == venue_rule
        assert finder.get_rule(ancient_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(another_booking) is None  # no rule for this venue

        offer_rule = finance_factories.CustomReimbursementRuleFactory(
            offer=yesterday_booking.stock.offer, timespan=(yesterday, None)
        )

        finder = reimbursement.CustomRuleFinder()

        # Custom rule on Offer has priority over rule on Venue and Offerer
        assert finder.get_rule(yesterday_booking) == offer_rule
        assert finder.get_rule(ancient_booking) is None  # outside `rule.timespan`
        assert finder.get_rule(another_booking) is None  # no rule for this offer


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
