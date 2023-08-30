import dataclasses
import datetime
from decimal import Decimal

import pytest
import pytz

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import factories
from pcapi.core.finance import models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.repository import repository
import pcapi.utils.db as db_utils



class CustomReimbursementRuleTest:
    @dataclasses.dataclass
    class DummyBooking:
        dateUsed: datetime.datetime

    def test_timespan_setter(self):
        # Test the model, not the factory.
        start = datetime.datetime(2021, 1, 12, 0, 0)
        offer = offers_factories.OfferFactory()
        rule = models.CustomReimbursementRule(timespan=(start, None), amount=1, offer=offer)
        repository.save(rule)
        db.session.refresh(rule)

        # Test without upper bound
        assert rule.timespan.lower == start
        assert rule.timespan.upper is None
        assert rule.timespan.lower_inc
        assert not rule.timespan.upper_inc

        # Test with upper bound
        end = datetime.datetime(2021, 5, 12, 0, 0)
        rule.timespan = db_utils.make_timerange(start, end)
        repository.save(rule)
        db.session.refresh(rule)
        assert rule.timespan.lower == start
        assert rule.timespan.upper == end
        assert rule.timespan.lower_inc
        assert not rule.timespan.upper_inc

    def test_timespan_setter_with_timezone(self):
        offer = offers_factories.OfferFactory()
        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime.datetime(2021, 1, 12, 0, 0))
        rule = models.CustomReimbursementRule(timespan=(start, None), amount=1, offer=offer)
        repository.save(rule)
        db.session.refresh(rule)
        assert rule.timespan.lower == datetime.datetime(2021, 1, 11, 23, 0)

    def test_is_active(self):
        start = datetime.datetime(2021, 1, 12, 0, 0)
        rule = factories.CustomReimbursementRuleFactory(timespan=(start, None))

        # Test without upper bound
        assert rule.is_active(self.DummyBooking(start))
        assert rule.is_active(self.DummyBooking(start + datetime.timedelta(seconds=2)))
        assert not rule.is_active(self.DummyBooking(start - datetime.timedelta(seconds=2)))

        # Test with upper bound
        end = datetime.datetime(2021, 5, 12, 0, 0)
        rule = factories.CustomReimbursementRuleFactory(timespan=(start, end))
        assert rule.is_active(self.DummyBooking(start + datetime.timedelta(seconds=2)))
        assert not rule.is_active(self.DummyBooking(start - datetime.timedelta(seconds=2)))
        assert rule.is_active(self.DummyBooking(end - datetime.timedelta(seconds=2)))
        assert not rule.is_active(self.DummyBooking(end))
        assert not rule.is_active(self.DummyBooking(end + datetime.timedelta(seconds=2)))

    def test_is_relevant(self):
        offer1 = offers_factories.OfferFactory()
        booking1 = bookings_factories.BookingFactory(stock__offer=offer1)
        rule = factories.CustomReimbursementRuleFactory(offer=offer1)
        assert rule.is_relevant(booking1)

        booking2 = bookings_factories.BookingFactory()
        assert not rule.is_relevant(booking2)

    def test_apply_with_amount(self):
        rule = factories.CustomReimbursementRuleFactory(amount=10)
        single = bookings_factories.BookingFactory(quantity=1)
        double = bookings_factories.BookingFactory(quantity=2)

        assert rule.apply(single) == 10
        assert rule.apply(double) == 20

    def test_apply_with_rate(self):
        rule = factories.CustomReimbursementRuleFactory(rate=0.8)
        single = bookings_factories.BookingFactory(quantity=1)
        double = bookings_factories.BookingFactory(quantity=2)

        assert rule.apply(single) == Decimal("8.08")
        assert rule.apply(double) == Decimal("16.16")


class DepositSpecificCapsTest:
    def should_not_have_digital_cap_if_from_wallis_and_futuna(self):
        user = users_factories.BeneficiaryGrant18Factory(departementCode=986)
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP is None

    def should_have_no_specific_cap_if_underage(self):
        user = users_factories.UnderageBeneficiaryFactory()
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP is None
        assert specific_caps.PHYSICAL_CAP is None

    def should_have_digital_cap_if_grant_18_v2(self):
        user = users_factories.BeneficiaryGrant18Factory()
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP == Decimal(100)
        assert specific_caps.PHYSICAL_CAP is None

    def should_have_both_caps_when_18_v1(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP == Decimal(200)
        assert specific_caps.PHYSICAL_CAP == Decimal(200)

    def should_have_150_euros_cap_when_from_mayotte(self):
        user = users_factories.BeneficiaryGrant18Factory(departementCode=976)
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP == Decimal(150)
        assert specific_caps.PHYSICAL_CAP is None

    def should_have_200_euros_cap_when_from_saint_pierre_et_miquelon(self):
        user = users_factories.BeneficiaryGrant18Factory(departementCode=975)
        specific_caps = user.deposit.specific_caps

        assert specific_caps.DIGITAL_CAP == Decimal(200)
        assert specific_caps.PHYSICAL_CAP is None
