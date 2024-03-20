import csv
import datetime
from decimal import Decimal
import io
import logging
import pathlib
from unittest import mock
import zipfile

from dateutil.relativedelta import relativedelta
import pytest
import pytz
import time_machine

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import Ministry
from pcapi.core.educational.validation import check_institution_fund
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import utils
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.object_storage.testing import recursive_listdir
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import clean_temporary_files
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.utils import human_ids
import pcapi.utils.db as db_utils

import tests


pytestmark = pytest.mark.usefixtures("db_session")


def create_booking_with_undeletable_dependent(date_used=None, **kwargs):
    if not date_used:
        date_used = datetime.datetime.utcnow()
    booking = bookings_factories.UsedBookingFactory(dateUsed=date_used, **kwargs)
    factories.PricingFactory(
        booking__stock__offer__venue=booking.venue,
        valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        status=models.PricingStatus.PROCESSED,
    )
    return booking


def datetime_iterator(first):
    dt = first
    while 1:
        yield dt
        dt += datetime.timedelta(days=15)


class CleanStringTest:
    def test_remove_string_starting_with_space_if_string(self):
        name = " saut de ligne"
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne"

    def test_remove_doublequote_if_string(self):
        name = 'saut de ligne "spécial"\n'
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne spécial"

    def test_remove_new_line_if_string(self):
        name = "saut de ligne\n"
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne"

    def test_remove_new_line_within_string(self):
        name = "saut \n de ligne"
        result = api._clean_for_accounting(name)
        assert result == "saut  de ligne"

    def test_remove_semicolon_within_string(self):
        name = "point-virgule ; au milieu ; de la ligne"
        result = api._clean_for_accounting(name)
        assert result == "point-virgule  au milieu  de la ligne"

    def test_return_value_sent_if_not_string(self):
        number = 1
        result = api._clean_for_accounting(number)
        assert result == 1


def individual_stock_factory(**kwargs):
    create_bank_info = False
    if "offer__venue" not in kwargs:
        kwargs.setdefault("offer__venue__pricing_point", "self")
        kwargs.setdefault("offer__venue__reimbursement_point", "self")
        create_bank_info = True
    stock = offers_factories.ThingStockFactory(**kwargs)
    if create_bank_info:
        factories.BankInformationFactory(venue=stock.offer.venue)
    return stock


def collective_stock_factory(**kwargs):
    create_bank_info = False
    if "offer__venue" not in kwargs:
        kwargs.setdefault("collectiveOffer__venue__pricing_point", "self")
        kwargs.setdefault("collectiveOffer__venue__reimbursement_point", "self")
        create_bank_info = True
    stock = educational_factories.CollectiveStockFactory(**kwargs)
    if create_bank_info:
        factories.BankInformationFactory(venue=stock.collectiveOffer.venue)
    return stock


class PriceEventTest:
    def _make_individual_event(self, used_date=None, price=None, user=None, stock=None, venue=None):
        booking_kwargs = {}
        if user:
            booking_kwargs["user"] = user
        if stock:
            booking_kwargs["stock"] = stock
        else:
            stock_kwargs = {}
            if price is not None:
                stock_kwargs["price"] = price
            if venue:
                stock_kwargs["offer__venue"] = venue
            booking_kwargs["stock"] = individual_stock_factory(**stock_kwargs)
        booking = bookings_factories.BookingFactory(**booking_kwargs)
        with time_machine.travel(used_date or datetime.datetime.utcnow()):
            bookings_api.mark_as_used(booking)
        return models.FinanceEvent.query.filter_by(booking=booking).one()

    def _make_collective_event(self, price=None, user=None, stock=None, venue=None):
        booking_kwargs = {"dateUsed": datetime.datetime.utcnow()}
        if user:
            booking_kwargs["user"] = user
        if stock:
            booking_kwargs["stock"] = stock
        else:
            stock_kwargs = {}
            if price:
                stock_kwargs["price"] = price
            if venue:
                stock_kwargs["collectiveOffer__venue"] = venue
            booking_kwargs["collectiveStock"] = collective_stock_factory(**stock_kwargs)
        booking = educational_factories.UsedCollectiveBookingFactory(**booking_kwargs)
        api.add_event(models.FinanceEventMotive.BOOKING_USED, booking=booking)
        return models.FinanceEvent.query.filter_by(collectiveBooking=booking).one()

    def _make_incident_event(
        self, incident_motive: models.FinanceEventMotive, validation_date: datetime.datetime
    ) -> models.FinanceEvent:
        pricing_point = offerers_factories.VenueFactory()
        booking = bookings_factories.ReimbursedBookingFactory(
            stock__offer__venue__pricing_point=pricing_point,
        )
        used_event = factories.UsedBookingFinanceEventFactory(
            booking=booking,
            pricingOrderingDate=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        factories.PricingFactory(
            status=models.PricingStatus.INVOICED,
            event=used_event,
            booking=booking,
            amount=-1000,
            lines=[factories.PricingLineFactory(amount=1000)],
            venue=booking.venue,
            valueDate=used_event.valueDate,
            pricingPoint=pricing_point,
        )
        booking_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__venue__pricing_point=pricing_point,
            booking__stock__offer__venue__pricing_point=pricing_point,
            newTotalAmount=800,
            booking=booking,
        )

        event = api.add_event(
            incident_motive, booking_incident=booking_incident, incident_validation_date=validation_date
        )
        db.session.flush()
        return event

    def test_pricing_individual(self):
        user = users_factories.RichBeneficiaryFactory()
        event1 = self._make_individual_event(price=19_999, user=user)
        booking1 = event1.booking
        api.price_event(event1)

        pricing1 = models.Pricing.query.one()
        assert pricing1.event == event1
        assert pricing1.booking == booking1
        assert pricing1.collectiveBooking is None
        assert pricing1.venue == booking1.venue
        assert pricing1.pricingPoint == booking1.venue
        assert pricing1.valueDate == booking1.dateUsed
        assert pricing1.amount == -(19_999 * 100)
        assert pricing1.standardRule == "Remboursement total pour les offres physiques"
        assert pricing1.customRule is None
        assert pricing1.revenue == 19_999 * 100
        assert pricing1.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing1.lines[0].amount == -(19_999 * 100)
        assert pricing1.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing1.lines[1].amount == 0

        event2 = self._make_individual_event(price=100, user=user, venue=booking1.venue)
        booking2 = event2.booking
        api.price_event(event2)
        pricing2 = models.Pricing.query.filter_by(booking=event2.booking).one()
        assert pricing2.booking == booking2
        assert pricing2.amount == -(95 * 100)
        assert pricing2.standardRule == "Remboursement à 95% entre 20 000 € et 40 000 € par lieu (>= 2021-09-01)"
        assert pricing2.revenue == pricing1.revenue + (100 * 100)
        assert pricing2.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing2.lines[0].amount == -(100 * 100)
        assert pricing2.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing2.lines[1].amount == 5 * 100

    def test_pricing_collective(self):
        event1 = self._make_collective_event(price=19_999)
        booking1 = event1.collectiveBooking
        api.price_event(event1)
        pricing1 = models.Pricing.query.one()
        assert pricing1.event == event1
        assert pricing1.collectiveBooking == booking1
        assert pricing1.booking is None
        assert pricing1.venue == booking1.venue
        assert pricing1.pricingPoint == booking1.venue
        assert pricing1.valueDate == booking1.dateUsed
        assert pricing1.amount == -(19_999 * 100)
        assert pricing1.standardRule == "Remboursement total pour les offres éducationnelles"
        assert pricing1.customRule is None
        assert pricing1.revenue == 0
        assert pricing1.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing1.lines[0].amount == -(19_999 * 100)
        assert pricing1.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing1.lines[1].amount == 0

        event2 = self._make_collective_event(price=100)
        booking2 = event2.collectiveBooking
        api.price_event(event2)
        pricing2 = models.Pricing.query.filter_by(collectiveBooking=booking2).one()
        assert pricing2.collectiveBooking == booking2
        assert pricing2.amount == -(100 * 100)
        assert pricing1.revenue == 0
        assert pricing2.standardRule == "Remboursement total pour les offres éducationnelles"
        assert pricing2.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing2.lines[0].amount == -(100 * 100)
        assert pricing2.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing2.lines[1].amount == 0

    def test_pricing_incident_reversal_of_original_event(self):
        validation_date = datetime.datetime.utcnow()
        finance_event = self._make_incident_event(
            models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT, validation_date
        )

        api.price_event(finance_event)

        pricings = models.Pricing.query.order_by(models.Pricing.id.desc()).all()
        created_pricing = pricings[0]
        original_pricing = pricings[1]
        assert created_pricing.eventId == finance_event.id
        assert created_pricing.status == models.PricingStatus.VALIDATED
        assert created_pricing.amount == 1000
        assert created_pricing.valueDate == validation_date
        assert created_pricing.revenue == original_pricing.revenue

        assert len(created_pricing.lines) == 1
        assert created_pricing.lines[0].amount == -1000
        assert created_pricing.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE

    def test_price_event_on_cancelled_booking(self):
        venue = offerers_factories.VenueFactory(pricing_point="self", reimbursement_point="self")
        booking = bookings_factories.ReimbursedBookingFactory(stock__offer__venue=venue)
        used_event = factories.UsedBookingFinanceEventFactory(booking=booking)
        original_pricing = api.price_event(used_event)
        original_pricing.status = models.PricingStatus.INVOICED
        total_booking_incident = factories.IndividualBookingFinanceIncidentFactory(
            newTotalAmount=0, incident__venue=venue, booking=booking
        )

        api.validate_finance_incident(total_booking_incident.incident, force_debit_note=False)

        assert total_booking_incident.booking.status == bookings_models.BookingStatus.CANCELLED

        reversal_event = (
            models.FinanceEvent.query.join(models.FinanceEvent.bookingFinanceIncident)
            .filter(models.BookingFinanceIncident.bookingId == booking.id)
            .first()
        )

        pricing = api.price_event(reversal_event)
        assert pricing
        assert pricing.customRuleId == original_pricing.customRuleId
        assert pricing.standardRule == original_pricing.standardRule

    @pytest.mark.parametrize(
        "event_motive",
        [
            models.FinanceEventMotive.INCIDENT_NEW_PRICE,
            models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE,
        ],
    )
    def test_pricing_new_price_event(self, event_motive):
        validation_date = datetime.datetime.utcnow()
        finance_event = self._make_incident_event(event_motive, validation_date)

        api.price_event(finance_event)

        pricings = models.Pricing.query.order_by(models.Pricing.id.desc()).all()
        created_pricing = pricings[0]
        original_pricing = pricings[1]
        assert created_pricing.eventId == finance_event.id
        assert created_pricing.status == models.PricingStatus.VALIDATED
        assert created_pricing.amount == -800
        assert created_pricing.valueDate == validation_date
        assert created_pricing.revenue == original_pricing.revenue + 800

        assert len(created_pricing.lines) == 2
        assert created_pricing.lines[0].amount == -800
        assert created_pricing.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert created_pricing.lines[1].amount == 0
        assert created_pricing.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION

    def test_price_free_booking(self):
        event = self._make_individual_event(price=0)
        pricing = api.price_event(event)
        assert models.Pricing.query.count() == 1
        assert pricing.amount == 0

    def test_accrue_revenue(self):
        event1 = self._make_individual_event(price=10)
        venue = event1.booking.venue
        event2 = self._make_individual_event(venue=venue, price=20)
        event3 = self._make_collective_event(venue=venue, price=40)
        pricing1 = api.price_event(event1)
        pricing2 = api.price_event(event2)
        pricing3 = api.price_event(event3)
        assert pricing1.revenue == 1000
        assert pricing2.revenue == 3000
        assert pricing3.revenue == 3000  # collective bookings are not included in revenue

    def test_price_with_dependent_event(self):
        event1 = self._make_individual_event()
        api.price_event(event1)
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        event2 = self._make_individual_event(used_date=past, venue=event1.venue)
        api.price_event(event2)
        # Pricing of `event1.booking1` has been deleted.
        single_pricing = models.Pricing.query.one()
        assert single_pricing.event == event2

    def test_dont_price_twice_its_all_right(self):
        event = self._make_individual_event()
        api.price_event(event)
        assert models.Pricing.query.count() == 1
        api.price_event(event)
        assert models.Pricing.query.count() == 1

    def test_price_booking_that_has_been_unused_and_then_used_again(self):
        event = self._make_individual_event()

        api.price_event(event)
        assert models.Pricing.query.count() == 1

        bookings_api.mark_as_unused(event.booking)
        assert models.Pricing.query.count() == 1
        assert event.status == models.FinanceEventStatus.CANCELLED
        assert models.FinanceEvent.query.filter_by(status=models.FinanceEventStatus.READY).count() == 0

        bookings_api.mark_as_used(event.booking)
        event = models.FinanceEvent.query.filter_by(status=models.FinanceEventStatus.READY).one()
        api.price_event(event)
        assert models.Pricing.query.count() == 2
        assert event.pricings[0].status == models.PricingStatus.VALIDATED

    def test_num_queries(self):
        event = self._make_individual_event()

        queries = 0
        queries += 1  # acquire lock on pricing point
        queries += 1  # fetch event again with multiple joinedload
        queries += 1  # select existing Pricing (if any)
        queries += 1  # select dependent pricings
        queries += 1  # calculate revenue
        queries += 1  # select all CustomReimbursementRule
        queries += 1  # update status of FinanceEvent
        queries += 1  # insert 1 Pricing
        queries += 1  # insert 2 PricingLine
        with assert_num_queries(queries):
            api.price_event(event)

    def test_pricing_full_offerer_contribution(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

        digital_offer = offers_factories.DigitalOfferFactory(venue=venue)

        stock = offers_factories.EventStockFactory(
            offer=digital_offer,
            beginningDatetime=datetime.datetime.utcnow(),
            price=14,
        )
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        finance_event = factories.FinanceEventFactory(
            booking=booking,
            pricingOrderingDate=stock.beginningDatetime,
            status=models.FinanceEventStatus.READY,
            venue=venue,
        )

        price_event = api.price_event(finance_event)

        assert price_event.venue == venue
        assert price_event.pricingPoint == venue
        assert price_event.status == models.PricingStatus.VALIDATED
        assert price_event.amount == 0
        assert price_event.booking == booking
        assert price_event.revenue == 1400

        assert len(price_event.lines) == 2
        assert {line.amount for line in price_event.lines} == {1400, -1400}
        line1 = [line for line in price_event.lines if line.amount == 1400][0]
        line2 = [line for line in price_event.lines if line.amount == -1400][0]
        assert line1.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert line2.category == models.PricingLineCategory.OFFERER_REVENUE


class PriceEventsTest:
    few_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    def test_basics(self):
        event1 = factories.UsedBookingFinanceEventFactory(
            booking__dateUsed=self.few_minutes_ago,
            booking__stock__offer__venue__pricing_point="self",
        )
        event2 = factories.UsedBookingFinanceEventFactory(
            booking__dateUsed=self.few_minutes_ago,
            booking__stock__offer__venue__pricing_point="self",
        )

        api.price_events(min_date=self.few_minutes_ago)

        assert len(event1.pricings) == 1
        assert len(event2.pricings) == 1
        assert event1.status == models.FinanceEventStatus.PRICED
        assert event2.status == models.FinanceEventStatus.PRICED

    @mock.patch("pcapi.core.finance.api.price_event", lambda booking: None)
    def test_num_queries(self):
        factories.UsedBookingFinanceEventFactory(
            booking__dateUsed=self.few_minutes_ago,
            booking__stock__offer__venue__pricing_point="self",
        )
        factories.UsedBookingFinanceEventFactory(
            booking__dateUsed=self.few_minutes_ago,
            booking__stock__offer__venue__pricing_point="self",
        )

        n_queries = 0
        n_queries += 1  # count of events to price
        n_queries += 1  # select events
        with assert_num_queries(n_queries):
            api.price_events(min_date=self.few_minutes_ago)


class AddEventTest:
    def test_used(self):
        motive = models.FinanceEventMotive.BOOKING_USED
        pricing_point = offerers_factories.VenueFactory()
        booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue__pricing_point=pricing_point,
        )

        event = api.add_event(motive=motive, booking=booking)
        db.session.flush()  # setup relations

        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.READY
        assert event.motive == motive
        assert event.valueDate == booking.dateUsed
        assert event.venue == booking.venue
        assert event.pricingPoint == pricing_point
        assert event.pricingOrderingDate == booking.dateUsed

    def test_used_after_cancellation(self):
        motive = models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION
        pricing_point = offerers_factories.VenueFactory()
        booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue__pricing_point=pricing_point,
        )

        event = api.add_event(motive=motive, booking=booking)

        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.READY
        assert event.motive == motive
        assert event.valueDate == booking.dateUsed

    def test_unused(self):
        motive = models.FinanceEventMotive.BOOKING_UNUSED

        pricing_point = offerers_factories.VenueFactory()
        booking = bookings_factories.BookingFactory(
            stock__offer__venue__pricing_point=pricing_point,
        )

        event = api.add_event(motive=motive, booking=booking)

        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.NOT_TO_BE_PRICED
        assert event.motive == motive

    def test_cancelled_after_use(self):
        motive = models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE
        booking = bookings_factories.CancelledBookingFactory()

        event = api.add_event(motive=motive, booking=booking)

        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.NOT_TO_BE_PRICED
        assert event.motive == motive

    @pytest.mark.parametrize(
        "incident_motive",
        [
            models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT,
            models.FinanceEventMotive.INCIDENT_NEW_PRICE,
            models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE,
        ],
    )
    def test_create_incident_event(self, incident_motive):
        pricing_point = offerers_factories.VenueFactory()
        booking_incident = factories.IndividualBookingFinanceIncidentFactory(
            booking__stock__offer__venue__pricing_point=pricing_point,
            incident__venue__pricing_point=pricing_point,
        )
        validation_date = datetime.datetime.utcnow()
        event = api.add_event(
            incident_motive,
            booking_incident=booking_incident,
            incident_validation_date=validation_date,
        )

        assert event.bookingFinanceIncident == booking_incident
        assert event.status == models.FinanceEventStatus.READY
        assert event.motive == incident_motive
        assert event.pricingOrderingDate == validation_date


class CancelLatestEventTest:
    def test_with_booking_used(self):
        event = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point="self",
        )
        pricing = factories.PricingFactory(event=event, booking=event.booking)

        api.cancel_latest_event(event.booking)

        assert event.status == models.FinanceEventStatus.CANCELLED
        assert pricing.status == models.PricingStatus.CANCELLED

    def test_with_booking_used_after_cancellation(self):
        event = factories.UsedBookingFinanceEventFactory(
            motive=models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
            booking__stock__offer__venue__pricing_point="self",
        )
        pricing = factories.PricingFactory(event=event, booking=event.booking)

        api.cancel_latest_event(event.booking)

        assert event.status == models.FinanceEventStatus.CANCELLED
        assert pricing.status == models.PricingStatus.CANCELLED

    def test_no_event_to_cancel(self):
        booking = bookings_factories.UsedBookingFactory()

        event = api.cancel_latest_event(booking)

        assert event is None

    def test_event_is_not_cancellable_because_of_processed_pricing(self):
        event = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point="self",
        )
        pricing = factories.PricingFactory(
            event=event,
            booking=event.booking,
            status=models.PricingStatus.PROCESSED,
        )

        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_latest_event(event.booking)

        assert event.status == models.FinanceEventStatus.READY  # unchanged
        assert pricing.status == models.PricingStatus.PROCESSED  # unchanged

    def test_delete_dependent_pricings(self):
        event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point="self",
            status=models.FinanceEventStatus.PRICED,
        )
        factories.PricingFactory(event=event1, booking=event1.booking)
        event2 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point=event1.pricingPoint,
            status=models.FinanceEventStatus.PRICED,
        )
        factories.PricingFactory(event=event2, booking=event2.booking)

        api.cancel_latest_event(event1.booking)

        assert event1.status == models.FinanceEventStatus.CANCELLED
        assert event1.pricings[0].status == models.PricingStatus.CANCELLED

        assert event2.status == models.FinanceEventStatus.READY
        assert not event2.pricings

    def test_cannot_delete_dependent_pricings_that_are_not_deletable(self):
        event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point="self",
            status=models.FinanceEventStatus.PRICED,
        )
        ppoint = event1.pricingPoint
        factories.PricingFactory(event=event1, booking=event1.booking)
        event2 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point=ppoint,
            status=models.FinanceEventStatus.PRICED,
        )
        factories.PricingFactory(
            event=event2,
            booking=event2.booking,
            status=models.PricingStatus.PROCESSED,
        )

        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_latest_event(event1.booking)

        # No changes!
        assert event1.status == models.FinanceEventStatus.PRICED
        assert event1.pricings[0].status == models.PricingStatus.VALIDATED
        assert event2.status == models.FinanceEventStatus.PRICED
        assert event2.pricings[0].status == models.PricingStatus.PROCESSED

        with override_settings(FINANCE_OVERRIDE_PRICING_ORDERING_ON_PRICING_POINTS=[ppoint.id]):
            api.cancel_latest_event(event1.booking)

        # This time, event1 and its pricing were cancelled. event2 and
        # its pricing were left untouched.
        assert event1.status == models.FinanceEventStatus.CANCELLED
        assert event1.pricings[0].status == models.PricingStatus.CANCELLED
        assert event2.status == models.FinanceEventStatus.PRICED  # unchanged
        assert event2.pricings[0].status == models.PricingStatus.PROCESSED  # unchanged


class UpdateFinanceEventPricingDateTest:
    @time_machine.travel("2023-10-20 17:00:00", tick=False)
    def test_editing_beginning_datetime_edits_finance_event(self):
        # Given
        new_beginning_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=4)

        pricing_point = offerers_factories.VenueFactory()
        oldest_event = _generate_finance_event_context(
            pricing_point, datetime.datetime.utcnow() + datetime.timedelta(days=2), datetime.datetime.utcnow()
        )
        older_event = _generate_finance_event_context(
            pricing_point, datetime.datetime.utcnow() + datetime.timedelta(days=6), datetime.datetime.utcnow()
        )
        changing_event = _generate_finance_event_context(
            pricing_point, datetime.datetime.utcnow() + datetime.timedelta(days=8), datetime.datetime.utcnow()
        )
        newest_event = _generate_finance_event_context(
            pricing_point, datetime.datetime.utcnow() + datetime.timedelta(days=10), datetime.datetime.utcnow()
        )

        unrelated_event = _generate_finance_event_context(
            offerers_factories.VenueFactory(),
            datetime.datetime.utcnow() + datetime.timedelta(days=8),
            datetime.datetime.utcnow(),
        )

        # When
        changing_event.booking.stock.beginningDatetime = new_beginning_datetime
        api.update_finance_event_pricing_date(stock=changing_event.booking.stock)

        # Then
        assert oldest_event.pricingOrderingDate == datetime.datetime.utcnow() + datetime.timedelta(days=2)
        assert oldest_event.status == models.FinanceEventStatus.PRICED
        assert len(oldest_event.pricings) == 1

        assert older_event.pricingOrderingDate == datetime.datetime.utcnow() + datetime.timedelta(days=6)
        assert older_event.status == models.FinanceEventStatus.READY
        assert len(older_event.pricings) == 0

        assert changing_event.pricingOrderingDate == datetime.datetime.utcnow() + datetime.timedelta(days=4)
        assert changing_event.status == models.FinanceEventStatus.READY
        assert len(changing_event.pricings) == 1
        assert changing_event.pricings[0].status == models.PricingStatus.CANCELLED

        assert newest_event.pricingOrderingDate == datetime.datetime.utcnow() + datetime.timedelta(days=10)
        assert newest_event.status == models.FinanceEventStatus.READY
        assert len(newest_event.pricings) == 0

        assert unrelated_event.pricingOrderingDate == datetime.datetime.utcnow() + datetime.timedelta(days=8)
        assert unrelated_event.status == models.FinanceEventStatus.PRICED
        assert len(unrelated_event.pricings) == 1


def _generate_finance_event_context(
    pricing_point: offerers_models.Venue,
    stock_beginning_datetime: datetime.datetime,
    booking_date_used: datetime.datetime,
) -> models.FinanceEvent:
    venue = offerers_factories.VenueFactory(pricing_point=pricing_point)
    stock = offers_factories.EventStockFactory(
        offer__venue=venue,
        beginningDatetime=stock_beginning_datetime,
        bookingLimitDatetime=booking_date_used - datetime.timedelta(days=1),
    )
    booking = bookings_factories.UsedBookingFactory(stock=stock, dateUsed=booking_date_used)
    event = factories.FinanceEventFactory(
        booking=booking,
        pricingOrderingDate=stock.beginningDatetime,
        status=models.FinanceEventStatus.PRICED,
        venue=venue,
    )
    factories.PricingFactory(event=event, booking=event.booking)
    return event


def test_force_event_repricing():
    event_before = factories.UsedBookingFinanceEventFactory(booking__stock__offer__venue__pricing_point="self")
    venue = event_before.venue
    event = factories.UsedBookingFinanceEventFactory(booking__stock__offer__venue=venue)
    event_after = factories.UsedBookingFinanceEventFactory(booking__stock__offer__venue=venue)
    for e in (event_before, event, event_after):
        api.price_event(e)
    assert models.Pricing.query.count() == 3

    api.force_event_repricing(event, models.PricingLogReason.CHANGE_AMOUNT)
    db.session.flush()

    assert event_before.status == models.FinanceEventStatus.PRICED
    assert len(event_before.pricings) == 1
    assert event.status == models.FinanceEventStatus.READY
    assert [e.status for e in event.pricings] == [models.PricingStatus.CANCELLED]
    assert event_after.status == models.FinanceEventStatus.READY
    assert event_after.pricings == []


class GetPricingPointLinkTest:
    def test_used_before_start_of_only_active_link(self):
        # link:      |----------------------
        # used:  ^
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            stock__offer__venue__pricing_point="self",
        )
        link = api.get_pricing_point_link(booking)
        assert link.pricingPoint == booking.venue

    def test_used_after_start_of_only_active_link(self):
        # link:      |---------------------
        # used:          ^
        booking = bookings_factories.BookingFactory(
            stock__offer__venue__pricing_point="self",
            dateUsed=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        )
        link = api.get_pricing_point_link(booking)
        assert link.pricingPoint == booking.venue

    def test_used_after_start_of_subsequent_active_link(self):
        # link:      |----|   |---------------------
        # used:                    ^
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow(),
        )
        _link1 = offerers_factories.VenuePricingPointLinkFactory(
            venue=booking.venue,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=30),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        current_link = offerers_factories.VenuePricingPointLinkFactory(
            venue=booking.venue,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
                None,
            ),
        )
        assert api.get_pricing_point_link(booking) == current_link

    def test_used_between_inactive_and_active_link(self):
        # link:      |------|     |-----------
        # used:                ^
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=15),
        )
        _link1 = offerers_factories.VenuePricingPointLinkFactory(
            venue=booking.venue,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=30),
                datetime.datetime.utcnow() - datetime.timedelta(days=20),
            ),
        )
        current_link = offerers_factories.VenuePricingPointLinkFactory(
            venue=booking.venue,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
                None,
            ),
        )
        assert api.get_pricing_point_link(booking) == current_link

    def test_used_before_start_of_only_inactive_link(self):
        # link:      |------|
        # used:   ^
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=10),
            stock__offer__venue__pricing_point="self",
        )
        link = booking.venue.pricing_point_links[0]
        link.timespan = db_utils.make_timerange(
            datetime.datetime.utcnow() - datetime.timedelta(days=5),
            datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )
        db.session.flush()
        db.session.refresh(link)  # otherwise `link.timespan.lower` is seen as a string

        with pytest.raises(ValueError):
            api.get_pricing_point_link(booking)

    def test_used_after_end_of_inactive_link(self):
        # link:      |------|
        # used:                 ^
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            stock__offer__venue__pricing_point="self",
        )
        link = booking.venue.pricing_point_links[0]
        link.timespan = db_utils.make_timerange(
            link.timespan.lower,
            datetime.datetime.utcnow(),
        )
        db.session.flush()
        db.session.refresh(link)  # otherwise `link.timespan.lower` is seen as a string

        with pytest.raises(ValueError):
            api.get_pricing_point_link(booking)

    def test_used_before_inactive_link_followed_by_active_link(self):
        # link:      |------| |-----------
        # used:   ^
        #
        # The behaviour is not clearly defined. We could raise an
        # error, or choose the second (active) link (assuming that the
        # first link was a mistake). We choose the former.
        booking = bookings_factories.BookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            stock__offer__venue__siret=None,
            stock__offer__venue__comment="no SIRET",
        )
        offerer = booking.venue.managingOfferer
        pricing_point_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_api.link_venue_to_pricing_point(booking.venue, pricing_point_1.id)
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_api.link_venue_to_pricing_point(
            booking.venue,
            pricing_point_2.id,
            force_link=True,
        )

        with pytest.raises(ValueError):
            api.get_pricing_point_link(booking)

    def test_no_link(self):
        booking = bookings_factories.UsedBookingFactory()
        assert not booking.venue.pricing_point_links

        with pytest.raises(ValueError):
            api.get_pricing_point_link(booking)


class GetRevenuePeriodTest:
    def test_after_midnight(self):
        # Year is 2021 in CET.
        value_date = datetime.datetime(2021, 1, 1, 0, 0)
        period = api._get_revenue_period(value_date)

        start = datetime.datetime(2020, 12, 31, 23, 0, tzinfo=pytz.utc)
        end = datetime.datetime(2021, 12, 31, 22, 59, 59, 999999, tzinfo=pytz.utc)
        assert period == (start, end)

    def test_before_midnight(self):
        # Year is 2022 in CET.
        value_date = datetime.datetime(2021, 12, 31, 23, 30)
        period = api._get_revenue_period(value_date)

        start = datetime.datetime(2021, 12, 31, 23, 0, tzinfo=pytz.utc)
        end = datetime.datetime(2022, 12, 31, 22, 59, 59, 999999, tzinfo=pytz.utc)
        assert period == (start, end)


def test_get_next_cashflow_batch_label():
    label = api._get_next_cashflow_batch_label()
    assert label == "VIR1"

    factories.CashflowBatchFactory(label=label)
    label = api._get_next_cashflow_batch_label()
    assert label == "VIR2"


class GenerateCashflowsLegacyTest:
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics(self):
        now = datetime.datetime.utcnow()
        reimbursement_point1 = offerers_factories.VenueFactory()
        bank_info1 = factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point2)
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
            amount=-1000,
        )
        pricing12 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-1000,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        pricing2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-3000,
            booking__stock__beginningDatetime=now - datetime.timedelta(days=1),
            booking__stock__offer__venue__reimbursement_point=reimbursement_point2,
        )
        collective_pricing13 = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__collectiveOffer__venue__reimbursement_point=reimbursement_point1,
            amount=-500,
            collectiveBooking__collectiveStock__beginningDatetime=now - datetime.timedelta(days=1),
        )
        pricing_future_event = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now + datetime.timedelta(days=1),
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        collective_pricing_future_event = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__beginningDatetime=now + datetime.timedelta(days=1),
            collectiveBooking__collectiveStock__collectiveOffer__venue__reimbursement_point=reimbursement_point1,
        )
        pricing_pending = factories.PricingFactory(
            status=models.PricingStatus.PENDING,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        cutoff = datetime.datetime.utcnow()
        pricing_after_cutoff = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )

        batch = api.generate_cashflows(cutoff)

        queried_batch = models.CashflowBatch.query.one()
        assert queried_batch.id == batch.id
        assert queried_batch.cutoff == cutoff
        assert pricing11.status == models.PricingStatus.PROCESSED
        assert pricing12.status == models.PricingStatus.PROCESSED
        assert collective_pricing13.status == models.PricingStatus.PROCESSED
        assert pricing2.status == models.PricingStatus.PROCESSED
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert len(collective_pricing13.cashflows) == 1
        assert pricing11.cashflows == pricing12.cashflows == collective_pricing13.cashflows
        assert len(pricing2.cashflows) == 1
        assert pricing11.cashflows[0].amount == -2500
        assert pricing11.cashflows[0].bankInformation == bank_info1
        assert pricing11.cashflows[0].bankInformationId == bank_info1.id
        assert pricing2.cashflows[0].amount == -3000

        assert not pricing_future_event.cashflows
        assert not collective_pricing_future_event.cashflows
        assert not pricing_pending.cashflows
        assert not pricing_after_cutoff.cashflows

    @pytest.mark.parametrize(
        "booking_pricing,incident_booking_amount",
        [
            (-2000, 10),
            (-1000, 10),
            (-1000, 20),
        ],
    )
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics_with_incident(self, booking_pricing, incident_booking_amount):
        reimbursement_point1 = offerers_factories.VenueFactory(pricing_point="self", reimbursement_point="self")
        bank_info1 = factories.BankInformationFactory(venue=reimbursement_point1)

        # creating an incident for another booking in the same reimbursment_point
        offer = offers_factories.OfferFactory(venue=reimbursement_point1)
        _beginningDatetime = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=30)
        stock = offers_factories.StockFactory(
            offer=offer, price=incident_booking_amount, beginningDatetime=_beginningDatetime
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(stock=stock)

        event = api.add_event(
            motive=models.FinanceEventMotive.BOOKING_USED,
            booking=reimbursed_booking,
        )
        db.session.flush()
        pricing = api.price_event(event)
        pricing.status = models.PricingStatus.INVOICED

        booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(booking=reimbursed_booking)

        finance_incident_events = api._create_finance_events_from_incident(
            booking_finance_incident=booking_finance_incident,
            incident_validation_date=datetime.datetime.utcnow(),
        )

        for finance_incident_event in finance_incident_events:
            api.price_event(finance_incident_event)

        # creating a pricing for a booking
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=reimbursement_point1,
            amount=booking_pricing,
        )
        assert models.Pricing.query.count() == 3

        # Generating Cashflow
        cutoff = datetime.datetime.utcnow()
        batch = api.generate_cashflows(cutoff)

        queried_batch = models.CashflowBatch.query.one()

        processed_pricings = models.Pricing.query.filter(models.Pricing.status == models.PricingStatus.PROCESSED).all()

        if abs(incident_booking_amount * 100) > abs(booking_pricing):
            assert len(processed_pricings) == 0

            assert len(batch.cashflows) == 0
            assert len(pricing11.cashflows) == 0
        elif abs(incident_booking_amount * 100) == abs(booking_pricing):
            assert len(processed_pricings) == 2

            assert len(batch.cashflows) == 0
            assert len(pricing11.cashflows) == 0
        else:
            assert len(processed_pricings) == 2
            assert models.Cashflow.query.count() == 1
            assert len(batch.cashflows) == 1
            assert batch.cashflows[0].amount == booking_pricing + (incident_booking_amount * 100)

            assert len(pricing11.cashflows) == 1
            assert pricing11.cashflows[0].bankInformation == bank_info1

        assert queried_batch.id == batch.id
        assert queried_batch.cutoff == cutoff

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_no_cashflow_if_no_accepted_bank_information(self):
        venue_ok = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue_ok)
        venue_rejected_iban = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(
            venue=venue_rejected_iban,
            status=models.BankInformationStatus.REJECTED,
        )
        venue_without_iban = offerers_factories.VenueFactory(reimbursement_point="self")

        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_ok,
            amount=-1000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_rejected_iban,
            amount=-2000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_without_iban,
            amount=-4000,
        )

        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)

        cashflow = models.Cashflow.query.one()
        assert cashflow.reimbursementPoint == venue_ok

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_no_cashflow_if_total_is_zero(self):
        venue = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue)
        _pricing_total_is_zero_1 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=-1000,
        )
        _pricing_total_is_zero_2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=1000,
        )
        _pricing_free_offer = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=0,
        )
        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)
        assert models.Cashflow.query.count() == 0

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_check_pricing_integrity(self):
        # Price an individual and a collective booking.
        venue1 = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=venue1)
        finance_event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue__pricing_point=venue1,
            booking__stock__offer__venue__reimbursement_point=venue1,
        )
        api.price_event(finance_event1)
        venue2 = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=venue2)
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue__pricing_point=venue2,
            collectiveBooking__collectiveStock__collectiveOffer__venue__reimbursement_point=venue2,
        )
        api.price_event(finance_event2)

        # Do something terrible: change amount of the individual
        # booking and the collective stock without re-pricing
        # bookings.
        finance_event1.booking.amount -= 1
        finance_event2.collectiveBooking.collectiveStock.price -= 1
        db.session.flush()

        api.generate_cashflows(cutoff=datetime.datetime.utcnow())

        assert models.Cashflow.query.count() == 0  # not 2!

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_assert_num_queries(self):
        venue1 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue1)
        venue2 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue2)
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue2,
        )

        cutoff = datetime.datetime.utcnow()

        n_queries = 0
        n_queries += 1  # compute next CashflowBatch.label
        n_queries += 1  # insert CashflowBatch
        n_queries += 1  # check FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY
        n_queries += 1  # select CashflowBatch again after commit
        n_queries += 1  # select reimbursement points and bank account ids to process
        n_queries += 2 * sum(  # 2 reimbursement points
            (
                1,  # check integration of pricings
                1,  # compute sum of pricings
                1,  # insert Cashflow
                1,  # select pricings to be linked to CashflowPricing's
                1,  # insert CashflowPricing's
                1,  # update Pricing.status
                1,  # check sum of pricings = cashflow.amount
            )
        )

        with assert_num_queries(n_queries):
            api.generate_cashflows(cutoff)

        assert models.Cashflow.query.count() == 2


class GenerateCashflowsTest:
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_basics(self):
        now = datetime.datetime.utcnow()
        venue_bank_account_link1 = offerers_factories.VenueBankAccountLinkFactory()
        venue1 = venue_bank_account_link1.venue
        bank_account1 = venue_bank_account_link1.bankAccount
        venue_bank_account_link2 = offerers_factories.VenueBankAccountLinkFactory()
        venue2 = venue_bank_account_link2.venue
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
            amount=-1000,
        )
        pricing12 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-1000,
            booking__stock__offer__venue=venue1,
        )
        pricing2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-3000,
            booking__stock__beginningDatetime=now - datetime.timedelta(days=1),
            booking__stock__offer__venue=venue2,
        )
        collective_pricing13 = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
            amount=-500,
            collectiveBooking__collectiveStock__beginningDatetime=now - datetime.timedelta(days=1),
        )
        pricing_future_event = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now + datetime.timedelta(days=1),
            booking__stock__offer__venue=venue1,
        )
        collective_pricing_future_event = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__beginningDatetime=now + datetime.timedelta(days=1),
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        )
        pricing_pending = factories.PricingFactory(
            status=models.PricingStatus.PENDING,
            booking__stock__offer__venue=venue1,
        )
        cutoff = datetime.datetime.utcnow()
        pricing_after_cutoff = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
        )

        batch = api.generate_cashflows(cutoff)

        queried_batch = models.CashflowBatch.query.one()
        assert queried_batch.id == batch.id
        assert queried_batch.cutoff == cutoff
        assert pricing11.status == models.PricingStatus.PROCESSED
        assert pricing12.status == models.PricingStatus.PROCESSED
        assert collective_pricing13.status == models.PricingStatus.PROCESSED
        assert pricing2.status == models.PricingStatus.PROCESSED
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert len(collective_pricing13.cashflows) == 1
        assert pricing11.cashflows == pricing12.cashflows == collective_pricing13.cashflows
        assert len(pricing2.cashflows) == 1
        assert pricing11.cashflows[0].amount == -2500
        assert pricing11.cashflows[0].bankAccount == bank_account1
        assert pricing11.cashflows[0].bankAccountId == bank_account1.id
        assert pricing2.cashflows[0].amount == -3000

        assert not pricing_future_event.cashflows
        assert not collective_pricing_future_event.cashflows
        assert not pricing_pending.cashflows
        assert not pricing_after_cutoff.cashflows

    @pytest.mark.parametrize(
        "booking_pricing,incident_booking_amount",
        [
            (-2000, 10),
            (-1000, 10),
            (-1000, 20),
        ],
    )
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_basics_with_incident(self, booking_pricing, incident_booking_amount):
        venue1 = offerers_factories.VenueFactory(pricing_point="self")
        venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(venue=venue1)
        bank_account = venue_bank_account_link.bankAccount

        # creating an incident for another booking in the same reimbursment_point
        offer = offers_factories.OfferFactory(venue=venue1)
        _beginningDatetime = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=30)
        stock = offers_factories.StockFactory(
            offer=offer, price=incident_booking_amount, beginningDatetime=_beginningDatetime
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(stock=stock)

        event = api.add_event(
            motive=models.FinanceEventMotive.BOOKING_USED,
            booking=reimbursed_booking,
        )
        db.session.flush()
        pricing = api.price_event(event)
        pricing.status = models.PricingStatus.INVOICED

        booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(booking=reimbursed_booking)

        finance_incident_events = api._create_finance_events_from_incident(
            booking_finance_incident=booking_finance_incident,
            incident_validation_date=datetime.datetime.utcnow(),
        )

        for finance_incident_event in finance_incident_events:
            api.price_event(finance_incident_event)

        # creating a pricing for a booking
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
            amount=booking_pricing,
        )
        assert models.Pricing.query.count() == 3

        # Generating Cashflow
        cutoff = datetime.datetime.utcnow()
        batch = api.generate_cashflows(cutoff)

        queried_batch = models.CashflowBatch.query.one()

        processed_pricings = models.Pricing.query.filter(models.Pricing.status == models.PricingStatus.PROCESSED).all()

        if abs(incident_booking_amount * 100) > abs(booking_pricing):
            assert len(processed_pricings) == 0

            assert len(batch.cashflows) == 0
            assert len(pricing11.cashflows) == 0
        elif abs(incident_booking_amount * 100) == abs(booking_pricing):
            assert len(processed_pricings) == 2

            assert len(batch.cashflows) == 1
            assert batch.cashflows[0].amount == 0

            assert len(pricing11.cashflows) == 1
            assert pricing11.cashflows[0].bankAccount == bank_account
        else:
            assert len(processed_pricings) == 2
            assert models.Cashflow.query.count() == 1
            assert len(batch.cashflows) == 1
            assert batch.cashflows[0].amount == booking_pricing + (incident_booking_amount * 100)

            assert len(pricing11.cashflows) == 1
            assert pricing11.cashflows[0].bankAccount == bank_account

        assert queried_batch.id == batch.id
        assert queried_batch.cutoff == cutoff

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_no_cashflow_if_no_accepted_bank_account(self):
        venue_ok = offerers_factories.VenueFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_ok)
        venue_rejected_iban = offerers_factories.VenueFactory()
        rejected_bank_account = factories.BankAccountFactory(
            offerer=venue_rejected_iban.managingOfferer, status=models.BankAccountApplicationStatus.REFUSED
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_rejected_iban, bankAccount=rejected_bank_account)
        venue_without_iban = offerers_factories.VenueFactory()

        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_ok,
            amount=-1000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_rejected_iban,
            amount=-2000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_without_iban,
            amount=-4000,
        )

        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)

        cashflow = models.Cashflow.query.one()
        assert cashflow.bankAccount == venue_ok.current_bank_account_link.bankAccount

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_cashflow_for_zero_total(self):
        venue = offerers_factories.VenueFactory()
        venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(venue=venue)
        bank_account = venue_bank_account_link.bankAccount
        _pricing_total_is_zero_1 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=-1000,
        )
        _pricing_total_is_zero_2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=1000,
        )
        _pricing_free_offer = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=0,
        )
        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)
        cashflows = models.Cashflow.query.all()
        assert len(cashflows) == 1
        cashflow = cashflows[0]
        assert cashflow.bankAccount == bank_account
        assert cashflow.status == models.CashflowStatus.PENDING
        assert cashflow.amount == 0

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_check_pricing_integrity(self):
        # Price an individual and a collective booking.
        venue1 = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1)
        finance_event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock__offer__venue=venue1,
        )
        api.price_event(finance_event1)
        venue2 = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2)
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue2,
        )
        api.price_event(finance_event2)

        # Do something terrible: change amount of the individual
        # booking and the collective stock without re-pricing
        # bookings.
        finance_event1.booking.amount -= 1
        finance_event2.collectiveBooking.collectiveStock.price -= 1
        db.session.flush()

        api.generate_cashflows(cutoff=datetime.datetime.utcnow())

        assert models.Cashflow.query.count() == 0  # not 2!

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_assert_num_queries(self):
        venue1 = offerers_factories.VenueFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1)
        venue2 = offerers_factories.VenueFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2)
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue1,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue2,
        )

        cutoff = datetime.datetime.utcnow()

        n_queries = 0
        n_queries += 1  # compute next CashflowBatch.label
        n_queries += 1  # insert CashflowBatch
        n_queries += 1  # check FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY
        n_queries += 1  # select CashflowBatch again after commit
        n_queries += 1  # select reimbursement points and bank account ids to process
        n_queries += 2 * sum(  # 2 reimbursement points
            (
                1,  # check integration of pricings
                1,  # compute sum of pricings
                1,  # insert Cashflow
                1,  # select pricings to be linked to CashflowPricing's
                1,  # insert CashflowPricing's
                1,  # update Pricing.status
                1,  # check sum of pricings = cashflow.amount
            )
        )

        with assert_num_queries(n_queries):
            api.generate_cashflows(cutoff)

        assert models.Cashflow.query.count() == 2


@clean_temporary_files
@time_machine.travel(datetime.datetime(2023, 2, 1, 12, 34, 56))
@mock.patch("pcapi.connectors.googledrive.TestingBackend.create_file")
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
def test_generate_payment_files_with_legacy_generate_cashflows(mocked_gdrive_create_file):
    # The contents of generated files is unit-tested in other test
    # functions below.
    venue = offerers_factories.VenueFactory(
        pricing_point="self",
        reimbursement_point="self",
    )
    # FIXME (dbaty, 2022-09-14): the BankInformation object should
    # automatically be created when linking a reimbursement point.
    factories.BankInformationFactory(venue=venue)
    factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        valueDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
    )
    cutoff = datetime.datetime.utcnow()
    api.generate_cashflows_and_payment_files(cutoff)

    cashflow = models.Cashflow.query.one()
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    assert len(cashflow.logs) == 1
    assert cashflow.logs[0].statusBefore == models.CashflowStatus.PENDING
    assert cashflow.logs[0].statusAfter == models.CashflowStatus.UNDER_REVIEW
    gdrive_file_names = {call.args[1] for call in mocked_gdrive_create_file.call_args_list}
    assert gdrive_file_names == {
        "reimbursement_points_20230201_133456.csv",
        "down_payment_20230201_133456.csv",
    }


@clean_temporary_files
@time_machine.travel(datetime.datetime(2023, 2, 1, 12, 34, 56))
@mock.patch("pcapi.connectors.googledrive.TestingBackend.create_file")
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
def test_generate_payment_files(mocked_gdrive_create_file):
    # The contents of generated files is unit-tested in other test
    # functions below.
    venue = offerers_factories.VenueFactory(
        pricing_point="self",
    )
    bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        valueDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
    )
    cutoff = datetime.datetime.utcnow()
    api.generate_cashflows_and_payment_files(cutoff)

    cashflow = models.Cashflow.query.one()
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    assert len(cashflow.logs) == 1
    assert cashflow.logs[0].statusBefore == models.CashflowStatus.PENDING
    assert cashflow.logs[0].statusAfter == models.CashflowStatus.UNDER_REVIEW
    gdrive_file_names = {call.args[1] for call in mocked_gdrive_create_file.call_args_list}
    assert gdrive_file_names == {
        "bank_accounts_20230201_133456.csv",
        "down_payment_20230201_133456.csv",
    }


@clean_temporary_files
def test_generate_reimbursement_points_file():
    now = datetime.datetime.utcnow()
    point1 = offerers_factories.VenueFactory()
    point2 = offerers_factories.VenueFactory(
        name='Name1\n "with double quotes"   ',
        siret='siret 1 "t"',
    )
    point3 = offerers_factories.VenueFactory()
    factories.BankInformationFactory(venue=point1, iban="older-iban", bic="older-bic")
    factories.BankInformationFactory(venue=point2, iban="some-iban", bic="some-bic")
    factories.BankInformationFactory(venue=point3, iban="newer-iban", bic="newer-bic")
    offerers_factories.VenueReimbursementPointLinkFactory(
        reimbursementPoint=point1, timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)]
    )
    offerers_factories.VenueReimbursementPointLinkFactory(
        reimbursementPoint=point2, timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)]
    )
    offerers_factories.VenueReimbursementPointLinkFactory(
        reimbursementPoint=point3,
        timespan=[
            now - datetime.timedelta(days=1),
        ],
    )

    n_queries = 1  # select reimbursement point data
    with assert_num_queries(n_queries):
        path = api._generate_reimbursement_points_file(datetime.datetime.utcnow() - datetime.timedelta(days=2))

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(point2.id),
        "SIRET": "siret 1 t",
        "Raison sociale du point de remboursement": "Name1 with double quotes",
        "IBAN": "some-iban",
        "BIC": "some-bic",
    }


@clean_temporary_files
def test_generate_bank_accounts_file():
    now = datetime.datetime.utcnow()
    offerer = offerers_factories.OffererFactory(name="Nom de la structure")
    venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_2 = offerers_factories.VenueFactory(
        name='Name1\n "with double quotes"   ', siret='siret 1 "t"', managingOfferer=offerer
    )
    venue_3 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_4 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_5 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_6 = offerers_factories.VenueFactory(managingOfferer=offerer)
    bank_account_1 = factories.BankAccountFactory(
        label="old-label", iban="older-iban", bic="older-bic", offerer=offerer
    )
    bank_account_2 = factories.BankAccountFactory(label="some-label", iban="some-iban", bic="some-bic", offerer=offerer)
    bank_account_3 = factories.BankAccountFactory(
        label="newer-label", iban="newer-iban", bic="newer-bic", offerer=offerer
    )
    bank_account_4 = factories.BankAccountFactory(label="Fourth bank account", offerer=offerer)
    _bank_account_5 = factories.BankAccountFactory(label="Fifth bank account", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_1,
        bankAccount=bank_account_1,
        timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_2,
        bankAccount=bank_account_2,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_3,
        bankAccount=bank_account_3,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_4,
        bankAccount=bank_account_3,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_5,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_6,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    n_queries = 1  # select reimbursement point data
    with assert_num_queries(n_queries):
        path = api._generate_bank_accounts_file(datetime.datetime.utcnow() - datetime.timedelta(days=2))

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 3
    for row, bank_account in zip(rows, [bank_account_2, bank_account_3, bank_account_4]):
        assert row == {
            "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account.id),
            "SIREN de la structure": bank_account.offerer.siren,
            "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account.offerer.name} - {bank_account.label}",
            "IBAN": bank_account.iban,
            "BIC": bank_account.bic,
        }


@clean_temporary_files
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
def test_generate_payments_file_legacy_journey():
    used_date = datetime.datetime(2020, 1, 2)
    # This pricing belongs to a reimbursement point that is the venue
    # of the offer.
    venue1 = offerers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
        pricing_point="self",
        reimbursement_point="self",
    )
    factories.BankInformationFactory(venue=venue1)
    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire formidable",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # A free booking that should not appear in the CSV file.
    factories.PricingFactory(
        amount=0,
        booking__amount=0,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire gratuite",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # These other pricings belong to a reimbursement point that is NOT
    # the venue of the offers.
    reimbursement_point_2 = offerers_factories.VenueFactory(
        siret="22222222233333",
        name="Point de remboursement du Gigantesque Cubitus\n",
    )
    factories.BankInformationFactory(venue=reimbursement_point_2)
    offer_venue2 = offerers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        pricing_point="self",
        reimbursement_point=reimbursement_point_2,
    )
    # the 2 pricings below should be merged together as they share the same BU and same deposit type
    factories.PricingFactory(
        amount=-900,  # rate = 75 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
    )
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(amount=600),
    )
    # pricing for an underage individual booking
    underage_user = users_factories.UnderageBeneficiaryFactory()
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(amount=600),
    )
    # pricing for educational booking
    # check that the right deposit is used for csv
    year1 = EducationalYearFactory()
    year2 = EducationalYearFactory()
    year3 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    deposit2 = EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year2,
        ministry=Ministry.EDUCATION_NATIONALE.name,
    )
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year3, ministry=Ministry.ARMEES.name
    )
    # the 2 following pricing should be merged together in the csv file
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-700,  # rate = 100 %
        collectiveBooking__collectiveStock__price=7,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien 2",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )

    # Create booking for overpayment finance incident
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=12,
        dateUsed=used_date,
        stock__offer__name="Une histoire plutôt bien",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=offer_venue2,
    )

    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)
    factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        venue=incident_booking.venue,
        valueDate=datetime.datetime.utcnow(),
    )

    # Create finance incident on the booking above (incident amount: 2€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=1000
    )
    incident_events = api._create_finance_events_from_incident(booking_finance_incident, datetime.datetime.utcnow())

    for event in incident_events:
        api.price_event(event)

    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff).id

    n_queries = 1  # select pricings
    with assert_num_queries(n_queries):
        path = api._generate_payments_file_legacy(batch_id)

    with open(path, encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(venue1.id),
        "SIRET du point de remboursement": "123456 test",
        "Libellé du point de remboursement": "Le Petit Rintintin test",
        "Montant net offreur": 10,
    }
    assert rows[1] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point_2.id),
        "SIRET du point de remboursement": "22222222233333",
        "Libellé du point de remboursement": "Point de remboursement du Gigantesque Cubitus",
        "Montant net offreur": 6 + 15 + 10 - 2,
    }


@clean_temporary_files
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
def test_generate_payments_file_new_journey():
    used_date = datetime.datetime(2020, 1, 2)
    venue1 = offerers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
        pricing_point="self",
    )
    bank_account_1 = factories.BankAccountFactory(offerer=venue1.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )
    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire formidable",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # A free booking that should not appear in the CSV file.
    factories.PricingFactory(
        amount=0,
        booking__amount=0,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire gratuite",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )

    venue2 = offerers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        pricing_point="self",
    )
    bank_account_2 = factories.BankAccountFactory(offerer=venue2.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_2, timespan=(datetime.datetime.utcnow(),)
    )
    # the 2 pricings below should be merged together as they share the same BU and same deposit type
    factories.PricingFactory(
        amount=-900,  # rate = 75 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
    )
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(amount=600),
    )
    # pricing for an underage individual booking
    underage_user = users_factories.UnderageBeneficiaryFactory()
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(amount=600),
    )
    # pricing for educational booking
    # check that the right deposit is used for csv
    year1 = EducationalYearFactory()
    year2 = EducationalYearFactory()
    year3 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    deposit2 = EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year2,
        ministry=Ministry.EDUCATION_NATIONALE.name,
    )
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year3, ministry=Ministry.ARMEES.name
    )
    # the 2 following pricing should be merged together in the csv file
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-700,  # rate = 100 %
        collectiveBooking__collectiveStock__price=7,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien 2",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )

    # Create booking for overpayment finance incident
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=12,
        dateUsed=used_date,
        stock__offer__name="Une histoire plutôt bien",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=venue2,
    )

    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)
    factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        venue=incident_booking.venue,
        valueDate=datetime.datetime.utcnow(),
    )

    # Create finance incident on the booking above (incident amount: 2€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=1000
    )
    incident_events = api._create_finance_events_from_incident(booking_finance_incident, datetime.datetime.utcnow())

    for event in incident_events:
        api.price_event(event)

    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff).id

    n_queries = 1  # select pricings
    with assert_num_queries(n_queries):
        path = api._generate_payments_file(batch_id)

    with open(path, encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "SIREN de la structure": bank_account_1.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_1.offerer.name} - {bank_account_1.label}",
        "Montant net offreur": 10,
    }
    assert rows[1] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_2.id),
        "SIREN de la structure": bank_account_2.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_2.offerer.name} - {bank_account_2.label}",
        "Montant net offreur": 6 + 15 + 10 - 2,
    }


@clean_temporary_files
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
def test_generate_invoice_file_legacy_journey():
    first_siret = "12345678900"
    reimbursement_point1 = offerers_factories.VenueFactory(siret=first_siret)
    bank_info1 = factories.BankInformationFactory(venue=reimbursement_point1)
    offerer1 = reimbursement_point1.managingOfferer
    pricing_point1 = offerers_factories.VenueFactory(managingOfferer=offerer1)
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        pricing_point=pricing_point1,
        reimbursement_point=reimbursement_point1,
    )
    pricing1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline11 = factories.PricingLineFactory(pricing=pricing1, amount=-1100)
    pline12 = factories.PricingLineFactory(
        pricing=pricing1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # add a pricing with identical pricing line values, to make sure it's taken into account
    pricing_with_same_values_as_pricing_1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline11_identical = factories.PricingLineFactory(pricing=pricing_with_same_values_as_pricing_1, amount=-1100)
    pline12_identical = factories.PricingLineFactory(
        pricing=pricing_with_same_values_as_pricing_1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    pricing2 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline21 = factories.PricingLineFactory(pricing=pricing2, amount=-1100)
    pline22 = factories.PricingLineFactory(
        pricing=pricing2,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac pricing
    year1 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    deposit = EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    pricing3 = factories.CollectivePricingFactory(
        amount=-3000,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
        collectiveBooking__educationalInstitution=deposit.educationalInstitution,
        collectiveBooking__educationalYear=deposit.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    pline31 = factories.PricingLineFactory(pricing=pricing3, amount=-3300)
    pline32 = factories.PricingLineFactory(
        pricing=pricing3,
        amount=300,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac related to a program
    educational_program = educational_factories.EducationalInstitutionProgramFactory(label="Marseille en grand")
    educational_institution_with_program = EducationalInstitutionFactory(programs=[educational_program])
    deposit_with_program = EducationalDepositFactory(
        educationalInstitution=educational_institution_with_program,
        educationalYear=year1,
        ministry=Ministry.AGRICULTURE.name,
    )
    pricing4 = factories.CollectivePricingFactory(
        amount=-2345,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        collectiveBooking__educationalInstitution=educational_institution_with_program,
        collectiveBooking__educationalYear=deposit_with_program.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    pline4 = factories.PricingLineFactory(pricing=pricing4, amount=-2345)

    # Create booking for overpayment finance incident
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=18,
        dateUsed=datetime.datetime.utcnow(),
        stock__offer__name="Une histoire plutôt bien",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=venue,
    )

    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)
    incident_booking_original_pricing = factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        valueDate=datetime.datetime.utcnow(),
        amount=-1800,
    )
    factories.PricingLineFactory(pricing=incident_booking_original_pricing, amount=-1800)
    factories.PricingLineFactory(
        pricing=incident_booking_original_pricing,
        amount=0,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # Create finance incident on the booking above (incident amount: 2€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=1600
    )
    incident_events = api._create_finance_events_from_incident(booking_finance_incident, datetime.datetime.utcnow())

    incidents_pricings = []
    for event in incident_events:
        incidents_pricings.append(api.price_event(event))

    cashflow1 = factories.CashflowFactory(
        bankInformation=bank_info1,
        reimbursementPoint=reimbursement_point1,
        pricings=[pricing1, pricing_with_same_values_as_pricing_1, pricing2, pricing3, pricing4, *incidents_pricings],
        status=models.CashflowStatus.ACCEPTED,
    )
    invoice1 = factories.InvoiceFactory(
        reimbursementPoint=reimbursement_point1,
        cashflows=[cashflow1],
    )

    # The file should contain only cashflows from the selected batch.
    # This second invoice should not appear.
    second_siret = "12345673900"
    reimbursement_point2 = offerers_factories.VenueFactory(siret=second_siret)
    bank_info2 = factories.BankInformationFactory(venue=reimbursement_point2)
    offerer2 = reimbursement_point2.managingOfferer
    pricing_point2 = offerers_factories.VenueFactory(managingOfferer=offerer2)
    offerers_factories.VenueFactory(
        managingOfferer=offerer2,
        pricing_point=pricing_point2,
        reimbursement_point=reimbursement_point2,
    )
    pline5 = factories.PricingLineFactory()
    pricing5 = pline5.pricing
    cashflow2 = factories.CashflowFactory(
        bankInformation=bank_info2,
        reimbursementPoint=reimbursement_point2,
        pricings=[pricing5],
        status=models.CashflowStatus.ACCEPTED,
    )
    factories.InvoiceFactory(
        reimbursementPoint=reimbursement_point2,
        cashflows=[cashflow2],
        reference="not displayed because on a different date",
        date=datetime.datetime(2022, 1, 1),
    )

    # Freeze time so that we can guess the timestamp of the CSV file.
    with time_machine.travel(datetime.datetime(2023, 2, 1, 12, 34, 56)):
        path = api.generate_invoice_file_legacy(cashflow1.batch)
    with zipfile.ZipFile(path) as zfile:
        with zfile.open("invoices_20230201_133456.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 5
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline11.category.value,
        "Type de réservation": "PC",
        "Ministère": "",
        "Somme des tickets de facturation": pline11.amount
        + pline11_identical.amount
        + pline21.amount
        + 200,  # 200 is the incident amount
    }
    assert rows[1] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline12.category.value,
        "Type de réservation": "PC",
        "Ministère": "",
        "Somme des tickets de facturation": pline12.amount + pline12_identical.amount + pline22.amount,
    }
    # collective pricing lines
    assert rows[2] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline31.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": pline31.amount,
    }
    assert rows[3] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline32.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": pline32.amount,
    }
    assert rows[4] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline4.category.value,
        "Type de réservation": "EACC",
        "Ministère": educational_program.label,
        "Somme des tickets de facturation": pline4.amount,
    }


@clean_temporary_files
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
def test_generate_invoice_file_new_journey():
    first_siret = "12345678900"
    venue = offerers_factories.VenueFactory(siret=first_siret, pricing_point="self")
    offerer1 = venue.managingOfferer
    bank_account_1 = factories.BankAccountFactory(offerer=offerer1)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )
    pricing1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline11 = factories.PricingLineFactory(pricing=pricing1, amount=-1100)
    pline12 = factories.PricingLineFactory(
        pricing=pricing1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # add a pricing with identical pricing line values, to make sure it's taken into account
    pricing_with_same_values_as_pricing_1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline11_identical = factories.PricingLineFactory(pricing=pricing_with_same_values_as_pricing_1, amount=-1100)
    pline12_identical = factories.PricingLineFactory(
        pricing=pricing_with_same_values_as_pricing_1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    pricing2 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        amount=-1000,
    )
    pline21 = factories.PricingLineFactory(pricing=pricing2, amount=-1100)
    pline22 = factories.PricingLineFactory(
        pricing=pricing2,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac pricing
    year1 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    deposit = EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    pricing3 = factories.CollectivePricingFactory(
        amount=-3000,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
        collectiveBooking__educationalInstitution=deposit.educationalInstitution,
        collectiveBooking__educationalYear=deposit.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    pline31 = factories.PricingLineFactory(pricing=pricing3, amount=-3300)
    pline32 = factories.PricingLineFactory(
        pricing=pricing3,
        amount=300,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac related to a program
    educational_program = educational_factories.EducationalInstitutionProgramFactory(label="Marseille en grand")
    educational_institution_with_program = EducationalInstitutionFactory(programs=[educational_program])
    deposit_with_program = EducationalDepositFactory(
        educationalInstitution=educational_institution_with_program,
        educationalYear=year1,
        ministry=Ministry.AGRICULTURE.name,
    )
    pricing4 = factories.CollectivePricingFactory(
        amount=-2345,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        collectiveBooking__educationalInstitution=educational_institution_with_program,
        collectiveBooking__educationalYear=deposit_with_program.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    pline4 = factories.PricingLineFactory(pricing=pricing4, amount=-2345)

    # Create booking for overpayment finance incident
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=18,
        dateUsed=datetime.datetime.utcnow(),
        stock__offer__name="Une histoire plutôt bien",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=venue,
    )

    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)
    incident_booking_original_pricing = factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        valueDate=datetime.datetime.utcnow(),
        amount=-1800,
    )
    factories.PricingLineFactory(pricing=incident_booking_original_pricing, amount=-1800)
    factories.PricingLineFactory(
        pricing=incident_booking_original_pricing,
        amount=0,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # Create finance incident on the booking above (incident amount: 2€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=1600
    )
    incident_events = api._create_finance_events_from_incident(booking_finance_incident, datetime.datetime.utcnow())

    incidents_pricings = []
    for event in incident_events:
        incidents_pricings.append(api.price_event(event))

    cashflow1 = factories.CashflowFactory(
        bankAccount=bank_account_1,
        pricings=[pricing1, pricing_with_same_values_as_pricing_1, pricing2, pricing3, pricing4, *incidents_pricings],
        status=models.CashflowStatus.ACCEPTED,
    )
    invoice1 = factories.InvoiceFactory(
        bankAccount=bank_account_1,
        cashflows=[cashflow1],
    )

    # The file should contain only cashflows from the selected batch.
    # This second invoice should not appear.
    second_siret = "12345673900"
    venue2 = offerers_factories.VenueFactory(siret=second_siret, pricing_point="self")
    offerer2 = venue2.managingOfferer
    bank_account_2 = factories.BankAccountFactory(offerer=offerer2)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account_2)
    pline5 = factories.PricingLineFactory()
    pricing5 = pline5.pricing
    cashflow2 = factories.CashflowFactory(
        bankAccount=bank_account_2,
        pricings=[pricing5],
        status=models.CashflowStatus.ACCEPTED,
    )
    factories.InvoiceFactory(
        bankAccount=bank_account_2,
        cashflows=[cashflow2],
        reference="not displayed because on a different date",
        date=datetime.datetime(2022, 1, 1),
    )

    # Freeze time so that we can guess the timestamp of the CSV file.
    with time_machine.travel(datetime.datetime(2023, 2, 1, 12, 34, 56)):
        path = api.generate_invoice_file(cashflow1.batch)
    with zipfile.ZipFile(path) as zfile:
        with zfile.open("invoices_20230201_133456.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 5
    assert rows[0] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline11.category.value,
        "Type de réservation": "PC",
        "Ministère": "",
        "Somme des tickets de facturation": pline11.amount
        + pline11_identical.amount
        + pline21.amount
        + 200,  # 200 is the incident amount
    }
    assert rows[1] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline12.category.value,
        "Type de réservation": "PC",
        "Ministère": "",
        "Somme des tickets de facturation": pline12.amount + pline12_identical.amount + pline22.amount,
    }
    # collective pricing lines
    assert rows[2] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline31.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": pline31.amount,
    }
    assert rows[3] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline32.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": pline32.amount,
    }
    assert rows[4] == {
        "Identifiant des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline4.category.value,
        "Type de réservation": "EACC",
        "Ministère": educational_program.label,
        "Somme des tickets de facturation": pline4.amount,
    }


class GenerateDebitNotesLegacyTest:
    @mock.patch("pcapi.core.finance.api._generate_debit_note_html_legacy")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @clean_temporary_files
    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_when_there_is_no_debit_not_to_generate(self, _mocked1, _mocked2):
        user = users_factories.RichBeneficiaryFactory()
        venue_kwargs = {
            "pricing_point": "self",
            "reimbursement_point": "self",
        }
        venue = offerers_factories.VenueFactory(**venue_kwargs)
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )

        api.price_event(incident_booking1_event)
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        db.session.flush()

        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_event = api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        api.price_event(incident_event[0])

        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_debit_notes(batch)

        invoices = models.Invoice.query.all()
        assert len(invoices) == 0


class GenerateDebitNotesTest:
    @mock.patch("pcapi.core.finance.api._generate_debit_note_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @clean_temporary_files
    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_when_there_is_no_debit_not_to_generate(self, _mocked1, _mocked2):
        user = users_factories.RichBeneficiaryFactory()
        venue_kwargs = {
            "pricing_point": "self",
        }
        venue = offerers_factories.VenueFactory(**venue_kwargs)
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )

        api.price_event(incident_booking1_event)
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        db.session.flush()

        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_event = api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        api.price_event(incident_event[0])

        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_debit_notes(batch)

        invoices = models.Invoice.query.all()
        assert len(invoices) == 0


@pytest.fixture(name="invoice_data_legacy")
def invoice_test_data_legacy():
    venue_kwargs = {
        "pricing_point": "self",
        "reimbursement_point": "self",
    }
    offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
    venue = offerers_factories.VenueFactory(
        publicName="Coiffeur justificaTIF",
        name="Coiffeur explicaTIF",
        siret="85331845900023",
        bookingEmail="pro@example.com",
        managingOfferer=offerer,
        **venue_kwargs,
    )
    factories.BankInformationFactory(venue=venue, iban="FR2710010000000000000000064")

    reimbursement_point = venue
    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=19_950),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]

    return reimbursement_point, stocks, venue


@pytest.fixture(name="invoice_data")
def invoice_test_data():
    venue_kwargs = {
        "pricing_point": "self",
    }
    offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
    venue = offerers_factories.VenueFactory(
        publicName="Coiffeur justificaTIF",
        name="Coiffeur explicaTIF",
        siret="85331845900023",
        bookingEmail="pro@example.com",
        managingOfferer=offerer,
        **venue_kwargs,
    )
    bank_account = factories.BankAccountFactory(
        offerer=offerer, iban="FR2710010000000000000000064", label="Compte bancaire Coiffeur"
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=19_950),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]

    return bank_account, stocks, venue


class GenerateInvoicesLegacyTest:
    # Mock slow functions that we are not interested in.
    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @clean_temporary_files
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics(self, _mocked1, _mocked2):
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=individual_stock_factory())
        booking1 = finance_event1.booking
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=individual_stock_factory())
        booking2 = finance_event2.booking
        for finance_event in (finance_event1, finance_event2):
            factories.BankInformationFactory(venue=finance_event.booking.venue)

        # Cashflows for booking1 and booking2 will be UNDER_REVIEW.
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_invoices(batch)

        invoices = models.Invoice.query.all()
        assert len(invoices) == 2
        invoiced_bookings = {inv.cashflows[0].pricings[0].booking for inv in invoices}
        assert invoiced_bookings == {booking1, booking2}


class GenerateInvoicesTest:
    # Mock slow functions that we are not interested in.
    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @clean_temporary_files
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_basics(self, _mocked1, _mocked2):
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=individual_stock_factory())
        booking1 = finance_event1.booking
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=individual_stock_factory())
        booking2 = finance_event2.booking
        for finance_event in (finance_event1, finance_event2):
            b_a = factories.BankAccountFactory()
            offerers_factories.VenueBankAccountLinkFactory(venue=finance_event.booking.venue, bankAccount=b_a)

        # Cashflows for booking1 and booking2 will be UNDER_REVIEW.
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_invoices(batch)

        invoices = models.Invoice.query.all()
        assert len(invoices) == 2
        invoiced_bookings = {inv.cashflows[0].pricings[0].booking for inv in invoices}
        assert invoiced_bookings == {booking1, booking2}

    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_invoice_cashflows_with_0_amount(self, _generate_invoice_html, _store_invoice_pdf):
        finance_event = factories.UsedBookingFinanceEventFactory(booking__stock=individual_stock_factory())
        booking = finance_event.booking
        bank_account = factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=finance_event.booking.venue, bankAccount=bank_account)
        factories.CustomReimbursementRuleFactory(rate=0, venue=finance_event.booking.venue)

        api.price_event(finance_event)
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_invoices(batch)

        invoices = models.Invoice.query.all()
        assert len(invoices) == 1
        invoice = invoices[0]
        assert len(invoice.cashflows) == 1
        cashflow = invoice.cashflows[0]
        assert cashflow.amount == 0

        assert len(cashflow.pricings) == 1
        pricing = cashflow.pricings[0]
        assert pricing.booking == booking


class GenerateInvoiceTest:
    EXPECTED_NUM_QUERIES = (
        1  # lock reimbursement point
        + 1  # select cashflows, pricings, pricing_lines, and custom_reimbursement_rules
        + 1  # select and lock ReferenceScheme
        + 1  # update ReferenceScheme
        + 1  # insert invoice
        + 1  # insert invoice lines
        + 1  # insert invoice_cashflows
        + 1  # update Cashflow.status
        + 1  # update Pricing.status
        + 1  # update Booking.status
        + 1  # FF is cached in all test due to generate_cashflows call
    )

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    @time_machine.travel(datetime.datetime(2022, 1, 15))
    def test_reference_scheme_increments(self):
        venue = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
        cashflow1 = factories.CashflowFactory(
            bankAccount=bank_account,
            bankInformation=None,
            status=models.CashflowStatus.UNDER_REVIEW,
        )
        invoice1 = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=[cashflow1.id],
        )
        cashflow2 = factories.CashflowFactory(
            bankAccount=bank_account,
            bankInformation=None,
            status=models.CashflowStatus.UNDER_REVIEW,
        )
        invoice2 = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=[cashflow2.id],
        )

        assert invoice1.reference == "F220000001"
        assert invoice2.reference == "F220000002"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_one_regular_rule_one_rate(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock = offers_factories.ThingStockFactory(offer=offer, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        year = invoice.date.year % 100
        assert invoice.reference == f"F{year}0000001"
        assert invoice.bankAccount == bank_account
        assert invoice.amount == -40 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -40 * 100
        assert line.rate == 1
        assert line.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_two_regular_rules_two_rates(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock1 = offers_factories.ThingStockFactory(offer=offer, price=19_850)
        stock2 = offers_factories.ThingStockFactory(offer=offer, price=160)
        user = users_factories.RichBeneficiaryFactory()
        finance_event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock=stock1,
            booking__user=user,
        )
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        # 100% of 19_850*100 + 95% of 160*100 aka 152*100
        assert invoice.amount == -20_002 * 100
        assert len(invoice.lines) == 2
        invoice_lines = sorted(invoice.lines, key=lambda x: x.rate, reverse=True)

        line_rate_1 = invoice_lines[0]
        assert line_rate_1.group == {"label": "Barème général", "position": 1}
        assert line_rate_1.contributionAmount == 0
        assert line_rate_1.reimbursedAmount == -19_850 * 100
        assert line_rate_1.rate == 1
        assert line_rate_1.label == "Réservations"
        line_rate_0_95 = invoice_lines[1]
        assert line_rate_0_95.group == {"label": "Barème général", "position": 1}
        assert line_rate_0_95.contributionAmount == 8 * 100
        assert line_rate_0_95.reimbursedAmount == -152 * 100
        assert line_rate_0_95.rate == Decimal("0.95")
        assert line_rate_0_95.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_one_custom_rule(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock = offers_factories.ThingStockFactory(offer=offer, price=23)
        factories.CustomReimbursementRuleFactory(amount=2200, offer=offer)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == -4400
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.contributionAmount == 200
        assert line.reimbursedAmount == -4400
        assert line.rate == Decimal("0.9565")
        assert line.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_full_offerer_contribution(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue)
        factories.CustomReimbursementRuleFactory(rate=0, offer=offer)

        stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=datetime.datetime.utcnow(),
            price=23,
        )
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        finance_event = factories.FinanceEventFactory(
            booking=booking,
            pricingOrderingDate=stock.beginningDatetime,
            status=models.FinanceEventStatus.READY,
            venue=venue,
        )

        api.price_event(finance_event)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == 0

        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.reimbursedAmount == 0
        assert line.contributionAmount == 2300
        assert line.rate == Decimal("0")
        assert line.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_100_per_cent_offerer_contribution_mixed(self):
        venue1 = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(managingOfferer=venue1.managingOfferer, pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer1 = offers_factories.DigitalOfferFactory(venue=venue1)
        stock1 = offers_factories.EventStockFactory(
            offer=offer1, beginningDatetime=datetime.datetime.utcnow(), price=10
        )
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=50)
        factories.CustomReimbursementRuleFactory(amount=600, offer=offer2)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == -600

        assert len(invoice.lines) == 2
        assert {line.reimbursedAmount for line in invoice.lines} == {0, -600}
        line1 = [line for line in invoice.lines if line.reimbursedAmount == 0][0]
        line2 = [line for line in invoice.lines if line.reimbursedAmount == -600][0]

        assert line1.group == {"label": "Barème non remboursé", "position": 3}
        assert line1.contributionAmount == 1000
        assert line1.rate == Decimal("0")
        assert line1.label == "Réservations"

        assert line2.group == {"label": "Barème dérogatoire", "position": 4}
        assert line2.contributionAmount == 4400
        assert line2.rate == Decimal("0.12")
        assert line2.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_many_rules_and_rates_two_cashflows(self, invoice_data):
        bank_account, stocks, _venue = invoice_data
        finance_events = []
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            finance_events.append(finance_event)
        for finance_event in finance_events[:3]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        for finance_event in finance_events[3:]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert len(invoice.cashflows) == 2
        assert invoice.bankAccount == bank_account
        assert invoice.amount == -20_156_04
        # général 100%, général 95%, livre 100%, livre 95%, pas remboursé, custom 1, custom 2
        assert len(invoice.lines) == 7

        # sort by group position asc then rate desc, as displayed in the PDF
        invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))

        line0 = invoice_lines[0]
        assert line0.group == {"label": "Barème général", "position": 1}
        assert line0.contributionAmount == 0
        assert line0.reimbursedAmount == -19_980 * 100  # 19_950 + 30
        assert line0.rate == Decimal("1.0000")
        assert line0.label == "Réservations"

        line1 = invoice_lines[1]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 406
        assert line1.reimbursedAmount == -7724
        assert line1.rate == Decimal("0.9500")
        assert line1.label == "Réservations"

        line2 = invoice_lines[2]
        assert line2.group == {"label": "Barème livres", "position": 2}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == -20 * 100
        assert line2.rate == Decimal("1.0000")
        assert line2.label == "Réservations"

        line3 = invoice_lines[3]
        assert line3.group == {"label": "Barème livres", "position": 2}
        assert line3.contributionAmount == 2 * 100
        assert line3.reimbursedAmount == -38 * 100
        assert line3.rate == Decimal("0.9500")
        assert line3.label == "Réservations"

        line4 = invoice_lines[4]
        assert line4.group == {"label": "Barème non remboursé", "position": 3}
        assert line4.contributionAmount == 58 * 100
        assert line4.reimbursedAmount == 0
        assert line4.rate == Decimal("0.0000")
        assert line4.label == "Réservations"

        line5 = invoice_lines[5]
        assert line5.group == {"label": "Barème dérogatoire", "position": 4}
        assert line5.contributionAmount == 100
        assert line5.reimbursedAmount == -22 * 100
        assert line5.rate == Decimal("0.9565")
        assert line5.label == "Réservations"

        line6 = invoice_lines[6]
        assert line6.group == {"label": "Barème dérogatoire", "position": 4}
        assert line6.contributionAmount == 120
        assert line6.reimbursedAmount == -1880
        assert line6.rate == Decimal("0.9400")
        assert line6.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_with_free_offer(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        # 2 offers that have a distinct reimbursement rate rule.
        offer1 = offers_factories.ThingOfferFactory(
            venue=venue2,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock1 = offers_factories.StockFactory(offer=offer1, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        offer2 = offers_factories.ThingOfferFactory(
            venue=venue2,
            subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id,
        )
        stock2 = offers_factories.StockFactory(offer=offer2, price=0)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.amount == -20 * 100
        assert len(invoice.lines) == 2
        line1 = invoice.lines[0]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 0
        assert line1.reimbursedAmount == -20 * 100
        assert line1.rate == 1
        assert line1.label == "Réservations"
        line2 = invoice.lines[1]
        assert line2.group == {"label": "Barème non remboursé", "position": 3}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == 0
        assert line2.rate == 0
        assert line2.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_update_statuses_and_booking_reimbursement_date(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
        stock = individual_stock_factory(offer__venue=venue)
        indiv_finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking1 = indiv_finance_event1.booking
        indiv_finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking2 = indiv_finance_event2.booking
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        collective_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking1 = collective_finance_event1.collectiveBooking
        collective_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking2 = collective_finance_event2.collectiveBooking
        for e in (collective_finance_event1, collective_finance_event2, indiv_finance_event1, indiv_finance_event2):
            api.price_event(e)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = {cf.id for cf in models.Cashflow.query.all()}
        indiv_booking2.status = bookings_models.BookingStatus.CANCELLED
        collective_booking2.status = educational_models.CollectiveBookingStatus.CANCELLED
        db.session.flush()

        invoice = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )

        get_statuses = lambda model: {s for s, in model.query.with_entities(getattr(model, "status"))}
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        assert indiv_booking1.status == bookings_models.BookingStatus.REIMBURSED  # updated
        assert indiv_booking1.reimbursementDate == invoice.date  # updated
        assert indiv_booking2.status == bookings_models.BookingStatus.CANCELLED  # not updated
        assert indiv_booking2.reimbursementDate == invoice.date  # updated
        assert collective_booking1.status == educational_models.CollectiveBookingStatus.REIMBURSED  # updated
        assert collective_booking1.reimbursementDate == invoice.date  # updated
        assert collective_booking2.status == educational_models.CollectiveBookingStatus.CANCELLED  # not updated
        assert collective_booking2.reimbursementDate == invoice.date  # updated


class GenerateInvoiceLegacyTest:
    EXPECTED_NUM_QUERIES = (
        1  # lock reimbursement point
        + 1  # select cashflows, pricings, pricing_lines, and custom_reimbursement_rules
        + 1  # select and lock ReferenceScheme
        + 1  # update ReferenceScheme
        + 1  # insert invoice
        + 1  # insert invoice lines
        + 1  # insert invoice_cashflows
        + 1  # update Cashflow.status
        + 1  # update Pricing.status
        + 1  # update Booking.status
        + 1  # FF is cached in all test due to generate_cashflows call
    )

    @time_machine.travel(datetime.datetime(2022, 1, 15))
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_reference_scheme_increments(self):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point)
        cashflow1 = factories.CashflowFactory(
            reimbursementPoint=reimbursement_point,
            status=models.CashflowStatus.UNDER_REVIEW,
        )
        invoice1 = api._generate_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=[cashflow1.id],
        )
        cashflow2 = factories.CashflowFactory(
            reimbursementPoint=reimbursement_point,
            status=models.CashflowStatus.UNDER_REVIEW,
        )
        invoice2 = api._generate_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=[cashflow2.id],
        )

        assert invoice1.reference == "F220000001"
        assert invoice2.reference == "F220000002"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_one_regular_rule_one_rate(self):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point)
        venue = offerers_factories.VenueFactory(
            managingOfferer=reimbursement_point.managingOfferer,
            pricing_point="self",
            reimbursement_point=reimbursement_point,
        )

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        reimbursement_point_id = reimbursement_point.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        year = invoice.date.year % 100
        assert invoice.reference == f"F{year}0000001"
        assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -40 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -40 * 100
        assert line.rate == 1
        assert line.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_two_regular_rules_two_rates(self):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point)
        venue = offerers_factories.VenueFactory(
            managingOfferer=reimbursement_point.managingOfferer,
            pricing_point="self",
            reimbursement_point=reimbursement_point,
        )

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock1 = offers_factories.ThingStockFactory(offer=offer, price=19_850)
        stock2 = offers_factories.ThingStockFactory(offer=offer, price=160)
        user = users_factories.RichBeneficiaryFactory()
        finance_event1 = factories.UsedBookingFinanceEventFactory(
            booking__stock=stock1,
            booking__user=user,
        )
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        reimbursement_point_id = reimbursement_point.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reimbursementPoint == reimbursement_point
        # 100% of 19_850*100 + 95% of 160*100 aka 152*100
        assert invoice.amount == -20_002 * 100
        assert len(invoice.lines) == 2
        invoice_lines = sorted(invoice.lines, key=lambda x: x.rate, reverse=True)

        line_rate_1 = invoice_lines[0]
        assert line_rate_1.group == {"label": "Barème général", "position": 1}
        assert line_rate_1.contributionAmount == 0
        assert line_rate_1.reimbursedAmount == -19_850 * 100
        assert line_rate_1.rate == 1
        assert line_rate_1.label == "Réservations"
        line_rate_0_95 = invoice_lines[1]
        assert line_rate_0_95.group == {"label": "Barème général", "position": 1}
        assert line_rate_0_95.contributionAmount == 8 * 100
        assert line_rate_0_95.reimbursedAmount == -152 * 100
        assert line_rate_0_95.rate == Decimal("0.95")
        assert line_rate_0_95.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_one_custom_rule(self):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point)
        venue = offerers_factories.VenueFactory(
            managingOfferer=reimbursement_point.managingOfferer,
            pricing_point="self",
            reimbursement_point=reimbursement_point,
        )

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=23)
        factories.CustomReimbursementRuleFactory(amount=2200, offer=offer)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        reimbursement_point_id = reimbursement_point.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -4400
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.contributionAmount == 200
        assert line.reimbursedAmount == -4400
        assert line.rate == Decimal("0.9565")
        assert line.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_many_rules_and_rates_two_cashflows(self, invoice_data_legacy):
        reimbursement_point, stocks, _venue = invoice_data_legacy
        finance_events = []
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            finance_events.append(finance_event)
        for finance_event in finance_events[:3]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        for finance_event in finance_events[3:]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        reimbursement_point_id = reimbursement_point.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert len(invoice.cashflows) == 2
        assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -20_156_04
        # général 100%, général 95%, livre 100%, livre 95%, pas remboursé, custom 1, custom 2
        assert len(invoice.lines) == 7

        # sort by group position asc then rate desc, as displayed in the PDF
        invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))

        line0 = invoice_lines[0]
        assert line0.group == {"label": "Barème général", "position": 1}
        assert line0.contributionAmount == 0
        assert line0.reimbursedAmount == -19_980 * 100  # 19_950 + 30
        assert line0.rate == Decimal("1.0000")
        assert line0.label == "Réservations"

        line1 = invoice_lines[1]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 406
        assert line1.reimbursedAmount == -7724
        assert line1.rate == Decimal("0.9500")
        assert line1.label == "Réservations"

        line2 = invoice_lines[2]
        assert line2.group == {"label": "Barème livres", "position": 2}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == -20 * 100
        assert line2.rate == Decimal("1.0000")
        assert line2.label == "Réservations"

        line3 = invoice_lines[3]
        assert line3.group == {"label": "Barème livres", "position": 2}
        assert line3.contributionAmount == 2 * 100
        assert line3.reimbursedAmount == -38 * 100
        assert line3.rate == Decimal("0.9500")
        assert line3.label == "Réservations"

        line4 = invoice_lines[4]
        assert line4.group == {"label": "Barème non remboursé", "position": 3}
        assert line4.contributionAmount == 58 * 100
        assert line4.reimbursedAmount == 0
        assert line4.rate == Decimal("0.0000")
        assert line4.label == "Réservations"

        line5 = invoice_lines[5]
        assert line5.group == {"label": "Barème dérogatoire", "position": 4}
        assert line5.contributionAmount == 100
        assert line5.reimbursedAmount == -22 * 100
        assert line5.rate == Decimal("0.9565")
        assert line5.label == "Réservations"

        line6 = invoice_lines[6]
        assert line6.group == {"label": "Barème dérogatoire", "position": 4}
        assert line6.contributionAmount == 120
        assert line6.reimbursedAmount == -1880
        assert line6.rate == Decimal("0.9400")
        assert line6.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_with_free_offer(self):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point)
        venue = offerers_factories.VenueFactory(
            managingOfferer=reimbursement_point.managingOfferer,
            pricing_point="self",
            reimbursement_point=reimbursement_point,
        )

        # 2 offers that have a distinct reimbursement rate rule.
        offer1 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock1 = offers_factories.StockFactory(offer=offer1, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        offer2 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id,
        )
        stock2 = offers_factories.StockFactory(offer=offer2, price=0)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        reimbursement_point_id = reimbursement_point.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.amount == -20 * 100
        assert len(invoice.lines) == 2
        line1 = invoice.lines[0]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 0
        assert line1.reimbursedAmount == -20 * 100
        assert line1.rate == 1
        assert line1.label == "Réservations"
        line2 = invoice.lines[1]
        assert line2.group == {"label": "Barème non remboursé", "position": 3}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == 0
        assert line2.rate == 0
        assert line2.label == "Réservations"

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_update_statuses_and_booking_reimbursement_date(self):
        stock = individual_stock_factory()
        indiv_finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking1 = indiv_finance_event1.booking
        indiv_finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking2 = indiv_finance_event2.booking
        venue = stock.offer.venue
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        collective_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking1 = collective_finance_event1.collectiveBooking
        collective_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__beginningDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking2 = collective_finance_event2.collectiveBooking
        for e in (collective_finance_event1, collective_finance_event2, indiv_finance_event1, indiv_finance_event2):
            api.price_event(e)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = {cf.id for cf in models.Cashflow.query.all()}
        indiv_booking2.status = bookings_models.BookingStatus.CANCELLED
        collective_booking2.status = educational_models.CollectiveBookingStatus.CANCELLED
        db.session.flush()

        invoice = api._generate_invoice_legacy(
            reimbursement_point_id=venue.current_reimbursement_point_id,
            cashflow_ids=cashflow_ids,
        )

        get_statuses = lambda model: {s for s, in model.query.with_entities(getattr(model, "status"))}
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        assert indiv_booking1.status == bookings_models.BookingStatus.REIMBURSED  # updated
        assert indiv_booking1.reimbursementDate == invoice.date  # updated
        assert indiv_booking2.status == bookings_models.BookingStatus.CANCELLED  # not updated
        assert indiv_booking2.reimbursementDate == invoice.date  # updated
        assert collective_booking1.status == educational_models.CollectiveBookingStatus.REIMBURSED  # updated
        assert collective_booking1.reimbursementDate == invoice.date  # updated
        assert collective_booking2.status == educational_models.CollectiveBookingStatus.CANCELLED  # not updated
        assert collective_booking2.reimbursementDate == invoice.date  # updated


class PrepareInvoiceContextLegacyTest:
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_context(self, invoice_data_legacy):
        reimbursement_point, stocks, _venue = invoice_data_legacy
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        invoice = api._generate_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=cashflow_ids,
        )
        batch = models.CashflowBatch.query.get(batch.id)

        context = api._prepare_invoice_context_legacy(invoice, batch)

        general, books, not_reimbursed, custom = tuple(g for g in context["groups"])
        assert general.used_bookings_subtotal == 2006130
        assert general.contribution_subtotal == 406
        assert general.reimbursed_amount_subtotal == -2005724

        assert books.used_bookings_subtotal == 6000
        assert books.contribution_subtotal == 200
        assert books.reimbursed_amount_subtotal == -5800

        assert not_reimbursed.used_bookings_subtotal == 5800
        assert not_reimbursed.contribution_subtotal == 5800
        assert not_reimbursed.reimbursed_amount_subtotal == 0

        assert custom.used_bookings_subtotal == 4300
        assert custom.contribution_subtotal == 220
        assert custom.reimbursed_amount_subtotal == -4080

        assert context["invoice"] == invoice
        assert context["total_used_bookings_amount"] == 2022230
        assert context["total_contribution_amount"] == 6626
        assert context["total_reimbursed_amount"] == -2015604

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_get_invoice_period_second_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 31))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 16)
        assert end_period == datetime.date(2020, 3, 31)

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_get_invoice_period_first_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 15))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 1)
        assert end_period == datetime.date(2020, 3, 15)

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_common_name_is_not_empty_public_name(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        venue_kwargs = {
            "pricing_point": "self",
            "reimbursement_point": "self",
        }
        venue = offerers_factories.VenueFactory(
            publicName="",
            name="common name should not be empty",
            siret="85331845900023",
            bookingEmail="pro@example.com",
            managingOfferer=offerer,
            **venue_kwargs,
        )
        factories.BankInformationFactory(venue=venue, iban="FR2710010000000000000000064")

        thing_offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=thing_offer, price=30)

        user = users_factories.RichBeneficiaryFactory()
        finance_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=stock,
            booking__user=user,
        )
        api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        invoice = api._generate_invoice_legacy(
            reimbursement_point_id=venue.id,
            cashflow_ids=cashflow_ids,
        )
        batch = models.CashflowBatch.query.get(batch.id)

        context = api._prepare_invoice_context_legacy(invoice, batch)

        reimbursements = list(context["reimbursements_by_venue"])
        assert len(reimbursements) == 1
        assert reimbursements[0]["venue_name"] == "common name should not be empty"


class PrepareInvoiceContextTest:
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_context(self, invoice_data):
        bank_account, stocks, _venue = invoice_data
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        invoice = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )
        batch = models.CashflowBatch.query.get(batch.id)

        context = api._prepare_invoice_context(invoice, batch)

        general, books, not_reimbursed, custom = tuple(g for g in context["groups"])
        assert general.used_bookings_subtotal == 2006130
        assert general.contribution_subtotal == 406
        assert general.reimbursed_amount_subtotal == -2005724

        assert books.used_bookings_subtotal == 6000
        assert books.contribution_subtotal == 200
        assert books.reimbursed_amount_subtotal == -5800

        assert not_reimbursed.used_bookings_subtotal == 5800
        assert not_reimbursed.contribution_subtotal == 5800
        assert not_reimbursed.reimbursed_amount_subtotal == 0

        assert custom.used_bookings_subtotal == 4300
        assert custom.contribution_subtotal == 220
        assert custom.reimbursed_amount_subtotal == -4080

        assert context["invoice"] == invoice
        assert context["total_used_bookings_amount"] == 2022230
        assert context["total_contribution_amount"] == 6626
        assert context["total_reimbursed_amount"] == -2015604

    def test_get_invoice_period_second_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 31))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 16)
        assert end_period == datetime.date(2020, 3, 31)

    def test_get_invoice_period_first_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 15))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 1)
        assert end_period == datetime.date(2020, 3, 15)

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_common_name_is_not_empty_public_name(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            publicName="",
            name="common name should not be empty",
            siret="85331845900023",
            bookingEmail="pro@example.com",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )

        thing_offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=thing_offer, price=30)

        user = users_factories.RichBeneficiaryFactory()
        finance_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=stock,
            booking__user=user,
        )
        api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        invoice = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )
        batch = models.CashflowBatch.query.get(batch.id)

        context = api._prepare_invoice_context(invoice, batch)

        reimbursements = list(context["reimbursements_by_venue"])
        assert len(reimbursements) == 1
        assert reimbursements[0]["venue_name"] == "common name should not be empty"


class GenerateInvoiceHtmlLegacyTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, stocks, reimbursement_point, venue):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)

        duo_offer = offers_factories.OfferFactory(venue=venue, isDuo=True)
        duo_stock = offers_factories.StockFactory(offer=duo_offer, price=1)
        duo_booking = bookings_factories.UsedBookingFactory(stock=duo_stock, quantity=2)
        duo_finance_event = factories.UsedBookingFinanceEventFactory(booking=duo_booking)
        api.price_event(duo_finance_event)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        incident_collective_booking_event = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=30,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            pricingOrderingDate=datetime.datetime.utcnow(),
        )
        api.price_event(incident_collective_booking_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_collective_booking_event.pricings[0].status = models.PricingStatus.INVOICED

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking1_event.booking,
            newTotalAmount=0,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        # create collective total overpayment incident (30 €)
        collective_booking_total_incident = factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            collectiveBooking=incident_collective_booking_event.collectiveBooking,
            newTotalAmount=0,
        )
        incident_events += api._create_finance_events_from_incident(
            collective_booking_total_incident, datetime.datetime.utcnow()
        )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflows = models.Cashflow.query.order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=cashflow_ids,
        )

        batch = models.CashflowBatch.query.get(batch.id)
        invoice_html = api._generate_invoice_html_legacy(invoice, batch)
        expected_generated_file_name = "rendered_invoice_legacy.html"

        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_batch_label">1</td>',
            f'<td class="cashflow_batch_label">{cashflows[0].batch.label}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_creation_date">21/12/2021</td>',
            f'<td class="cashflow_creation_date">{invoice.date.strftime("%d/%m/%Y")}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°F220000001 du 30/01/2022";',
            f'content: "Relevé n°{invoice.reference} du {cashflows[0].batch.cutoff.strftime("%d/%m/%Y")}";',
        )
        start_period, end_period = api.get_invoice_period(cashflows[0].batch.cutoff)
        expected_invoice_html = expected_invoice_html.replace(
            "Remboursement des réservations validées entre le 01/01/22 et le 14/01/22, sauf cas exceptionnels.",
            f'Remboursement des réservations validées entre le {start_period.strftime("%d/%m/%y")} et le {end_period.strftime("%d/%m/%y")}, sauf cas exceptionnels.',
        )

        assert expected_invoice_html == invoice_html

    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics(self, invoice_data_legacy):
        reimbursement_point, stocks, venue = invoice_data_legacy
        pricing_point = offerers_models.Venue.query.get(venue.current_pricing_point_id)
        only_educational_venue = offerers_factories.VenueFactory(
            name="Coiffeur collecTIF",
            pricing_point=pricing_point,
            reimbursement_point=reimbursement_point,
        )
        only_collective_booking_finance_event = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=666,
            collectiveBooking__collectiveStock__collectiveOffer__venue=only_educational_venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=only_educational_venue,
        )
        collective_booking_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=5000,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        collective_booking_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=250,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        api.price_event(only_collective_booking_finance_event)
        api.price_event(collective_booking_finance_event1)
        api.price_event(collective_booking_finance_event2)

        self.generate_and_compare_invoice(stocks, reimbursement_point, venue)


class GenerateDebitNoteHtmlLegacyTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, reimbursement_point, venue):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED

        db.session.flush()

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=False,
            incident__venue=venue,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW

        cashflows = models.Cashflow.query.order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=cashflow_ids,
            is_debit_note=True,
        )
        batch = models.CashflowBatch.query.get(batch.id)
        invoice_html = api._generate_debit_note_html_legacy(invoice, batch)
        expected_generated_file_name = "rendered_debit_note_legacy.html"

        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html

        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°A240000001 du 26/01/2024";',
            f'content: "Relevé n°{invoice.reference} du {cashflows[0].batch.cutoff.strftime("%d/%m/%Y")}";',
        )
        assert expected_invoice_html == invoice_html

    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True)
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics(self, invoice_data_legacy):
        reimbursement_point, stock, venue = invoice_data_legacy

        del stock  # we don't need it

        self.generate_and_compare_invoice(reimbursement_point, venue)


class GenerateDebitNoteHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, bank_account, venue):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED

        db.session.flush()

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=False,
            incident__venue=venue,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW

        cashflows = models.Cashflow.query.order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
            is_debit_note=True,
        )
        batch = models.CashflowBatch.query.get(batch.id)
        invoice_html = api._generate_debit_note_html(invoice, batch)
        expected_generated_file_name = "rendered_debit_note.html"

        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html

        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°A240000001 du 26/01/2024";',
            f'content: "Relevé n°{invoice.reference} du {cashflows[0].batch.cutoff.strftime("%d/%m/%Y")}";',
        )
        assert expected_invoice_html == invoice_html

    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True)
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_basics(self, invoice_data):
        bank_account, stocks, venue = invoice_data

        del stocks  # we don't need it

        self.generate_and_compare_invoice(bank_account, venue)


class GenerateInvoiceHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, stocks, bank_account, venue):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)

        duo_offer = offers_factories.OfferFactory(venue=venue, isDuo=True)
        duo_stock = offers_factories.StockFactory(offer=duo_offer, price=1)
        duo_booking = bookings_factories.UsedBookingFactory(stock=duo_stock, quantity=2)
        duo_finance_event = factories.UsedBookingFinanceEventFactory(booking=duo_booking)
        api.price_event(duo_finance_event)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        incident_collective_booking_event = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=30,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            pricingOrderingDate=datetime.datetime.utcnow(),
        )
        api.price_event(incident_collective_booking_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_collective_booking_event.pricings[0].status = models.PricingStatus.INVOICED

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking1_event.booking,
            newTotalAmount=0,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        # create collective total overpayment incident (30 €)
        collective_booking_total_incident = factories.CollectiveBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            collectiveBooking=incident_collective_booking_event.collectiveBooking,
            newTotalAmount=0,
        )
        incident_events += api._create_finance_events_from_incident(
            collective_booking_total_incident, datetime.datetime.utcnow()
        )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflows = models.Cashflow.query.order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )

        batch = models.CashflowBatch.query.get(batch.id)
        invoice_html = api._generate_invoice_html(invoice, batch)
        expected_generated_file_name = "rendered_invoice.html"
        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()

        # We need to replace Cashflow IDs and dates that were used when generating the expected html
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_batch_label">1</td>',
            f'<td class="cashflow_batch_label">{cashflows[0].batch.label}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_creation_date">21/12/2021</td>',
            f'<td class="cashflow_creation_date">{invoice.date.strftime("%d/%m/%Y")}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°F220000001 du 30/01/2022";',
            f'content: "Relevé n°{invoice.reference} du {cashflows[0].batch.cutoff.strftime("%d/%m/%Y")}";',
        )
        start_period, end_period = api.get_invoice_period(cashflows[0].batch.cutoff)
        expected_invoice_html = expected_invoice_html.replace(
            "Remboursement des réservations validées entre le 01/01/22 et le 14/01/22, sauf cas exceptionnels.",
            f'Remboursement des réservations validées entre le {start_period.strftime("%d/%m/%y")} et le {end_period.strftime("%d/%m/%y")}, sauf cas exceptionnels.',
        )
        assert expected_invoice_html == invoice_html

    @override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_basics(self, invoice_data):
        bank_account, stocks, venue = invoice_data
        pricing_point = offerers_models.Venue.query.get(venue.current_pricing_point_id)
        only_educational_venue = offerers_factories.VenueFactory(
            name="Coiffeur collecTIF",
            pricing_point=pricing_point,
            bank_account=bank_account,
        )
        only_collective_booking_finance_event = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=666,
            collectiveBooking__collectiveStock__collectiveOffer__venue=only_educational_venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=only_educational_venue,
        )
        collective_booking_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=5000,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        collective_booking_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=250,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__beginningDatetime=datetime.datetime.utcnow()
            - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        api.price_event(only_collective_booking_finance_event)
        api.price_event(collective_booking_finance_event1)
        api.price_event(collective_booking_finance_event2)

        self.generate_and_compare_invoice(stocks, bank_account, venue)


class StoreInvoicePdfTest:
    STORAGE_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    INVOICES_DIR = STORAGE_DIR / "invoices"

    @override_settings(OBJECT_STORAGE_URL=STORAGE_DIR)
    def test_basics(self, clear_tests_invoices_bucket):
        invoice = factories.InvoiceFactory()
        html = "<p>Trust me, I am an invoice.<p>"
        existing_number_of_files = len(recursive_listdir(self.INVOICES_DIR))
        api._store_invoice_pdf(invoice.storage_object_id, html)

        assert invoice.url == f"{self.INVOICES_DIR}/{invoice.storage_object_id}"
        assert len(recursive_listdir(self.INVOICES_DIR)) == existing_number_of_files + 2
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}").exists()
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}.type").exists()


class GenerateAndStoreInvoiceTest:
    STORAGE_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"

    @override_settings(OBJECT_STORAGE_URL=STORAGE_DIR)
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_basics(self, clear_tests_invoices_bucket, css_font_http_request_mock):
        reimbursement_point = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point, iban="FR2710010000000000000000064")
        cashflow = factories.CashflowFactory(
            reimbursementPoint=reimbursement_point,
            status=models.CashflowStatus.UNDER_REVIEW,
        )

        # We're not interested in the invoice itself. We just want to
        # check that the function does not fail and that the email is
        # sent.
        api.generate_and_store_invoice_legacy(
            reimbursement_point_id=reimbursement_point.id,
            cashflow_ids=[cashflow.id],
        )

        assert len(mails_testing.outbox) == 1


@pytest.mark.parametrize("ff_activated", [True, False])
def test_we_cant_merge_batches_cashflow_from_both_bank_journey_from_target_batch(ff_activated):
    rp1, rp2, rp3, rp4 = [
        factories.BankInformationFactory(
            venue=offerers_factories.VenueFactory(),
        ).venue
        for i in range(4)
    ]

    venue = offerers_factories.VenueFactory()
    bank_account5 = factories.BankAccountFactory(offerer=venue.managingOfferer)

    batch1 = factories.CashflowBatchFactory(id=1)
    batch2 = factories.CashflowBatchFactory(id=2)
    batch3 = factories.CashflowBatchFactory(id=3)
    batch4 = factories.CashflowBatchFactory(id=4)
    batch5 = factories.CashflowBatchFactory(id=5)

    # Cashflow of batches 1 and 2: should not be changed.
    factories.CashflowFactory(batch=batch1, reimbursementPoint=rp1, amount=10)
    factories.CashflowFactory(batch=batch2, reimbursementPoint=rp1, amount=20)
    # Reimbursement point 1: batches 3, 4 and 5.
    factories.CashflowFactory(batch=batch3, reimbursementPoint=rp1, amount=40)
    factories.CashflowFactory(batch=batch4, reimbursementPoint=rp1, amount=80)
    factories.CashflowFactory(batch=batch5, reimbursementPoint=rp1, amount=160)
    # Reimbursement point 2: batches 3 and 4.
    cf_3_2 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp2, amount=320)
    factories.PricingFactory(cashflows=[cf_3_2])
    cf_4_2 = factories.CashflowFactory(batch=batch4, reimbursementPoint=rp2, amount=640)
    factories.PricingFactory(cashflows=[cf_4_2])
    # Reimbursement point 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp3, amount=1280)
    factories.PricingFactory(cashflows=[cf_3_3])
    cf_5_3 = factories.CashflowFactory(batch=batch5, reimbursementPoint=rp3, amount=2560)
    factories.PricingFactory(cashflows=[cf_5_3])
    # Reimbursement point 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp4, amount=5120)
    factories.PricingFactory(cashflows=[cf_3_4])
    # Reimbursement point 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, bankAccount=bank_account5, amount=10240)
    factories.PricingFactory(cashflows=[cf_5_5])

    with (
        override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=ff_activated),
        pytest.raises(AssertionError, match=r".*merge batches from both bank journeys.*"),
    ):
        api.merge_cashflow_batches(batches_to_remove=[batch3, batch4], target_batch=batch5)


@pytest.mark.parametrize("ff_activated", [True, False])
def test_we_cant_merge_batches_cashflow_from_both_bank_journey_from_batches_to_remove(ff_activated):
    rp1, rp4, rp5 = [
        factories.BankInformationFactory(
            venue=offerers_factories.VenueFactory(),
        ).venue
        for i in range(3)
    ]

    venue = offerers_factories.VenueFactory()
    bank_account2 = factories.BankAccountFactory(offerer=venue.managingOfferer)
    bank_account3 = factories.BankAccountFactory(offerer=venue.managingOfferer)

    batch1 = factories.CashflowBatchFactory(id=1)
    batch2 = factories.CashflowBatchFactory(id=2)
    batch3 = factories.CashflowBatchFactory(id=3)
    batch4 = factories.CashflowBatchFactory(id=4)
    batch5 = factories.CashflowBatchFactory(id=5)

    # Cashflow of batches 1 and 2: should not be changed.
    factories.CashflowFactory(batch=batch1, reimbursementPoint=rp1, amount=10)
    factories.CashflowFactory(batch=batch2, reimbursementPoint=rp1, amount=20)
    # Reimbursement point 1: batches 3, 4 and 5.
    factories.CashflowFactory(batch=batch3, reimbursementPoint=rp1, amount=40)
    factories.CashflowFactory(batch=batch4, reimbursementPoint=rp1, amount=80)
    factories.CashflowFactory(batch=batch5, reimbursementPoint=rp5, amount=160)
    # Reimbursement point 2: batches 3 and 4.
    cf_3_2 = factories.CashflowFactory(batch=batch3, bankAccount=bank_account2, amount=320)
    factories.PricingFactory(cashflows=[cf_3_2])
    cf_4_2 = factories.CashflowFactory(batch=batch4, bankAccount=bank_account2, amount=640)
    factories.PricingFactory(cashflows=[cf_4_2])
    # Reimbursement point 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, bankAccount=bank_account3, amount=1280)
    factories.PricingFactory(cashflows=[cf_3_3])
    cf_5_3 = factories.CashflowFactory(batch=batch5, bankAccount=bank_account3, amount=2560)
    factories.PricingFactory(cashflows=[cf_5_3])
    # Reimbursement point 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp4, amount=5120)
    factories.PricingFactory(cashflows=[cf_3_4])
    # Reimbursement point 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, reimbursementPoint=rp5, amount=10240)
    factories.PricingFactory(cashflows=[cf_5_5])

    with (
        override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=ff_activated),
        pytest.raises(AssertionError, match=r".*merge batches from both bank journeys.*"),
    ):
        api.merge_cashflow_batches(batches_to_remove=[batch3, batch4], target_batch=batch5)


@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
def test_merge_cashflow_batches_old_journey():
    rp1, rp2, rp3, rp4, rp5 = [
        factories.BankInformationFactory(
            venue=offerers_factories.VenueFactory(),
        ).venue
        for i in range(5)
    ]
    batch1 = factories.CashflowBatchFactory(id=1)
    batch2 = factories.CashflowBatchFactory(id=2)
    batch3 = factories.CashflowBatchFactory(id=3)
    batch4 = factories.CashflowBatchFactory(id=4)
    batch5 = factories.CashflowBatchFactory(id=5)

    # Cashflow of batches 1 and 2: should not be changed.
    factories.CashflowFactory(batch=batch1, reimbursementPoint=rp1, amount=10)
    factories.CashflowFactory(batch=batch2, reimbursementPoint=rp1, amount=20)
    # Reimbursement point 1: batches 3, 4 and 5.
    factories.CashflowFactory(batch=batch3, reimbursementPoint=rp1, amount=40)
    factories.CashflowFactory(batch=batch4, reimbursementPoint=rp1, amount=80)
    factories.CashflowFactory(batch=batch5, reimbursementPoint=rp1, amount=160)
    # Reimbursement point 2: batches 3 and 4.
    cf_3_2 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp2, amount=320)
    factories.PricingFactory(cashflows=[cf_3_2])
    cf_4_2 = factories.CashflowFactory(batch=batch4, reimbursementPoint=rp2, amount=640)
    factories.PricingFactory(cashflows=[cf_4_2])
    # Reimbursement point 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp3, amount=1280)
    factories.PricingFactory(cashflows=[cf_3_3])
    cf_5_3 = factories.CashflowFactory(batch=batch5, reimbursementPoint=rp3, amount=2560)
    factories.PricingFactory(cashflows=[cf_5_3])
    # Reimbursement point 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, reimbursementPoint=rp4, amount=5120)
    factories.PricingFactory(cashflows=[cf_3_4])
    # Reimbursement point 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, reimbursementPoint=rp5, amount=10240)
    factories.PricingFactory(cashflows=[cf_5_5])

    def get_cashflows(batch_id, reimbursement_point=None):
        query = models.Cashflow.query.filter_by(batchId=batch_id)
        if reimbursement_point:
            query = query.filter_by(reimbursementPoint=reimbursement_point)
        return query.all()

    api.merge_cashflow_batches(batches_to_remove=[batch3, batch4], target_batch=batch5)

    # No changes on batches 1 and 2.
    cashflows = get_cashflows(batch_id=1)
    assert len(cashflows) == 1
    assert cashflows[0].reimbursementPoint == rp1
    assert cashflows[0].amount == 10
    cashflows = get_cashflows(batch_id=2)
    assert len(cashflows) == 1
    assert cashflows[0].reimbursementPoint == rp1
    assert cashflows[0].amount == 20

    # Batches 3 and 4 have been deleted.
    assert not models.CashflowBatch.query.filter(models.CashflowBatch.id.in_((3, 4))).all()

    # Batch 5 now has all cashflows.
    assert len(get_cashflows(batch_id=5)) == 5
    assert get_cashflows(batch_id=5, reimbursement_point=rp1)[0].amount == 40 + 80 + 160
    assert get_cashflows(batch_id=5, reimbursement_point=rp2)[0].amount == 320 + 640
    assert get_cashflows(batch_id=5, reimbursement_point=rp3)[0].amount == 1280 + 2560
    assert get_cashflows(batch_id=5, reimbursement_point=rp4)[0].amount == 5120
    assert get_cashflows(batch_id=5, reimbursement_point=rp5)[0].amount == 10240


@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
def test_merge_cashflow_batches_new_journey():
    venue = offerers_factories.VenueFactory()

    (
        bank_account1,
        bank_account2,
        bank_account3,
        bank_account4,
        bank_account5,
    ) = factories.BankAccountFactory.create_batch(size=5, offerer=venue.managingOfferer)

    batch1 = factories.CashflowBatchFactory(id=1)
    batch2 = factories.CashflowBatchFactory(id=2)
    batch3 = factories.CashflowBatchFactory(id=3)
    batch4 = factories.CashflowBatchFactory(id=4)
    batch5 = factories.CashflowBatchFactory(id=5)

    # Cashflow of batches 1 and 2: should not be changed.
    factories.CashflowFactory(batch=batch1, bankAccount=bank_account1, amount=10)
    factories.CashflowFactory(batch=batch2, bankAccount=bank_account1, amount=20)
    # Reimbursement point 1: batches 3, 4 and 5.
    factories.CashflowFactory(batch=batch3, bankAccount=bank_account1, amount=40)
    factories.CashflowFactory(batch=batch4, bankAccount=bank_account1, amount=80)
    factories.CashflowFactory(batch=batch5, bankAccount=bank_account1, amount=160)
    # Reimbursement point 2: batches 3 and 4.
    cf_3_2 = factories.CashflowFactory(batch=batch3, bankAccount=bank_account2, amount=320)
    factories.PricingFactory(cashflows=[cf_3_2])
    cf_4_2 = factories.CashflowFactory(batch=batch4, bankAccount=bank_account2, amount=640)
    factories.PricingFactory(cashflows=[cf_4_2])
    # Reimbursement point 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, bankAccount=bank_account3, amount=1280)
    factories.PricingFactory(cashflows=[cf_3_3])
    cf_5_3 = factories.CashflowFactory(batch=batch5, bankAccount=bank_account3, amount=2560)
    factories.PricingFactory(cashflows=[cf_5_3])
    # Reimbursement point 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, bankAccount=bank_account4, amount=5120)
    factories.PricingFactory(cashflows=[cf_3_4])
    # Reimbursement point 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, bankAccount=bank_account5, amount=10240)
    factories.PricingFactory(cashflows=[cf_5_5])

    def get_cashflows(batch_id, bank_account=None):
        query = models.Cashflow.query.filter_by(batchId=batch_id)
        if bank_account:
            query = query.filter_by(bankAccount=bank_account)
        return query.all()

    api.merge_cashflow_batches(batches_to_remove=[batch3, batch4], target_batch=batch5)

    # No changes on batches 1 and 2.
    cashflows = get_cashflows(batch_id=1)
    assert len(cashflows) == 1
    assert cashflows[0].bankAccount == bank_account1
    assert cashflows[0].amount == 10
    cashflows = get_cashflows(batch_id=2)
    assert len(cashflows) == 1
    assert cashflows[0].bankAccount == bank_account1
    assert cashflows[0].amount == 20

    # Batches 3 and 4 have been deleted.
    assert not models.CashflowBatch.query.filter(models.CashflowBatch.id.in_((3, 4))).all()

    # Batch 5 now has all cashflows.
    assert len(get_cashflows(batch_id=5)) == 5
    assert get_cashflows(batch_id=5, bank_account=bank_account1)[0].amount == 40 + 80 + 160
    assert get_cashflows(batch_id=5, bank_account=bank_account2)[0].amount == 320 + 640
    assert get_cashflows(batch_id=5, bank_account=bank_account3)[0].amount == 1280 + 2560
    assert get_cashflows(batch_id=5, bank_account=bank_account4)[0].amount == 5120
    assert get_cashflows(batch_id=5, bank_account=bank_account5)[0].amount == 10240


def test_get_drive_folder_name():
    cutoff = datetime.datetime(2022, 4, 30, 22, 0)
    batch = factories.CashflowBatchFactory(cutoff=cutoff)
    name = api._get_drive_folder_name(batch)
    assert name == "2022-04 - jusqu'au 30 avril"


class CreateOffererReimbursementRuleTest:
    def test_create_rule(self):
        offerer = offerers_factories.OffererFactory()
        start = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=1))
        end = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=2))
        rule = api.create_offerer_reimbursement_rule(
            offerer.id, subcategories=["VOD"], rate=0.8, start_date=start, end_date=end
        )

        db.session.refresh(rule)
        assert rule.offerer == offerer
        assert rule.subcategories == ["VOD"]
        assert rule.rate == Decimal("0.8")
        assert rule.timespan.lower.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=1)
        ).strftime("%d/%m/%Y")
        assert rule.timespan.upper.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=2)
        ).strftime("%d/%m/%Y")

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        offerer = offerers_factories.OffererFactory()
        start = (datetime.datetime.today() + datetime.timedelta(days=1)).astimezone(pytz.utc)
        with pytest.raises(exceptions.UnknownSubcategoryForReimbursementRule):
            api.create_offerer_reimbursement_rule(offerer.id, subcategories=["UNKNOWN"], rate=0.8, start_date=start)


class CreateVenueReimbursementRuleTest:
    def test_create_rule(self):
        venue = offerers_factories.VenueFactory()
        start = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=1))
        end = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=2))
        rule = api.create_venue_reimbursement_rule(
            venue.id, subcategories=["VOD"], rate=0.8, start_date=start, end_date=end
        )

        db.session.refresh(rule)
        assert rule.venue == venue
        assert rule.subcategories == ["VOD"]
        assert rule.rate == Decimal("0.8")
        assert rule.timespan.lower.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=1)
        ).strftime("%d/%m/%Y")
        assert rule.timespan.upper.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=2)
        ).strftime("%d/%m/%Y")

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        venue = offerers_factories.VenueFactory()
        start = (datetime.datetime.today() + datetime.timedelta(days=1)).astimezone(pytz.utc)
        with pytest.raises(exceptions.UnknownSubcategoryForReimbursementRule):
            api.create_venue_reimbursement_rule(venue.id, subcategories=["UNKNOWN"], rate=0.8, start_date=start)


class CreateOfferReimbursementRuleTest:
    def test_create_rule(self):
        offer = offers_factories.OfferFactory()
        start = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=1))
        end = pytz.utc.localize(datetime.datetime.today() + datetime.timedelta(days=2))
        rule = api.create_offer_reimbursement_rule(offer.id, amount=12.34, start_date=start, end_date=end)

        db.session.refresh(rule)
        assert rule.offer == offer
        assert rule.amount == 1234
        assert rule.timespan.lower.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=1)
        ).strftime("%d/%m/%Y")
        assert rule.timespan.upper.strftime("%d/%m/%Y") == (
            datetime.datetime.today() + datetime.timedelta(days=2)
        ).strftime("%d/%m/%Y")

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        offer = offers_factories.OfferFactory()
        start = (datetime.datetime.today() + datetime.timedelta(days=1)).astimezone(pytz.utc)
        factories.CustomReimbursementRuleFactory(offer=offer, timespan=(start, None))
        with pytest.raises(exceptions.ConflictingReimbursementRule):
            api.create_offer_reimbursement_rule(offer.id, amount=12.34, start_date=start)


class EditReimbursementRuleTest:
    def test_edit_rule(self):
        today = datetime.date.today()
        timespan = (pytz.utc.localize(datetime.datetime(today.year + 1, 1, 1)), None)
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        end = pytz.utc.localize(datetime.datetime(today.year + 2, 10, 3, 0, 0))
        api.edit_reimbursement_rule(rule, end_date=end)

        db.session.refresh(rule)
        assert rule.timespan.lower == datetime.datetime(today.year + 1, 1, 1, 0, 0)  # unchanged
        assert rule.timespan.upper == datetime.datetime(today.year + 2, 10, 3, 0, 0)

    def test_cannot_change_existing_end_date(self):
        today = datetime.datetime.today()
        timespan = (today - datetime.timedelta(days=10), today)
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            api.edit_reimbursement_rule(rule, end_date=today + datetime.timedelta(days=5))

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        timespan = (datetime.datetime.today() - datetime.timedelta(days=10), None)
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        end = pytz.utc.localize(datetime.datetime.today())
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            api.edit_reimbursement_rule(rule, end_date=end)


class CreateDepositTest:
    @time_machine.travel("2021-02-05 09:00:00")
    @pytest.mark.parametrize("age,expected_amount", [(15, Decimal(20)), (16, Decimal(30)), (17, Decimal(30))])
    def test_create_underage_deposit(self, age, expected_amount):
        with time_machine.travel(
            datetime.datetime.combine(datetime.datetime.utcnow(), datetime.time(0, 0))
            - relativedelta(years=age, months=2)
        ):
            beneficiary = users_factories.UserFactory(validatedBirthDate=datetime.datetime.utcnow())
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(month=1)):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.OK,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(
                    registration_datetime=datetime.datetime.utcnow()
                ),
            )

        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility, age_at_registration=age)

        assert deposit.type == models.DepositType.GRANT_15_17
        assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime.datetime(2021 - (age + 1) + 18, 12, 5, 0, 0, 0)

    @time_machine.travel("2021-02-05 09:00:00")
    @pytest.mark.parametrize("age, expected_amount", [(15, Decimal(50)), (16, Decimal(60)), (17, Decimal(300))])
    def test_create_underage_deposit_and_recredit_after_validation(self, age, expected_amount):
        with time_machine.travel(
            datetime.datetime.combine(datetime.datetime.utcnow(), datetime.time(0, 0))
            - relativedelta(years=age + 1, months=1)  # 16 (or 17) years and 1 month ago, user was born
        ):
            beneficiary = users_factories.UserFactory(validatedBirthDate=datetime.datetime.utcnow())

        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(months=2)):
            # User starts registration at 15 (or 16) years and 11 months old
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.STARTED,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(
                    registration_datetime=datetime.datetime.utcnow()
                ),
            )

        # Registration is completed 2 months later, when user is 16 (or 17) years and 1 months old
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=beneficiary,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )

        # Deposit is created right after the validation of the registration
        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility, age_at_registration=age)

        if age < 16:
            assert deposit.type == models.DepositType.GRANT_15_17
            assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id

    @time_machine.travel("2021-02-05 09:00:00")
    @pytest.mark.parametrize("age, expected_amount", [(15, Decimal(80))])
    def test_create_underage_deposit_and_recredit_sum_of_15_17(self, age, expected_amount):
        with time_machine.travel(
            datetime.datetime.combine(datetime.datetime.utcnow(), datetime.time(0, 0))
            - relativedelta(years=age + 2, months=1)  # 17 years and 1 month ago, user was born
        ):
            beneficiary = users_factories.UserFactory(validatedBirthDate=datetime.datetime.utcnow())

        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=1, months=2)):
            # User starts registration at 15 years and 11 months old
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.STARTED,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(
                    registration_datetime=datetime.datetime.utcnow()
                ),
            )

        # Registration is completed 2 months later, when user is 16 (or 17) years and 1 months old
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=beneficiary,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )

        # Deposit is created right after the validation of the registration
        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility, age_at_registration=age)

        if age < 16:
            assert deposit.type == models.DepositType.GRANT_15_17
            assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id

    @time_machine.travel("2022-09-05 09:00:00")
    def test_create_18_years_old_deposit(self):
        beneficiary = users_factories.UserFactory()

        deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        # We use time_machine to ensure this test is not flaky. Otherwise, the expiration date would be dependant on the daylight saving time.
        assert deposit.expirationDate == datetime.datetime(2024, 9, 5, 23, 59, 59, 999999)

    def test_tahiti_grant_18_expiration_is_2_years_after_at_EOD(self):
        tahiti_tz = datetime.timezone(datetime.timedelta(hours=-10))
        tahiti_datetime = datetime.datetime(2023, 5, 29, tzinfo=tahiti_tz)
        with time_machine.travel(tahiti_datetime.replace(hour=0, minute=0, second=0)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(tahiti_datetime.replace(hour=23, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 30, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(tahiti_datetime.replace(hour=13, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(tahiti_datetime.replace(hour=14, minute=0, second=0)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 30, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )

    def test_wallis_grant_18_expiration_is_2_years_after_at_EOD(self):
        wallis_tz = datetime.timezone(datetime.timedelta(hours=12))
        wallis_datetime = datetime.datetime(2023, 5, 29, tzinfo=wallis_tz)
        with time_machine.travel(wallis_datetime.replace(hour=0, minute=0, second=0)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 28, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(wallis_datetime.replace(hour=23, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(wallis_datetime.replace(hour=11, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 28, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(wallis_datetime.replace(hour=12, minute=00, second=00)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )

    def test_metropole_grant_18_expiration_is_2_years_after_at_EOD(self):
        metropole_tz = datetime.timezone(datetime.timedelta(hours=1))
        metropole_datetime = datetime.datetime(2023, 5, 29, tzinfo=metropole_tz)
        with time_machine.travel(metropole_datetime.replace(hour=0, minute=0, second=0)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 28, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(metropole_datetime.replace(hour=23, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(metropole_datetime.replace(hour=0, minute=59, second=59)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 28, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )
        with time_machine.travel(metropole_datetime.replace(hour=1, minute=0, second=0)):
            beneficiary = users_factories.UserFactory()
            deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)
        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.expirationDate == datetime.datetime(2025, 5, 29, 23, 59, 59, 999999, tzinfo=pytz.utc).replace(
            tzinfo=None
        )

    def test_deposit_created_when_another_type_already_exist_for_user(self):
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=3)):
            beneficiary = users_factories.UnderageBeneficiaryFactory()

        api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert beneficiary.deposit.type == models.DepositType.GRANT_18
        assert len(beneficiary.deposits) == 2

    def test_cannot_create_twice_a_deposit_of_same_type(self):
        # Given
        AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(years=18, months=2)
        beneficiary = users_factories.BeneficiaryGrant18Factory(validatedBirthDate=AGE18_ELIGIBLE_BIRTH_DATE)

        # When
        with pytest.raises(exceptions.DepositTypeAlreadyGrantedException) as error:
            api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        # Then
        assert models.Deposit.query.filter(models.Deposit.userId == beneficiary.id).count() == 1
        assert error.value.errors["user"] == ['Cet utilisateur a déjà été crédité de la subvention "GRANT_18".']


class UserRecreditTest:
    @time_machine.travel("2021-07-01")
    @pytest.mark.parametrize(
        "birth_date,registration_datetime,expected_result",
        [
            ("2006-01-01", datetime.datetime(2021, 5, 1), False),
            ("2005-01-01", datetime.datetime(2020, 5, 1), True),
            ("2005-07-01", datetime.datetime(2021, 5, 1), True),
        ],
    )
    def test_has_celebrated_birthday_since_credit_or_registration(
        self, birth_date, registration_datetime, expected_result
    ):
        user = users_factories.BeneficiaryGrant18Factory(
            dateOfBirth=birth_date,
        )
        fraud_check_result_content = fraud_factories.UbbleContentFactory(registration_datetime=registration_datetime)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            resultContent=fraud_check_result_content,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=registration_datetime,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert api._has_celebrated_birthday_since_credit_or_registration(user) == expected_result

    def test_can_be_recredited(self):
        with time_machine.travel("2020-05-02"):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=15, dateOfBirth=datetime.date(2005, 5, 1)
            )

            # User turned 15. They are credited a first time
            content = fraud_factories.UbbleContentFactory(
                user=user, birth_date="2005-05-01", registration_datetime=datetime.datetime.utcnow()
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=content,
                dateCreated=datetime.datetime(2020, 5, 1),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            assert user.deposit.recredits == []
            assert api._can_be_recredited(user) is False

        with time_machine.travel("2021-05-02"):
            # User turned 16. They can be recredited
            assert api._can_be_recredited(user) is True

            api.recredit_underage_users()
            assert user.deposit.amount == 50
            assert user.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_16
            assert user.recreditAmountToShow == 30
            assert api._can_be_recredited(user) is False

        with time_machine.travel("2022-05-02"):
            # User turned 17. They can be recredited
            assert api._can_be_recredited(user) is True

            api.recredit_underage_users()
            assert user.deposit.amount == 80
            assert user.deposit.recredits[1].recreditType == models.RecreditType.RECREDIT_17
            assert user.recreditAmountToShow == 30
            assert api._can_be_recredited(user) is False

    def test_can_be_recredited_no_registration_datetime(self):
        with time_machine.travel("2020-05-02"):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=15, dateOfBirth=datetime.date(2005, 5, 1)
            )
            # I voluntarily don't use the EduconnectContentFactory to be allowed to omit registration_datetime
            content = {
                "birth_date": "2020-05-02",
                "educonnect_id": "educonnect_id",
                "first_name": "first_name",
                "ine_hash": "ine_hash",
                "last_name": "last_name",
                "school_uai": "school_uai",
                "student_level": "student_level",
            }
            fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent={},
                dateCreated=datetime.datetime(2020, 5, 1),  # first fraud check created
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_check.resultContent = content
        with time_machine.travel("2022-05-02"):
            assert api._can_be_recredited(user) is True

    def test_can_be_recredited_no_identity_fraud_check(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.date(2005, 5, 1))
        with time_machine.travel("2020-05-02"):
            assert api._can_be_recredited(user) is False

    @mock.patch("pcapi.core.finance.api._has_been_recredited")
    def should_not_check_recredits_on_age_18(self, mock_has_been_recredited):
        user = users_factories.BeneficiaryFactory(age=18)
        assert api._can_be_recredited(user) is False
        assert mock_has_been_recredited.call_count == 0

    @pytest.mark.parametrize(
        "user_age,user_recredits,expected_result",
        [
            (15, [], False),
            (16, [], False),
            (17, [], False),
            (
                16,
                [{"type": models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2020, 1, 1)}],
                True,
            ),
            (
                17,
                [{"type": models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2020, 1, 1)}],
                False,
            ),
            (
                17,
                [
                    {"type": models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2019, 1, 1)},
                    {"type": models.RecreditType.RECREDIT_17, "date_created": datetime.datetime(2020, 1, 1)},
                ],
                True,
            ),
            (
                17,
                [{"type": models.RecreditType.RECREDIT_17, "date_created": datetime.datetime(2020, 1, 1)}],
                True,
            ),
        ],
    )
    def test_has_been_recredited(self, user_age, user_recredits, expected_result):
        if 15 <= user_age <= 17:
            user = users_factories.UnderageBeneficiaryFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=user_age)
            )
        elif user_age == 18:
            user = users_factories.BeneficiaryGrant18Factory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=user_age)
            )

        for recredit in user_recredits:
            factories.RecreditFactory(
                deposit=user.deposit, recreditType=recredit["type"], dateCreated=recredit["date_created"]
            )
        assert api._has_been_recredited(user) == expected_result

    def test_has_been_recredited_logs_error_if_no_age(self, caplog):
        user = users_factories.BaseUserFactory(dateOfBirth=None)
        assert user.age is None

        with caplog.at_level(logging.ERROR):
            assert api._has_been_recredited(user) is False
            assert caplog.records[0].extra["user_id"] == user.id

    def test_recredit_underage_users(self):
        # This test aims to check all the possible use cases for recredit_underage_users
        # We create users with different ages (15, 16, 17) with different stages of activation
        # Each user that is credited is supposed to have the corresponding fraud_checks.
        # - We create the fraud_checks manually to override the registration_datetime

        with time_machine.travel("2020-01-01"):
            # Create users, with their fraud checks

            # Already beneficiary users
            user_15 = users_factories.UnderageBeneficiaryFactory(subscription_age=15)
            user_16_not_recredited = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_16_already_recredited = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_17_not_recredited = users_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_only_recredited_at_16 = users_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_already_recredited = users_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_already_recredited_twice = users_factories.UnderageBeneficiaryFactory(subscription_age=17)

            id_check_application_date = datetime.datetime(2019, 7, 31)  # Asked for credit before birthday
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_15,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_15, birth_date="2004-08-01", registration_datetime=id_check_application_date
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_16_not_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_16_not_recredited,
                    birth_date="2003-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_16_already_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_16_already_recredited,
                    birth_date="2003-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_not_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_not_recredited,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_only_recredited_at_16,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_only_recredited_at_16,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_already_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_already_recredited,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_already_recredited_twice,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_already_recredited_twice,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Not beneficiary user
            user_17_not_activated = users_factories.UserFactory(dateOfBirth=datetime.datetime(2004, 5, 1))
            user_17_not_activated.add_underage_beneficiary_role()

            # Create the recredits that already happened
            factories.RecreditFactory(
                deposit=user_16_already_recredited.deposit, recreditType=models.RecreditType.RECREDIT_16
            )
            factories.RecreditFactory(
                deposit=user_17_only_recredited_at_16.deposit,
                recreditType=models.RecreditType.RECREDIT_16,
                dateCreated=datetime.datetime(2020, 1, 1),
            )
            factories.RecreditFactory(
                deposit=user_17_already_recredited.deposit, recreditType=models.RecreditType.RECREDIT_17
            )
            factories.RecreditFactory(
                deposit=user_17_already_recredited_twice.deposit,
                recreditType=models.RecreditType.RECREDIT_16,
                dateCreated=datetime.datetime(2019, 5, 1),
            )
            factories.RecreditFactory(
                deposit=user_17_already_recredited_twice.deposit,
                recreditType=models.RecreditType.RECREDIT_17,
                dateCreated=datetime.datetime(2020, 5, 1),
            )

        # Check the initial conditions
        assert models.Recredit.query.count() == 5

        assert user_17_not_activated.deposit is None

        assert user_15.deposit.amount == 20
        assert user_16_not_recredited.deposit.amount == 30
        assert user_16_already_recredited.deposit.amount == 30
        assert user_17_not_recredited.deposit.amount == 30
        assert user_17_only_recredited_at_16.deposit.amount == 30
        assert user_17_already_recredited.deposit.amount == 30
        assert user_17_already_recredited_twice.deposit.amount == 30

        assert user_15.recreditAmountToShow is None
        assert user_16_not_recredited.recreditAmountToShow is None
        assert user_16_already_recredited.recreditAmountToShow is None
        assert user_17_not_recredited.recreditAmountToShow is None
        assert user_17_only_recredited_at_16.recreditAmountToShow is None
        assert user_17_already_recredited.recreditAmountToShow is None
        assert user_17_already_recredited_twice.recreditAmountToShow is None

        # Run the task
        with time_machine.travel("2020, 5, 2"):
            api.recredit_underage_users()

        # Check the results:
        # Assert we created new Recredits for user_16_not_recredited, user_17_not_recredited and user_17_only_recredited_at_16
        assert models.Recredit.query.count() == 8
        assert user_15.deposit.recredits == []
        assert user_16_not_recredited.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_16
        assert user_17_not_recredited.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_17
        assert len(user_17_only_recredited_at_16.deposit.recredits) == 2
        assert user_17_only_recredited_at_16.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_17

        assert user_15.deposit.amount == 20
        assert user_16_not_recredited.deposit.amount == 30 + 30
        assert user_16_already_recredited.deposit.amount == 30
        assert user_17_not_recredited.deposit.amount == 30 + 30
        assert user_17_only_recredited_at_16.deposit.amount == 30 + 30
        assert user_17_already_recredited.deposit.amount == 30
        assert user_17_already_recredited_twice.deposit.amount == 30

        assert user_15.recreditAmountToShow is None
        assert user_16_not_recredited.recreditAmountToShow == 30
        assert user_16_already_recredited.recreditAmountToShow is None
        assert user_17_not_recredited.recreditAmountToShow == 30
        assert user_17_only_recredited_at_16.recreditAmountToShow == 30
        assert user_17_already_recredited.recreditAmountToShow is None
        assert user_17_already_recredited_twice.recreditAmountToShow is None

    def test_recredit_around_the_year(self):
        with time_machine.travel("2015-05-01"):
            user_activated_at_15 = users_factories.UnderageBeneficiaryFactory(subscription_age=15)
            user_activated_at_16 = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_activated_at_17 = users_factories.UnderageBeneficiaryFactory(subscription_age=17)

        assert user_activated_at_15.deposit.amount == 20
        assert user_activated_at_16.deposit.amount == 30
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow is None
        assert user_activated_at_16.recreditAmountToShow is None
        assert user_activated_at_17.recreditAmountToShow is None

        # recredit the following year
        with time_machine.travel("2016-05-01"):
            api.recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 50
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30
        assert user_activated_at_17.recreditAmountToShow is None

        # recrediting the day after does not affect the amount
        with time_machine.travel("2016-05-02"):
            api.recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 50
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30
        assert user_activated_at_17.recreditAmountToShow is None

        # recredit the following year
        with time_machine.travel("2017-05-01"):
            api.recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 80
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30  # Was not reset
        assert user_activated_at_17.recreditAmountToShow is None

    def test_recredit_when_account_activated_on_the_birthday(self):
        with time_machine.travel("2020-05-01"):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=16, dateOfBirth=datetime.date(2004, 5, 1)
            )
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None

            # Should not recredit if the account was created the same day as the birthday
            api.recredit_underage_users()
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None


class ValidateFinanceIncidentTest:
    def test_educational_institution_is_recredited(self):
        deposit = educational_factories.EducationalDepositFactory(amount=Decimal(1000.00), isFinal=True)
        booking = educational_factories.ReimbursedCollectiveBookingFactory(
            collectiveStock__price=Decimal(500.00),
            educationalInstitution=deposit.educationalInstitution,
            educationalYearId=deposit.educationalYearId,
        )

        collective_booking_finance_incident = factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=booking
        )

        # before recredit
        with pytest.raises(educational_exceptions.InsufficientFund):
            check_institution_fund(
                booking.educationalInstitution.id, booking.educationalYearId, Decimal(7800.00), deposit
            )

        api.validate_finance_incident(collective_booking_finance_incident.incident, force_debit_note=False)

        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

        # after recredit, it does not raise InsufficientFund
        check_institution_fund(booking.educationalInstitution.id, booking.educationalYearId, Decimal(700.00), deposit)
