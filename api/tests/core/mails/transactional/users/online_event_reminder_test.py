import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users import online_event_reminder
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import testing as users_testing


pytestmark = pytest.mark.usefixtures("db_session")


class OnlineEventReminderTest:
    def test_get_online_events_happening_tomorrow(self) -> None:
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        two_days_from_now = now + datetime.timedelta(days=2)

        digital_event_offer = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        # Event happening tomorrow
        offers_factories.EventStockFactory(beginningDatetime=tomorrow, offer=digital_event_offer)
        # Event happening today
        offers_factories.EventStockFactory(beginningDatetime=now, offer=digital_event_offer)
        # Event happening in 2 days
        offers_factories.EventStockFactory(beginningDatetime=two_days_from_now, offer=digital_event_offer)

        # All events are booked
        bookings_factories.BookingFactory(stock=digital_event_offer.stocks[0])
        bookings_factories.BookingFactory(stock=digital_event_offer.stocks[1])
        bookings_factories.BookingFactory(stock=digital_event_offer.stocks[2])

        query = online_event_reminder._get_online_events_happening_tomorrow()

        assert query.count() == 1
        assert query.one().stock.beginningDatetime == tomorrow

    def test_get_email_data_by_stock(self):
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_and_two_hours = now + datetime.timedelta(days=1, hours=2)

        online_conference_offer = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        online_meetup = offers_factories.EventOfferFactory(
            url="http://example.com/offer/2", subcategoryId=subcategories.RENCONTRE.id
        )

        # The online conference and the online meetup are happening tomorrow at different hours
        online_conference_stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow, offer=online_conference_offer
        )
        online_meetup_stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow_and_two_hours, offer=online_meetup
        )

        # All events are booked multiple times
        bookings_factories.BookingFactory(stock=online_conference_offer.stocks[0])
        bookings_factories.BookingFactory(stock=online_conference_offer.stocks[0])

        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])
        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])
        bookings_factories.BookingFactory(stock=online_meetup.stocks[0])

        query = online_event_reminder._get_online_events_happening_tomorrow()  # tested above
        email_data_by_stocks = online_event_reminder._get_email_data_by_stock(query)

        assert len(email_data_by_stocks) == 2

        online_conference_data = email_data_by_stocks[online_conference_stock.id]
        assert online_conference_data.offer_name == online_conference_offer.name
        assert online_conference_data.offer_url == online_conference_offer.url
        assert online_conference_data.event_hour == tomorrow
        assert online_conference_data.withdrawal_details == online_conference_offer.withdrawalDetails
        assert len(online_conference_data.recipients) == 2

        online_meetup_data = email_data_by_stocks[online_meetup_stock.id]
        assert online_meetup_data.offer_name == online_meetup.name
        assert online_meetup_data.offer_url == online_meetup.url
        assert online_meetup_data.event_hour == tomorrow_and_two_hours
        assert online_meetup_data.withdrawal_details == online_meetup.withdrawalDetails
        assert len(online_meetup_data.recipients) == 3

    def test_send_email_by_stock(self):
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=-4)
        digital_event_offer = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow, offer=digital_event_offer)
        bookings_factories.BookingFactory(stock=stock)
        online_event_reminder.send_online_event_event_reminder_by_offer()
        assert len(mails_testing.outbox) == 1

        assert mails_testing.outbox[0]["scheduled_at"] == stock.beginningDatetime - datetime.timedelta(minutes=30)

    def test_cancel_online_event_reminder_when_no_reminder_scheduled(self):
        digital_event_offer = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        stock = offers_factories.EventStockFactory(offer=digital_event_offer)
        booking = bookings_factories.BookingFactory(stock=stock)
        online_event_reminder.cancel_online_event_reminder(booking_id=booking.id)
        assert len(users_testing.sendinblue_requests) == 0

    def test_cancel_online_event_reminder_when_reminders_scheduled(self):
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        digital_event_offer = offers_factories.EventOfferFactory(
            url="http://example.com/offer/1", subcategoryId=subcategories.CONFERENCE.id
        )
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow, offer=digital_event_offer)
        booking = bookings_factories.BookingFactory(stock=stock)
        online_event_reminder.send_online_event_event_reminder_by_offer()

        online_event_reminder.cancel_online_event_reminder(booking_id=booking.id)

        assert len(users_testing.sendinblue_requests) == 1
