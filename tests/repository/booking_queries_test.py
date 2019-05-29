""" repository booking queries test """
from datetime import datetime, timedelta

import pytest

from models import PcObject, ThingType, Booking
from models.api_errors import ResourceNotFound, ApiErrors
from repository.booking_queries import find_all_ongoing_bookings_by_stock, \
    find_offerer_bookings_paginated, \
    find_final_offerer_bookings, find_date_used, find_user_activation_booking, get_existing_tokens, \
    find_active_bookings_by_user_id, find_by, find_all_offerer_bookings
from tests.conftest import clean_database
from tests.test_utils import create_booking, \
    create_deposit, \
    create_offerer, \
    create_stock_with_event_offer, \
    create_stock_with_thing_offer, \
    create_user, \
    create_venue, create_stock_from_event_occurrence, create_event_occurrence, create_offer_with_thing_product, \
    create_offer_with_event_product, \
    create_booking_activity, save_all_activities, create_stock_from_offer, create_payment

NOW = datetime.utcnow()
two_days_ago = NOW - timedelta(days=2)
four_days_ago = NOW - timedelta(days=4)
five_days_ago = NOW - timedelta(days=5)
three_days_ago = NOW - timedelta(days=3)


@clean_database
@pytest.mark.standalone
def test_find_all_by_offerer_with_event_and_things(app):
    # given
    user = create_user()
    now = datetime.utcnow()
    create_deposit(user, now, amount=1600)
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    venue1 = create_venue(offerer1, siret=offerer1.siren + '12345')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    stock1 = create_stock_with_event_offer(offerer1, venue1, price=200)
    stock2 = create_stock_with_thing_offer(offerer1, venue1, offer=None, price=300)
    stock3 = create_stock_with_thing_offer(offerer2, venue2, offer=None, price=400)
    booking1 = create_booking(user, stock1, venue1, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, venue1, recommendation=None, quantity=1)
    booking3 = create_booking(user, stock3, venue2, recommendation=None, quantity=2)
    PcObject.save(booking1, booking2, booking3)

    # when
    bookings = find_offerer_bookings_paginated(offerer1.id)

    # then
    assert booking1 in bookings
    assert booking2 in bookings
    assert booking3 not in bookings


@clean_database
@pytest.mark.standalone
def test_find_all_bookings_by_offerer_in_a_not_search_context_returns_all_results(app):
    # given
    user = create_user()
    now = datetime.utcnow()
    create_deposit(user, now, amount=1600)
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    venue1 = create_venue(offerer1, siret=offerer1.siren + '12345')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    stock1 = create_stock_with_event_offer(offerer1, venue1, price=2, available=100)
    stock2 = create_stock_with_thing_offer(offerer1, venue1, price=3, available=100)
    booking1 = create_booking(user, stock1, venue1, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, venue1, recommendation=None, quantity=1)
    booking3 = create_booking(user, stock2, venue2, recommendation=None, quantity=2)
    booking4 = create_booking(user, stock1, venue1, recommendation=None, quantity=2)
    booking5 = create_booking(user, stock2, venue1, recommendation=None, quantity=1)
    booking6 = create_booking(user, stock2, venue2, recommendation=None, quantity=2)
    booking7 = create_booking(user, stock1, venue1, recommendation=None, quantity=2)
    booking8 = create_booking(user, stock2, venue1, recommendation=None, quantity=1)
    booking9 = create_booking(user, stock2, venue2, recommendation=None, quantity=2)
    booking10 = create_booking(user, stock1, venue2, recommendation=None, quantity=2)
    booking11 = create_booking(user, stock2, venue2, recommendation=None, quantity=2)
    booking12 = create_booking(user, stock2, venue2, recommendation=None, quantity=2)
    PcObject.save(booking1, booking2, booking3, booking4, booking5, booking6,
                  booking6, booking7, booking8, booking9, booking10, booking11, booking12)

    # when
    bookings = find_all_offerer_bookings(offerer1.id)

    # then
    assert len(bookings) == 12


@clean_database
@pytest.mark.standalone
def test_find_all_ongoing_bookings(app):
    # Given
    offerer = create_offerer(siren='985281920')
    PcObject.save(offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
    user = create_user()
    cancelled_booking = create_booking(user, stock, is_cancelled=True)
    validated_booking = create_booking(user, stock, is_used=True)
    ongoing_booking = create_booking(user, stock, is_cancelled=False, is_used=False)
    PcObject.save(ongoing_booking)
    PcObject.save(validated_booking)
    PcObject.save(cancelled_booking)

    # When
    all_ongoing_bookings = find_all_ongoing_bookings_by_stock(stock)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]


@pytest.mark.standalone
class FindFinalOffererBookingsTest:
    @clean_database
    def test_returns_bookings_for_given_offerer(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, datetime.utcnow(), amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1, siret=offerer1.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user, stock=stock, venue=venue, is_used=True)
        booking2 = create_booking(user, stock=stock, venue=venue, is_used=True)

        offerer2 = create_offerer(siren='987654321')
        venue = create_venue(offerer2, siret=offerer2.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer2, venue, offer)
        booking3 = create_booking(user, stock=stock, venue=venue, is_used=True)

        PcObject.save(deposit, booking1, booking2, booking3)

        # When
        bookings = find_final_offerer_bookings(offerer1.id)

        # Then
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    @clean_database
    def test_returns_bookings_with_payment_first_ordered_by_date_created(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, NOW, amount=500)

        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user, stock=stock, venue=venue, is_used=True, date_created=five_days_ago)
        booking2 = create_booking(user, stock=stock, venue=venue, is_used=True, date_created=two_days_ago)
        booking3 = create_booking(user, stock=stock, venue=venue, is_used=True, date_created=four_days_ago)
        booking4 = create_booking(user, stock=stock, venue=venue, is_used=True, date_created=three_days_ago)
        payment1 = create_payment(booking4, offerer, 5)
        payment2 = create_payment(booking3, offerer, 5)

        PcObject.save(deposit, booking1, booking2, booking3, booking4, payment1, payment2)

        # When
        bookings = find_final_offerer_bookings(offerer.id)

        # Then
        assert bookings[0] == booking3
        assert bookings[1] == booking4
        assert bookings[2] == booking1
        assert bookings[3] == booking2

    @clean_database
    def test_returns_not_cancelled_bookings_for_offerer(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, datetime.utcnow(), amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user, stock=stock, venue=venue, is_used=True)
        booking2 = create_booking(user, stock=stock, venue=venue, is_cancelled=True, is_used=True)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = find_final_offerer_bookings(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings

    @clean_database
    def test_returns_only_used_bookings(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user, datetime.utcnow(), amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer1, venue, offer)
        booking1 = create_booking(user, stock=stock, venue=venue, is_used=True)
        booking2 = create_booking(user, stock=stock, venue=venue, is_used=False)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = find_final_offerer_bookings(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings

    @clean_database
    def test_returns_only_bookings_on_events_finished_more_than_two_days_ago(self, app):
        # Given
        user = create_user()
        now = datetime.utcnow()
        deposit = create_deposit(user, now, amount=500)

        offerer1 = create_offerer(siren='123456789')
        venue = create_venue(offerer1)
        offer = create_offer_with_event_product(venue)
        old_event_occurrence = create_event_occurrence(
            offer,
            beginning_datetime=now - timedelta(hours=60),
            end_datetime=now - timedelta(hours=50)
        )
        recent_event_occurrence = create_event_occurrence(
            offer,
            beginning_datetime=now - timedelta(hours=50),
            end_datetime=now - timedelta(hours=40)
        )
        stock1 = create_stock_from_event_occurrence(old_event_occurrence)
        stock2 = create_stock_from_event_occurrence(recent_event_occurrence)
        booking1 = create_booking(user, stock=stock1, venue=venue, is_used=False)
        booking2 = create_booking(user, stock=stock2, venue=venue, is_used=False)

        PcObject.save(deposit, booking1, booking2)

        # When
        bookings = find_final_offerer_bookings(offerer1.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings


@pytest.mark.standalone
class FindDateUsedTest:
    @clean_database
    def test_returns_issued_date_of_matching_activity(self, app):
        # given
        user = create_user()
        deposit = create_deposit(user, datetime.utcnow(), amount=500)
        booking = create_booking(user)
        PcObject.save(user, deposit, booking)

        activity_insert = create_booking_activity(
            booking, 'booking', 'insert', issued_at=datetime(2018, 1, 28)
        )
        activity_update = create_booking_activity(
            booking, 'booking', 'update', issued_at=datetime(2018, 2, 12),
            data={'isUsed': True}
        )
        save_all_activities(activity_insert, activity_update)

        # when
        date_used = find_date_used(booking)

        # then
        assert date_used == datetime(2018, 2, 12)


@pytest.mark.standalone
@clean_database
def test_find_date_used_on_booking_returns_none_if_no_activity_with_is_used_changed_is_found(app):
    # given
    user = create_user()
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    booking = create_booking(user)
    PcObject.save(user, deposit, booking)

    activity_insert = create_booking_activity(
        booking, 'booking', 'insert', issued_at=datetime(2018, 1, 28)
    )

    save_all_activities(activity_insert)

    # when
    date_used = find_date_used(booking)

    # then
    assert date_used is None


@pytest.mark.standalone
class FindUserActivationBookingTest:
    @clean_database
    def test_returns_true_is_a_booking_exists_on_such_stock(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, available=200, price=0)
        activation_booking = create_booking(user, stock=activation_stock, venue=venue_online)
        PcObject.save(activation_booking)

        # when
        booking = find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @clean_database
    def test_returns_false_is_no_booking_exists_on_such_stock(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, available=200, price=0)
        book_booking = create_booking(user, stock=book_stock, venue=venue_online)
        PcObject.save(book_booking)

        # when
        booking = find_user_activation_booking(user)

        # then
        assert booking is None


@pytest.mark.standalone
class GetExistingTokensTest:
    @clean_database
    def test_returns_a_set_of_tokens(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, available=200, price=0)
        booking1 = create_booking(user, stock=book_stock, venue=venue_online)
        booking2 = create_booking(user, stock=book_stock, venue=venue_online)
        booking3 = create_booking(user, stock=book_stock, venue=venue_online)
        PcObject.save(booking1, booking2, booking3)

        # when
        tokens = get_existing_tokens()

        # then
        assert tokens == {booking1.token, booking2.token, booking3.token}

    @clean_database
    def test_returns_an_empty_set_if_no_bookings(self, app):
        # when
        tokens = get_existing_tokens()

        # then
        assert tokens == set()


@pytest.mark.standalone
class FindAllActiveByUserIdTest:
    @clean_database
    def test_returns_a_list_of_not_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, available=200, price=0)
        booking1 = create_booking(user, stock=book_stock, venue=venue_online, is_cancelled=True)
        booking2 = create_booking(user, stock=book_stock, venue=venue_online, is_used=True)
        booking3 = create_booking(user, stock=book_stock, venue=venue_online)
        PcObject.save(booking1, booking2, booking3)

        # when
        bookings = find_active_bookings_by_user_id(user.id)

        # then
        assert len(bookings) == 2
        assert booking1 not in bookings


@pytest.mark.standalone
class FindByTest:
    class ByTokenTest:
        @clean_database
        def test_returns_booking_if_token_is_known(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token)

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_unknown(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFound) as e:
                find_by('UNKNOWN')

            # then
            assert e.value.errors['global'] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailTest:
        @clean_database
        def test_returns_booking_if_token_and_email_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token, email='user@example.com')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_case_insensitively(self, app):
            # given
            user = create_user(email='USer@eXAMple.COm')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token, email='USER@example.COM')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_with_trailing_spaces(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token, email='   user@example.com  ')

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_known_but_email_is_unknown(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFound) as e:
                find_by(booking.token, email='other.user@example.com')

            # then
            assert e.value.errors['global'] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailAndOfferIdTest:
        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_thing_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token, email='user@example.com', offer_id=stock.resolvedOffer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_event_are_known(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, venue=venue, stock=stock)
            PcObject.save(booking)

            # when
            result = find_by(booking.token, email='user@example.com', offer_id=stock.resolvedOffer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_are_known_but_offer_id_is_unknown(self, app):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user, stock=stock)
            PcObject.save(booking)

            # when
            with pytest.raises(ResourceNotFound) as e:
                result = find_by(booking.token, email='user@example.com', offer_id=1234)

            # then
            assert e.value.errors['global'] == ["Cette contremarque n'a pas été trouvée"]


@pytest.mark.standalone
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
        cancelled_booking = create_booking(user_cancelled, stock, is_cancelled=True)
        booking = create_booking(user_booked, stock, is_cancelled=False)
        PcObject.save(cancelled_booking)

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
        booking1 = create_booking(user1, stock, is_cancelled=False)
        PcObject.save(booking1)
        booking2 = create_booking(user2, stock, is_cancelled=False)

        # When
        with pytest.raises(ApiErrors) as e:
            PcObject.save(booking2)

        # Then
        assert e.value.errors['global'] == ['la quantité disponible pour cette offre est atteinte']
