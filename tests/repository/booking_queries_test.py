from datetime import datetime, timedelta

import pytest

from models import PcObject, ThingType, Booking, EventType
from models.api_errors import ResourceNotFoundError, ApiErrors
from repository import booking_queries
from tests.conftest import clean_database
from tests.model_creators.activity_creators import create_booking_activity, save_all_activities
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit, create_payment, create_recommendation
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_from_offer, \
    create_stock_with_thing_offer, create_offer_with_thing_product, create_offer_with_event_product

NOW = datetime.utcnow()
two_days_ago = NOW - timedelta(days=2)
four_days_ago = NOW - timedelta(days=4)
five_days_ago = NOW - timedelta(days=5)
three_days_ago = NOW - timedelta(days=3)


class FindAllOffererBookingsByVenueIdTest:
    @clean_database
    def test_in_a_not_search_context_returns_all_results(self, app):
        # given
        user = create_user()
        offerer1 = create_offerer(siren='123456789')
        offerer2 = create_offerer(siren='987654321')
        venue1 = create_venue(offerer1, siret=offerer1.siren + '12345')
        venue2 = create_venue(offerer1, siret=offerer1.siren + '54321')
        venue3 = create_venue(offerer2, siret=offerer2.siren + '12345')
        stock1 = create_stock_with_event_offer(
            offerer1, venue1, price=0, available=100)
        stock2 = create_stock_with_thing_offer(
            offerer1, venue2, price=0, available=100)
        stock3 = create_stock_with_thing_offer(
            offerer2, venue3, price=0, available=100)
        booking1 = create_booking(user=user, stock=stock1, venue=venue1, quantity=2, recommendation=None)
        booking2 = create_booking(user=user, stock=stock2, venue=venue2, quantity=2, recommendation=None)
        booking3 = create_booking(user=user, stock=stock3, venue=venue3, quantity=2, recommendation=None)

        PcObject.save(booking1, booking2, booking3)

        # when
        bookings = booking_queries.find_offerer_bookings(offerer1.id)

        # then
        assert len(bookings) == 2

    @clean_database
    def test_returns_bookings_on_given_venue(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)
        offerer1 = create_offerer(siren='123456789')
        offerer2 = create_offerer(siren='987654321')
        venue1 = create_venue(offerer1, siret=offerer1.siren + '12345')
        venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
        offer1 = create_offer_with_event_product(venue1)
        offer2 = create_offer_with_thing_product(venue1)
        offer3 = create_offer_with_thing_product(venue2)
        stock1 = create_stock_from_offer(offer1, available=100, price=20)
        stock2 = create_stock_from_offer(offer2, available=150, price=16)
        stock3 = create_stock_from_offer(offer3, available=150, price=16)
        booking1 = create_booking(user=user, stock=stock1, venue=venue1, quantity=2, recommendation=None)
        booking2 = create_booking(user=user, stock=stock2, venue=venue1, quantity=2, recommendation=None)
        booking3 = create_booking(user=user, stock=stock3, venue=venue2, quantity=2, recommendation=None)
        PcObject.save(booking1, booking2, booking3)

        # when
        bookings = booking_queries.find_offerer_bookings(offerer1.id, venue_id=venue1.id)

        # then
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    @clean_database
    def test_returns_bookings_on_given_venue_and_thing_offer_and_date(self, app):
        # given
        user = create_user()
        create_deposit(user=user, amount=1600)
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer=offerer, siret=offerer.siren + '12345')
        target_offer = create_offer_with_thing_product(venue)
        other_offer = create_offer_with_thing_product(venue)
        target_stock = create_stock_from_offer(target_offer, available=100, price=20)
        other_stock = create_stock_from_offer(other_offer, available=150, price=16)
        other_booking_1 = create_booking(user=user,
                                         stock=target_stock,
                                         venue=venue,
                                         quantity=2,
                                         recommendation=None,
                                         date_created=datetime(2020, 5, 30))
        target_booking_1 = create_booking(user=user,
                                          stock=target_stock,
                                          venue=venue,
                                          quantity=2,
                                          recommendation=None,
                                          date_created=datetime(2020, 6, 1))
        target_booking_2 = create_booking(user=user,
                                          stock=target_stock,
                                          venue=venue,
                                          quantity=2,
                                          recommendation=None,
                                          date_created=datetime(2020, 6, 30))
        other_booking_2 = create_booking(user=user,
                                         stock=target_stock,
                                         venue=venue,
                                         quantity=2,
                                         recommendation=None,
                                         date_created=datetime(2020, 7, 1))
        other_booking_3 = create_booking(user=user,
                                         stock=other_stock,
                                         venue=venue,
                                         quantity=2,
                                         recommendation=None,
                                         date_created=datetime(2020, 6, 1))

        PcObject.save(other_booking_1, other_booking_2, other_booking_3, target_booking_1, target_booking_2)

        target_offer_id = target_offer.id

        # when
        bookings = booking_queries.find_offerer_bookings(offerer.id, venue_id=venue.id, offer_id=target_offer_id,
                                                         date_from=datetime(2020, 6, 1), date_to=datetime(2020, 6, 30))

        # then
        assert len(bookings) == 2
        assert target_booking_1 in bookings
        assert target_booking_2 in bookings

    @clean_database
    def test_returns_bookings_on_given_venue_and_event_offer_and_date(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)
        offerer = create_offerer(siren='offerer')
        venue = create_venue(offerer, siret=offerer.siren + '12345')

        target_offer = create_offer_with_event_product(venue)
        other_offer = create_offer_with_event_product(venue)

        target_stock = create_stock_from_offer(target_offer, available=150, price=16,
                                               beginning_datetime=datetime.strptime("2020-06-01T20:00:00.000Z",
                                                                                    "%Y-%m-%dT%H:%M:%S.%fZ"))
        other_stock_1 = create_stock_from_offer(target_offer, available=100, price=20,
                                                beginning_datetime=datetime.strptime("2020-06-01T16:00:00.000Z",
                                                                                     "%Y-%m-%dT%H:%M:%S.%fZ"))
        other_stock_2 = create_stock_from_offer(other_offer, available=150, price=16,
                                                beginning_datetime=datetime.strptime("2020-06-01T18:00:00.000Z",
                                                                                     "%Y-%m-%dT%H:%M:%S.%fZ"))
        other_stock_3 = create_stock_from_offer(other_offer, available=150, price=16,
                                                beginning_datetime=datetime.strptime("2020-07-02T20:00:00.000Z",
                                                                                     "%Y-%m-%dT%H:%M:%S.%fZ"))

        target_booking = create_booking(user=user, stock=target_stock, venue=venue, quantity=2, recommendation=None)
        other_booking_1 = create_booking(user=user, stock=other_stock_1, venue=venue, quantity=2, recommendation=None)
        other_booking_2 = create_booking(user=user, stock=other_stock_2, venue=venue, quantity=2, recommendation=None)
        other_booking_3 = create_booking(user=user, stock=other_stock_3, venue=venue, quantity=2, recommendation=None)

        PcObject.save(other_booking_1, other_booking_2,
                      target_booking, other_booking_3)

        target_offer_id = target_offer.id

        # when
        bookings = booking_queries.find_offerer_bookings(offerer.id, venue_id=venue.id, offer_id=target_offer_id,
                                                         date_from='2020-06-01T20:00:00.000Z',
                                                         date_to='2020-05-01T20:00:00.000Z')

        # then
        assert len(bookings) == 1
        assert target_booking in bookings


class FindAllDigitalBookingsForOffererTest:
    @clean_database
    def test_returns_bookings_linked_to_digital_venue(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)
        offerer1 = create_offerer(siren='123456789')
        digital_venue = create_venue(offerer1, siret=None, is_virtual=True)
        physical_venue = create_venue(offerer1, siret=offerer1.siren + '12345')
        stock1 = create_stock_with_event_offer(
            offerer1, digital_venue, price=2, available=100)
        stock2 = create_stock_with_thing_offer(
            offerer1, physical_venue, price=3, available=100)
        booking_for_digital = create_booking(user=user, stock=stock1, venue=digital_venue, quantity=2,
                                             recommendation=None)
        booking_for_physical = create_booking(user=user, stock=stock2, venue=physical_venue, quantity=2,
                                              recommendation=None)

        PcObject.save(booking_for_digital, booking_for_physical)

        # when
        bookings = booking_queries.find_digital_bookings_for_offerer(offerer1.id)

        # then
        assert len(bookings) == 1
        assert bookings[0] == booking_for_digital

    @clean_database
    def test_returns_only_bookings_for_specified_offerer(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)

        target_offerer = create_offerer(siren='123456789')
        other_offerer = create_offerer(siren='567891234')

        target_digital_venue = create_venue(
            target_offerer, siret=None, is_virtual=True)
        other_digital_venue = create_venue(
            other_offerer, siret=None, is_virtual=True)

        target_stock = create_stock_with_event_offer(
            target_offerer, target_digital_venue, price=2, available=100)
        other_stock = create_stock_with_thing_offer(
            other_offerer, other_digital_venue, price=3, available=100)

        targeet_booking = create_booking(user=user, stock=target_stock, venue=target_digital_venue, quantity=2,
                                         recommendation=None)
        other_booking = create_booking(user=user, stock=other_stock, venue=other_digital_venue, quantity=2,
                                       recommendation=None)

        PcObject.save(targeet_booking, other_booking)

        # when
        bookings = booking_queries.find_digital_bookings_for_offerer(target_offerer.id)

        # then
        assert len(bookings) == 1
        assert bookings[0] == targeet_booking

    @clean_database
    def test_returns_only_bookings_for_specified_offerer_and_offer(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)
        offerer1 = create_offerer(siren='123456789')
        digital_venue_for_offerer1 = create_venue(
            offerer1, siret=None, is_virtual=True)
        stock1 = create_stock_with_event_offer(
            offerer1, digital_venue_for_offerer1, price=2, available=100)
        stock2 = create_stock_with_thing_offer(
            offerer1, digital_venue_for_offerer1, price=3, available=100)
        booking_for_offerer1 = create_booking(user=user, stock=stock1, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None)
        booking_for_offerer2 = create_booking(user=user, stock=stock2, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None)

        PcObject.save(booking_for_offerer1, booking_for_offerer2)

        # when
        bookings = booking_queries.find_digital_bookings_for_offerer(
            offerer1.id, stock2.offer.id)

        # then
        assert len(bookings) == 1
        assert bookings[0] == booking_for_offerer2

    @clean_database
    def test_returns_only_bookings_for_specified_offerer_and_thing_offer_and_booking_date(self, app):
        # given
        user = create_user()
        now = datetime.utcnow()
        create_deposit(user, amount=1600)
        offerer1 = create_offerer(siren='123456789')
        digital_venue_for_offerer1 = create_venue(
            offerer1, siret=None, is_virtual=True)
        stock1 = create_stock_with_event_offer(
            offerer1, digital_venue_for_offerer1, price=2, available=100)
        stock2 = create_stock_with_thing_offer(
            offerer1, digital_venue_for_offerer1, price=3, available=100)
        booking_for_offerer1 = create_booking(user=user, stock=stock2, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None, date_created=datetime(2020, 5, 30))
        booking_for_offerer2 = create_booking(user=user, stock=stock2, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None, date_created=datetime(2020, 6, 1))
        booking_for_offerer3 = create_booking(user=user, stock=stock2, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None, date_created=datetime(2020, 6, 30))
        booking_for_offerer4 = create_booking(user=user, stock=stock2, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None, date_created=datetime(2020, 7, 31))
        booking_for_offerer5 = create_booking(user=user, stock=stock1, venue=digital_venue_for_offerer1, quantity=2,
                                              recommendation=None, date_created=datetime(2020, 6, 30))

        PcObject.save(booking_for_offerer1, booking_for_offerer2, booking_for_offerer3, booking_for_offerer4,
                      booking_for_offerer5)

        # when
        bookings = booking_queries.find_digital_bookings_for_offerer(offerer1.id, stock2.offer.id,
                                                                     date_from=datetime(2020, 6, 1),
                                                                     date_to=datetime(2020, 6, 30))

        # then
        assert len(bookings) == 2
        assert bookings[0] == booking_for_offerer2
        assert bookings[1] == booking_for_offerer3


@clean_database
def test_find_all_ongoing_bookings(app):
    # Given
    offerer = create_offerer(siren='985281920')
    PcObject.save(offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
    user = create_user()
    cancelled_booking = create_booking(user=user, stock=stock, is_cancelled=True)
    validated_booking = create_booking(user=user, stock=stock, is_used=True)
    ongoing_booking = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False)
    PcObject.save(ongoing_booking)
    PcObject.save(validated_booking)
    PcObject.save(cancelled_booking)

    # When
    all_ongoing_bookings = booking_queries.find_ongoing_bookings_by_stock(stock)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]


class FindFinalOffererBookingsTest:
    @clean_database
    def test_returns_bookings_for_given_offerer(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1, siret=offerer1.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user=user, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, is_used=True, stock=stock, venue=venue)

        offerer2 = create_offerer(siren='987654321')
        venue = create_venue(offerer2, siret=offerer2.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer2, venue, offer)
        booking3 = create_booking(user=user, is_used=True, stock=stock, venue=venue)

        PcObject.save(deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer1.id)

        # Then
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    @clean_database
    def test_returns_bookings_with_payment_first_ordered_by_date_created(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, amount=500)

        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user=user, date_created=five_days_ago, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, date_created=two_days_ago, is_used=True, stock=stock, venue=venue)
        booking3 = create_booking(user=user, date_created=four_days_ago, is_used=True, stock=stock, venue=venue)
        booking4 = create_booking(user=user, date_created=three_days_ago, is_used=True, stock=stock, venue=venue)
        payment1 = create_payment(booking4, offerer, 5)
        payment2 = create_payment(booking3, offerer, 5)

        PcObject.save(deposit, booking1, booking2, booking3,
                      booking4, payment1, payment2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer.id)

        # Then
        assert bookings[0] == booking3
        assert bookings[1] == booking4
        assert bookings[2] == booking1
        assert bookings[3] == booking2

    @clean_database
    def test_returns_not_cancelled_bookings_for_offerer(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user=user, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, is_cancelled=True, is_used=True, stock=stock, venue=venue)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings

    @clean_database
    def test_returns_only_used_bookings(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user=user, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, is_used=False, stock=stock, venue=venue)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings


class FindFinalVenueBookingsTest:
    @clean_database
    def test_returns_bookings_for_given_venue_ordered_by_date_created(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue1 = create_venue(offerer1, siret=offerer1.siren + '12345')
        offer = create_offer_with_thing_product(venue1)
        stock = create_stock_with_thing_offer(offerer1, venue1, offer)
        booking1 = create_booking(user=user, date_created=datetime(2019, 1, 1), is_used=True, stock=stock, venue=venue1)
        booking2 = create_booking(user=user, date_created=datetime(2019, 1, 2), is_used=True, stock=stock, venue=venue1)

        offerer2 = create_offerer(siren='987654321')
        venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
        offer = create_offer_with_thing_product(venue2)
        stock = create_stock_with_thing_offer(offerer2, venue2, offer)
        booking3 = create_booking(user=user, is_used=True, stock=stock, venue=venue2)

        PcObject.save(deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_eligible_bookings_for_venue(venue1.id)

        # Then
        assert len(bookings) == 2
        assert bookings[0] == booking1
        assert bookings[1] == booking2
        assert booking3 not in bookings

    @clean_database
    def test_returns_only_bookings_on_events_finished_more_than_two_days_ago(self, app):
        # Given
        user = create_user()
        now = datetime.utcnow()
        deposit = create_deposit(user, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(
            offer=offer, end_datetime=now - timedelta(days=3))
        stock2 = create_stock(
            offer=offer, end_datetime=now - timedelta(days=1))
        booking1 = create_booking(user=user, is_used=False, stock=stock1, venue=venue)
        booking2 = create_booking(user=user, is_used=False, stock=stock2, venue=venue)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings


class FindDateUsedTest:
    @clean_database
    def test_returns_date_used_if_not_none(self, app):
        # given
        user = create_user()
        deposit = create_deposit(user, amount=500)
        booking = create_booking(user=user, date_used=datetime(2018, 2, 12), is_used=True)
        PcObject.save(user, deposit, booking)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used == datetime(2018, 2, 12)

    @clean_database
    def test_returns_none_when_date_used_is_none(self, app):
        # given
        user = create_user()
        deposit = create_deposit(user, amount=500)
        booking = create_booking(user=user)
        PcObject.save(user, deposit, booking)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used is None

    @clean_database
    def test_find_date_used_on_booking_returns_none_if_no_update_recorded_in_activity_table(self, app):
        # given
        user = create_user()
        deposit = create_deposit(user, amount=500)
        booking = create_booking(user=user)
        PcObject.save(user, deposit, booking)

        activity_insert = create_booking_activity(
            booking, 'booking', 'insert', issued_at=datetime(2018, 1, 28)
        )

        save_all_activities(activity_insert)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used is None


class FindUserActivationBookingTest:
    @clean_database
    def test_returns_activation_thing_booking_linked_to_user(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.ACTIVATION)
        activation_stock = create_stock_from_offer(
            activation_offer, available=200, price=0)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        PcObject.save(activation_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @clean_database
    def test_returns_activation_event_booking_linked_to_user(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_event_product(
            venue_online, event_type=EventType.ACTIVATION)
        activation_stock = create_stock_from_offer(
            activation_offer, available=200, price=0)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        PcObject.save(activation_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @clean_database
    def test_returns_false_is_no_booking_exists_on_such_stock(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(
            book_offer, available=200, price=0)
        book_booking = create_booking(user=user, stock=book_stock, venue=venue_online)
        PcObject.save(book_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking is None


class GetExistingTokensTest:
    @clean_database
    def test_returns_a_set_of_tokens(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(
            book_offer, available=200, price=0)
        booking1 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking2 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        PcObject.save(booking1, booking2, booking3)

        # when
        tokens = booking_queries.find_existing_tokens()

        # then
        assert tokens == {booking1.token, booking2.token, booking3.token}

    @clean_database
    def test_returns_an_empty_set_if_no_bookings(self, app):
        # when
        tokens = booking_queries.find_existing_tokens()

        # then
        assert tokens == set()


class FindAllActiveByUserIdTest:
    @clean_database
    def test_returns_a_list_of_not_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(
            book_offer, available=200, price=0)
        booking1 = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue_online)
        booking2 = create_booking(user=user, is_used=True, stock=book_stock, venue=venue_online)
        booking3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        PcObject.save(booking1, booking2, booking3)

        # when
        bookings = booking_queries.find_active_bookings_by_user_id(user.id)

        # then
        assert len(bookings) == 2
        assert booking1 not in bookings


class FindByTest:
    class ByTokenTest:
        @clean_database
        def test_returns_booking_if_token_is_known(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token)

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_unknown(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as e:
                booking_queries.find_by('UNKNOWN')

            # then
            assert e.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailTest:
        @clean_database
        def test_returns_booking_if_token_and_email_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_case_insensitively(self, app):
            # given
            user = create_user(email='USer@eXAMple.COm')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='USER@example.COM')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_with_trailing_spaces(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='   user@example.com  ')

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_known_but_email_is_unknown(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as e:
                booking_queries.find_by(booking.token, email='other.user@example.com')

            # then
            assert e.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailAndOfferIdTest:
        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_thing_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com',
                                             offer_id=stock.resolvedOffer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_event_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            PcObject.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com',
                                             offer_id=stock.resolvedOffer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_are_known_but_offer_id_is_unknown(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as e:
                result = booking_queries.find_by(
                    booking.token, email='user@example.com', offer_id=1234)

            # then
            assert e.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]


class SaveBookingTest:
    @clean_database
    def test_saves_booking_when_enough_stocks_after_cancellation(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, available=1)
        user_cancelled = create_user(email='cancelled@booking.com')
        user_booked = create_user(email='booked@email.com')
        cancelled_booking = create_booking(user=user_cancelled, stock=stock, is_cancelled=True)
        PcObject.save(cancelled_booking)
        booking = create_booking(user=user_booked, stock=stock, is_cancelled=False)

        # When
        PcObject.save(booking)

        # Then
        assert Booking.query.filter_by(isCancelled=False).count() == 1
        assert Booking.query.filter_by(isCancelled=True).count() == 1

    @clean_database
    def test_raises_too_many_bookings_error_when_not_enough_stocks(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, available=1)
        user1 = create_user(email='cancelled@booking.com')
        user2 = create_user(email='booked@email.com')
        booking1 = create_booking(user=user1, stock=stock, is_cancelled=False)
        PcObject.save(booking1)
        booking2 = create_booking(user=user2, stock=stock, is_cancelled=False)

        # When
        with pytest.raises(ApiErrors) as e:
            PcObject.save(booking2)

        # Then
        assert e.value.errors['global'] == [
            'La quantité disponible pour cette offre est atteinte.']


class CountNonCancelledBookingsTest:
    @clean_database
    def test_returns_1_if_one_user_has_one_non_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 1

    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 0

    @clean_database
    def test_returns_zero_if_two_users_have_activation_booking(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='e@mail.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1)
        booking2 = create_booking(user=user2, stock=stock2)
        PcObject.save(booking1, booking2)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 0


class CountNonCancelledBookingsByDepartementTest:
    @clean_database
    def test_returns_1_if_one_user_has_one_non_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 1

    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 0

    @clean_database
    def test_returns_0_if_user_comes_from_wrong_departement(self, app):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('81')

        # Then
        assert count == 0

    @clean_database
    def test_returns_zero_if_users_only_have_activation_bookings(self, app):
        # Given
        user1 = create_user(departement_code='76')
        user2 = create_user(departement_code='76', email='e@mail.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1)
        booking2 = create_booking(user=user2, stock=stock2)
        PcObject.save(booking1, booking2)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 0


class GetAllCancelledBookingsCountTest:
    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user()
        booking = create_booking(user=user, stock=event_stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_1_if_one_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user()
        booking = create_booking(user=user, stock=event_stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_zero_if_only_activation_offers(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        stock1 = create_stock(
            offer=offer1,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        stock2 = create_stock(offer=offer2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=True)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 0


class GetAllCancelledBookingsByDepartementCountTest:
    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user(departement_code='76')
        booking = create_booking(user=user, stock=event_stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('76')

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_1_if_one_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user(departement_code='76')
        booking = create_booking(user=user, stock=event_stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('76')

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_1_when_filtered_on_user_departement(self, app):
        # Given
        user_in_76 = create_user(departement_code='76', email='user-76@example.net')
        user_in_41 = create_user(departement_code='41', email='user-41@example.net')

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)

        booking1 = create_booking(user=user_in_76, stock=stock, is_cancelled=True)
        booking2 = create_booking(user=user_in_41, stock=stock, is_cancelled=True)
        booking3 = create_booking(user=user_in_41, stock=stock, is_cancelled=False)
        PcObject.save(booking1, booking2, booking3)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('41')

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_zero_if_only_activation_bookings(self, app):
        # Given
        user = create_user(departement_code='41', email='user-41@example.net')

        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='78000')
        offer1 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)

        booking1 = create_booking(user=user, stock=stock1, is_cancelled=True)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('41')

        # Then
        assert number_of_bookings == 0


class CountAllBookingsTest:
    @clean_database
    def test_returns_0_when_no_bookings(self, app):
        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_saves_booking_when_existing_booking_is_used_and_booking_date_is_before_last_update_on_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, available=1)
        user1 = create_user(email='used_booking@booking.com')
        user2 = create_user(email='booked@email.com')
        one_day_before_stock_last_update = datetime.utcnow() - timedelta(days=2)
        booking1 = create_booking(user=user1, stock=stock, date_used=one_day_before_stock_last_update,
                                  is_cancelled=False,
                                  is_used=True)
        PcObject.save(booking1)
        booking2 = create_booking(user=user2, stock=stock, is_cancelled=False, is_used=False)

        # When
        PcObject.save(booking2)

        # Then
        assert Booking.query.filter_by(stock=stock).count() == 2

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_zero_when_bookings_are_on_activation_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1)
        booking2 = create_booking(user=user, stock=stock2)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 0


class CountBookingsByDepartementTest:
    @clean_database
    def test_returns_0_when_no_bookings(self, app):
        # When
        number_of_bookings = booking_queries.count_by_departement('74')

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user(departement_code='74')
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('74')

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_1_when_bookings_are_filtered_by_departement(self, app):
        # Given
        user_in_76 = create_user(departement_code='76', email='user-76@example.net')
        user_in_41 = create_user(departement_code='41', email='user-41@example.net')

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)

        booking1 = create_booking(user=user_in_76, stock=stock)
        booking2 = create_booking(user=user_in_41, stock=stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('76')

        # Then

    @clean_database
    def test_returns_0_when_bookings_are_on_activation_offers(self, app):
        # Given
        user = create_user(departement_code='76')

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)

        booking1 = create_booking(user=user, stock=stock1)
        booking2 = create_booking(user=user, stock=stock1)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('76')

        # Then
        assert number_of_bookings == 0


class FindAllNotUsedAndNotCancelledTest:
    @clean_database
    def test_return_no_booking_if_only_used(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, date_used=datetime(2019, 10, 12), is_used=True, stock=stock)
        PcObject.save(user, deposit, booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_no_booking_if_only_cancelled(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, is_cancelled=True, stock=stock)
        PcObject.save(user, deposit, booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_no_booking_if_used_but_cancelled(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, is_cancelled=True, is_used=True, stock=stock)
        PcObject.save(user, deposit, booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_1_booking_if_not_used_and_not_cancelled(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking1 = create_booking(user=user, is_cancelled=False, is_used=False, stock=stock)
        booking2 = create_booking(user=user, is_used=True, stock=stock)
        booking3 = create_booking(user=user, is_cancelled=True, stock=stock)
        PcObject.save(user, deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert bookings == [booking1]


class GetValidBookingsByUserId:
    @clean_database
    def test_should_return_bookings_by_user_id(self, app):
        # Given
        user1 = create_user(email='me@example.net')
        deposit1 = create_deposit(user1)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        user2 = create_user(email='fa@example.net')
        deposit2 = create_deposit(user2)
        booking1 = create_booking(user=user1, stock=stock)
        booking2 = create_booking(user=user2, stock=stock)
        PcObject.save(user1, user2, deposit1, deposit2, booking1, booking2)

        # When
        bookings = booking_queries.find_for_my_bookings_page(user1.id)

        # Then
        assert bookings == [booking1]

    @clean_database
    def test_should_return_bookings_by_type_other_than_ACTIVATION(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(
            venue, event_type='ThingType.ACTIVATION')
        offer2 = create_offer_with_event_product(
            venue, event_type='EventType.ACTIVATION')
        offer3 = create_offer_with_event_product(
            venue, event_type='ThingType.ANY')
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)
        stock3 = create_stock(offer=offer3)
        booking1 = create_booking(user=user, stock=stock1)
        booking2 = create_booking(user=user, stock=stock2)
        booking3 = create_booking(user=user, stock=stock3)
        PcObject.save(user, deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_for_my_bookings_page(user.id)

        # Then
        assert bookings == [booking3]

    @clean_database
    def test_should_return_bookings_when_there_is_one_cancelled_booking(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        offer2 = create_offer_with_event_product(venue)
        stock2 = create_stock(offer=offer2)
        booking1 = create_booking(user=user, is_cancelled=True, stock=stock)
        booking2 = create_booking(user=user, is_cancelled=False, stock=stock)
        booking3 = create_booking(user=user, is_cancelled=False, stock=stock2)
        PcObject.save(user, deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_for_my_bookings_page(user.id)

        # Then
        assert booking1 not in bookings

    @clean_database
    def test_should_return_most_recent_booking_when_two_cancelled_on_same_stock(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking1 = create_booking(user=user, date_created=two_days_ago, is_cancelled=True, stock=stock)
        booking2 = create_booking(user=user, date_created=three_days_ago, is_cancelled=True, stock=stock)
        PcObject.save(user, deposit, booking1, booking2)

        # When
        bookings = booking_queries.find_for_my_bookings_page(user.id)

        # Then
        assert bookings == [booking1]

    @clean_database
    def test_should_return_bookings_ordered_by_beginning_date_time_ascendant(self, app):
        # Given
        two_days = NOW + timedelta(days=2, hours=10)
        two_days_bis = NOW + timedelta(days=2, hours=20)
        five_days = NOW + timedelta(days=5)
        three_days = NOW + timedelta(days=3)
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer1, beginning_datetime=three_days, end_datetime=five_days,
                              booking_limit_datetime=NOW)
        offer2 = create_offer_with_event_product(venue)
        stock2 = create_stock(offer=offer2, beginning_datetime=two_days, end_datetime=five_days,
                              booking_limit_datetime=NOW)
        offer3 = create_offer_with_event_product(venue)
        stock3 = create_stock(offer=offer3, beginning_datetime=two_days_bis, end_datetime=five_days,
                              booking_limit_datetime=NOW)
        booking1 = create_booking(user=user, stock=stock1, recommendation=create_recommendation(user=user, offer=offer1))
        booking2 = create_booking(user=user, stock=stock2, recommendation=create_recommendation(user=user, offer=offer2))
        booking3 = create_booking(user=user, stock=stock3, recommendation=create_recommendation(user=user, offer=offer3))
        PcObject.save(user, deposit, booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_for_my_bookings_page(user.id)

        # Then
        assert bookings == [booking2, booking3, booking1]
