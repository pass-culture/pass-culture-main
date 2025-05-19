import datetime

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.mails.transactional.users import online_event_reminder
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.utils.date import utc_datetime_to_department_timezone


pytestmark = pytest.mark.usefixtures("db_session")


class OnlineEventReminderTest:
    def setup_method(self):
        now = datetime.datetime.utcnow()
        normalized_minute = 0 if now.minute < 30 else 30

        self.now = now.replace(minute=normalized_minute, second=0, microsecond=0)
        self.in_20_minutes = self.now + datetime.timedelta(minutes=20)
        self.in_35_minutes = self.now + datetime.timedelta(minutes=35)
        self.in_50_minutes = self.now + datetime.timedelta(minutes=50)
        self.in_2_hours = self.now + datetime.timedelta(hours=2)

    def test_get_online_bookings_happening_soon(self) -> None:
        online_conference = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        # Event happening in less than 1 hour
        stock_50m = offers_factories.EventStockFactory(beginningDatetime=self.in_50_minutes, offer=online_conference)
        # Event happening in less than 30 minutes
        stock_20m = offers_factories.EventStockFactory(beginningDatetime=self.in_20_minutes, offer=online_conference)
        # Event happening in more than 1 hour
        stock_2h = offers_factories.EventStockFactory(beginningDatetime=self.in_2_hours, offer=online_conference)

        # All events are booked
        bookings_factories.BookingFactory(stock=stock_50m)
        bookings_factories.BookingFactory(stock=stock_20m)
        bookings_factories.BookingFactory(stock=stock_2h)

        query = online_event_reminder._get_online_bookings_happening_soon()

        assert query.count() == 1
        assert query.one().stock.beginningDatetime == self.in_50_minutes

    def test_get_email_data_by_stock(self):
        online_conference = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        online_meetup = offers_factories.EventOfferFactory(
            url="http://example.com/offer/2", subcategoryId=subcategories.RENCONTRE.id
        )
        # The online conference and the online meetup are happening soon at different times
        online_conference_stock = offers_factories.EventStockFactory(
            beginningDatetime=self.in_50_minutes, offer=online_conference
        )
        online_meetup_stock = offers_factories.EventStockFactory(
            beginningDatetime=self.in_35_minutes, offer=online_meetup
        )

        # All events are booked multiple times
        bookings_factories.BookingFactory(stock=online_conference.stocks[0])
        bookings_factories.BookingFactory(stock=online_conference.stocks[0])

        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])
        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])
        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])

        with assert_no_duplicated_queries():
            query = online_event_reminder._get_online_bookings_happening_soon()  # tested above
            email_data_by_stocks = online_event_reminder._get_email_data_by_stock(query)

        assert len(email_data_by_stocks) == 2

        online_conference_data = email_data_by_stocks[online_conference_stock.id]
        expected_event_hour = utc_datetime_to_department_timezone(
            self.in_50_minutes, online_conference.venue.departementCode
        )
        assert online_conference_data.offer_name == online_conference.name
        assert online_conference_data.offer_url == online_conference.url
        assert online_conference_data.event_hour == expected_event_hour
        assert online_conference_data.withdrawal_details == online_conference.withdrawalDetails
        assert len(online_conference_data.recipients) == 2

        online_meetup_data = email_data_by_stocks[online_meetup_stock.id]
        expected_event_hour = utc_datetime_to_department_timezone(
            self.in_35_minutes, online_meetup.venue.departementCode
        )
        assert online_meetup_data.offer_name == online_meetup.name
        assert online_meetup_data.offer_url == online_meetup.url
        assert online_meetup_data.event_hour == expected_event_hour
        assert online_meetup_data.withdrawal_details == online_meetup.withdrawalDetails
        assert len(online_meetup_data.recipients) == 3

    def test_send_reminder_email(self):
        online_conference = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        stock = offers_factories.EventStockFactory(beginningDatetime=self.in_50_minutes, offer=online_conference)
        bookings_factories.BookingFactory(stock=stock)
        online_event_reminder.send_online_event_event_reminder()
        assert len(mails_testing.outbox) == 1

        expected_event_hour = utc_datetime_to_department_timezone(
            self.in_50_minutes, online_conference.venue.departementCode
        )

        assert mails_testing.outbox[0]["params"] == {
            "DIGITAL_OFFER_URL": online_conference.url,
            "EVENT_HOUR": expected_event_hour.strftime("%Hh%M"),
            "OFFER_NAME": online_conference.name,
            "OFFER_WITHDRAWAL_DETAILS": online_conference.withdrawalDetails,
        }

    def test_do_not_send_reminder_email_if_booking_cancelled(self):
        online_conference = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        stock = offers_factories.EventStockFactory(beginningDatetime=self.in_50_minutes, offer=online_conference)
        bookings_factories.BookingFactory(stock=stock, status=bookings_models.BookingStatus.CANCELLED)
        online_event_reminder.send_online_event_event_reminder()
        assert len(mails_testing.outbox) == 0
