from datetime import datetime, timedelta

import pytest
from dateutil import tz
from freezegun import freeze_time
from pytest import fixture

from domain.booking_recap.booking_recap import EventBookingRecap, BookBookingRecap
from models import BookingSQLEntity, EventType, ThingType
from models.api_errors import ApiErrors, ResourceNotFoundError
from models.payment_status import TransactionStatus
from models.stock_sql_entity import EVENT_AUTOMATIC_REFUND_DELAY
from repository import booking_queries, repository
from repository.booking_queries import find_by_pro_user_id, find_first_matching_from_offer_by_user
from tests.conftest import clean_database
from tests.model_creators.activity_creators import create_booking_activity, \
    save_all_activities
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_offerer, create_payment, create_stock, create_user, create_venue, create_user_offerer, \
    create_recommendation
from tests.model_creators.specific_creators import \
    create_offer_with_event_product, create_offer_with_thing_product, \
    create_stock_from_offer, create_stock_with_event_offer, \
    create_stock_with_thing_offer

NOW = datetime.utcnow()
ONE_DAY_AGO = NOW - timedelta(days=1)
TWO_DAYS_AGO = NOW - timedelta(days=2)
THREE_DAYS_AGO = NOW - timedelta(days=3)
FOUR_DAYS_AGO = NOW - timedelta(days=4)
FIVE_DAYS_AGO = NOW - timedelta(days=5)


@clean_database
def test_find_all_ongoing_bookings(app):
    # Given
    offerer = create_offerer()
    repository.save(offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
    user = create_user()
    cancelled_booking = create_booking(user=user, stock=stock, is_cancelled=True)
    validated_booking = create_booking(user=user, stock=stock, is_used=True)
    ongoing_booking = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False)
    repository.save(ongoing_booking, validated_booking, cancelled_booking)

    # When
    all_ongoing_bookings = booking_queries.find_ongoing_bookings_by_stock(stock.id)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]


@clean_database
def test_find_not_cancelled_bookings_by_stock(app):
    # Given
    offerer = create_offerer()
    repository.save(offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
    user = create_user()
    cancelled_booking = create_booking(user=user, stock=stock, is_cancelled=True)
    validated_booking = create_booking(user=user, stock=stock, is_used=True)
    not_cancelled_booking = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False)
    repository.save(not_cancelled_booking, validated_booking, cancelled_booking)

    # When
    all_not_cancelled_bookings = booking_queries.find_not_cancelled_bookings_by_stock(stock)

    # Then
    assert set(all_not_cancelled_bookings) == {validated_booking, not_cancelled_booking}


class FindFinalOffererBookingsTest:
    @clean_database
    def test_returns_bookings_for_given_offerer(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
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
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer1.id)

        # Then
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    @clean_database
    def test_returns_bookings_with_payment_first_ordered_by_date_created(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user=user, date_created=FIVE_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, date_created=TWO_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking3 = create_booking(user=user, date_created=FOUR_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking4 = create_booking(user=user, date_created=THREE_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        payment1 = create_payment(booking4, offerer, 5)
        payment2 = create_payment(booking3, offerer, 5)
        repository.save(booking1, booking2, payment1, payment2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer.id)

        # Then
        assert bookings[0] == booking3
        assert bookings[1] == booking4
        assert bookings[2] == booking1
        assert bookings[3] == booking2

    @clean_database
    def test_returns_not_cancelled_bookings_for_offerer(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user=user, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=user, is_cancelled=True, is_used=True, stock=stock, venue=venue)
        repository.save(booking1, booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings

    @clean_database
    def test_returns_only_used_bookings(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_offer = create_offer_with_thing_product(venue)
        thing_stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
        thing_booking1 = create_booking(user=user, is_used=True, stock=thing_stock, venue=venue)
        thing_booking2 = create_booking(user=user, is_used=False, stock=thing_stock, venue=venue)
        repository.save(thing_booking1, thing_booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 1
        assert thing_booking1 in bookings

    @clean_database
    def test_does_not_return_finished_for_more_than_the_automatic_refund_delay_bookings(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        in_the_past_less_than_automatic_refund_delay = datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY + timedelta(
            days=1)
        in_the_past_more_than_automatic_refund_delay = datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY

        event_stock_finished_more_than_automatic_refund_delay_ago = \
            create_stock_with_event_offer(offerer=offerer,
                                          venue=venue,
                                          beginning_datetime=in_the_past_more_than_automatic_refund_delay,
                                          booking_limit_datetime=in_the_past_more_than_automatic_refund_delay)
        event_stock_finished_less_than_automatic_refund_delay_ago = \
            create_stock_with_event_offer(offerer=offerer,
                                          venue=venue,
                                          beginning_datetime=in_the_past_less_than_automatic_refund_delay,
                                          booking_limit_datetime=in_the_past_less_than_automatic_refund_delay)
        event_booking1 = create_booking(user=user, is_used=False,
                                        stock=event_stock_finished_more_than_automatic_refund_delay_ago, venue=venue)
        event_booking2 = create_booking(user=user, is_used=False,
                                        stock=event_stock_finished_less_than_automatic_refund_delay_ago, venue=venue)
        repository.save(event_booking1, event_booking2)

        # When
        bookings = booking_queries.find_eligible_bookings_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 0


class FindFinalVenueBookingsTest:
    @clean_database
    def test_returns_bookings_for_given_venue_ordered_by_date_created(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
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
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_eligible_bookings_for_venue(venue1.id)

        # Then
        assert len(bookings) == 2
        assert bookings[0] == booking1
        assert bookings[1] == booking2
        assert booking3 not in bookings


class FindDateUsedTest:
    @clean_database
    def test_returns_date_used_if_not_none(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user, date_used=datetime(2018, 2, 12), is_used=True)
        repository.save(booking)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used == datetime(2018, 2, 12)

    @clean_database
    def test_returns_none_when_date_used_is_none(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user)
        repository.save(booking)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used is None

    @clean_database
    def test_find_date_used_on_booking_returns_none_if_no_update_recorded_in_activity_table(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user)
        repository.save(booking)
        activity_insert = create_booking_activity(booking, 'booking', 'insert', issued_at=datetime(2018, 1, 28))
        save_all_activities(activity_insert)

        # when
        date_used = booking_queries.find_date_used(booking)

        # then
        assert date_used is None


class FindUserActivationBookingTest:
    @clean_database
    def test_returns_activation_thing_booking_linked_to_user(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, price=0, quantity=200)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        repository.save(activation_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @clean_database
    def test_returns_activation_event_booking_linked_to_user(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_event_product(
            venue_online, event_type=EventType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, price=0, quantity=200)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        repository.save(activation_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @clean_database
    def test_returns_false_is_no_booking_exists_on_such_stock(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        book_booking = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(book_booking)

        # when
        booking = booking_queries.find_user_activation_booking(user)

        # then
        assert booking is None


class GetExistingTokensTest:
    @clean_database
    def test_returns_a_set_of_tokens(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        booking1 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking2 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(booking1, booking2, booking3)

        # when
        tokens = booking_queries.find_existing_tokens()

        # then
        assert tokens == {booking1.token, booking2.token, booking3.token}

    @clean_database
    def test_returns_an_empty_set_if_no_bookings(self, app: fixture):
        # when
        tokens = booking_queries.find_existing_tokens()

        # then
        assert tokens == set()


class FindByTest:
    class ByTokenTest:
        @clean_database
        def test_returns_booking_if_token_is_known(self, app: fixture):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token)

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_unknown(self, app: fixture):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_queries.find_by('UNKNOWN')

            # then
            assert resource_not_found_error.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailTest:
        @clean_database
        def test_returns_booking_if_token_and_email_are_known(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_case_insensitively(self, app: fixture):
            # given
            user = create_user(email='USer@eXAMple.COm')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='USER@example.COM')

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_is_known_and_email_is_known_with_trailing_spaces(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='   user@example.com  ')

            # then
            assert result.id == booking.id

        @clean_database
        def test_raises_an_exception_if_token_is_known_but_email_is_unknown(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_queries.find_by(booking.token, email='other.user@example.com')

            # then
            assert resource_not_found_error.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailAndOfferIdTest:
        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_thing_are_known(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com',
                                             offer_id=stock.offer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_and_offer_id_for_event_are_known(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)

            # when
            result = booking_queries.find_by(booking.token, email='user@example.com',
                                             offer_id=stock.offer.id)

            # then
            assert result.id == booking.id

        @clean_database
        def test_returns_booking_if_token_and_email_are_known_but_offer_id_is_unknown(self, app: fixture):
            # given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_queries.find_by(
                    booking.token, email='user@example.com', offer_id=1234)

            # then
            assert resource_not_found_error.value.errors['global'] == [
                "Cette contremarque n'a pas été trouvée"]


class SaveBookingTest:
    @clean_database
    def test_saves_booking_when_enough_stocks_after_cancellation(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, quantity=1)
        user_cancelled = create_user(email='cancelled@example.com')
        user_booked = create_user(email='booked@example.com')
        cancelled_booking = create_booking(user=user_cancelled, stock=stock, is_cancelled=True)
        repository.save(cancelled_booking)
        booking = create_booking(user=user_booked, stock=stock, is_cancelled=False)

        # When
        repository.save(booking)

        # Then
        assert BookingSQLEntity.query.filter_by(isCancelled=False).count() == 1
        assert BookingSQLEntity.query.filter_by(isCancelled=True).count() == 1

    @clean_database
    def test_raises_too_many_bookings_error_when_not_enough_stocks(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, quantity=1)
        user1 = create_user(email='cancelled@example.com')
        user2 = create_user(email='booked@example.com')
        booking1 = create_booking(user=user1, stock=stock, is_cancelled=False)
        repository.save(booking1)
        booking2 = create_booking(user=user2, stock=stock, is_cancelled=False)

        # When
        with pytest.raises(ApiErrors) as api_errors:
            repository.save(booking2)

        # Then
        assert api_errors.value.errors['global'] == [
            'La quantité disponible pour cette offre est atteinte.']


class CountNonCancelledBookingsTest:
    @clean_database
    def test_returns_1_if_one_user_has_one_non_cancelled_booking(self, app: fixture):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        repository.save(booking)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 1

    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app: fixture):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        repository.save(booking)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 0

    @clean_database
    def test_returns_zero_if_two_users_have_activation_booking(self, app: fixture):
        # Given
        user1 = create_user()
        user2 = create_user(email='user2@example.com')
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
        repository.save(booking1, booking2)

        # When
        count = booking_queries.count_non_cancelled()

        # Then
        assert count == 0


class CountNonCancelledBookingsByDepartementTest:
    @clean_database
    def test_returns_1_if_one_user_has_one_non_cancelled_booking(self, app: fixture):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        repository.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 1

    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app: fixture):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        repository.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 0

    @clean_database
    def test_returns_0_if_user_comes_from_wrong_departement(self, app: fixture):
        # Given
        user_having_booked = create_user(departement_code='76')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        repository.save(booking)

        # When
        count = booking_queries.count_non_cancelled_by_departement('81')

        # Then
        assert count == 0

    @clean_database
    def test_returns_zero_if_users_only_have_activation_bookings(self, app: fixture):
        # Given
        user1 = create_user(departement_code='76')
        user2 = create_user(departement_code='76', email='user2@example.com')
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
        repository.save(booking1, booking2)

        # When
        count = booking_queries.count_non_cancelled_by_departement('76')

        # Then
        assert count == 0


class GetAllCancelledBookingsCountTest:
    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(offer=event_offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=event_stock, is_cancelled=False)
        repository.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_1_if_one_cancelled_bookings(self, app: fixture):
        # Given
        beginning_datetime = datetime.utcnow() + timedelta(hours=4)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(beginning_datetime=beginning_datetime, offer=event_offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=event_stock, is_cancelled=True)
        repository.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_zero_if_only_activation_offers(self, app: fixture):
        # Given
        beginning_datetime = datetime.utcnow() + timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(
            venue, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_thing_product(
            venue, thing_type=ThingType.ACTIVATION)
        stock1 = create_stock(beginning_datetime=beginning_datetime, offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=True)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=True)
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_cancelled()

        # Then
        assert number_of_bookings == 0


class GetAllCancelledBookingsByDepartementCountTest:
    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app: fixture):
        # Given
        beginning_datetime = datetime.utcnow() + timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(beginning_datetime=beginning_datetime, offer=event_offer, price=0)
        user = create_user(departement_code='76')
        booking = create_booking(user=user, stock=event_stock, is_cancelled=False)
        repository.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('76')

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_1_if_one_cancelled_bookings(self, app: fixture):
        # Given
        beginning_datetime = datetime.utcnow() + timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(beginning_datetime=beginning_datetime, offer=event_offer, price=0)
        user = create_user(departement_code='76')
        booking = create_booking(user=user, stock=event_stock, is_cancelled=True)
        repository.save(booking)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('76')

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_1_when_filtered_on_user_departement(self, app: fixture):
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
        repository.save(booking1, booking2, booking3)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('41')

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_zero_if_only_activation_bookings(self, app: fixture):
        # Given
        user = create_user(departement_code='41')
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
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_cancelled_by_departement('41')

        # Then
        assert number_of_bookings == 0


class CountAllBookingsTest:
    @clean_database
    def test_returns_0_when_no_bookings(self, app: fixture):
        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_0_when_bookings_are_on_activation_offer(self, app: fixture):
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
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count()

        # Then
        assert number_of_bookings == 0


class CountBookingsByDepartementTest:
    @clean_database
    def test_returns_0_when_no_bookings(self, app: fixture):
        # When
        number_of_bookings = booking_queries.count_by_departement('74')

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user(departement_code='74')
        booking1 = create_booking(user=user, stock=stock)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=True)
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('74')

        # Then
        assert number_of_bookings == 2

    @clean_database
    def test_returns_1_when_bookings_are_filtered_by_departement(self, app: fixture):
        # Given
        user_in_76 = create_user(departement_code='76', email='user-76@example.net')
        user_in_41 = create_user(departement_code='41', email='user-41@example.net')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(user=user_in_76, stock=stock)
        booking2 = create_booking(user=user_in_41, stock=stock, is_cancelled=True)
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('76')

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_returns_0_when_bookings_are_on_activation_offers(self, app: fixture):
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
        repository.save(booking1, booking2)

        # When
        number_of_bookings = booking_queries.count_by_departement('76')

        # Then
        assert number_of_bookings == 0


class FindAllNotUsedAndNotCancelledTest:
    @clean_database
    def test_return_no_booking_if_only_used(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, date_used=datetime(2019, 10, 12), is_used=True, stock=stock)
        repository.save(booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_no_booking_if_only_cancelled(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, is_cancelled=True, stock=stock)
        repository.save(booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_no_booking_if_used_but_cancelled(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, is_cancelled=True, is_used=True, stock=stock)
        repository.save(booking)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @clean_database
    def test_return_1_booking_if_not_used_and_not_cancelled(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking1 = create_booking(user=user, is_cancelled=False, is_used=False, stock=stock)
        booking2 = create_booking(user=user, is_used=True, stock=stock)
        booking3 = create_booking(user=user, is_cancelled=True, stock=stock)
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled()

        # Then
        assert bookings == [booking1]


class GetValidBookingsByUserId:
    @clean_database
    def test_should_return_bookings_by_user_id(self, app: fixture):
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
        repository.save(booking1, booking2)

        # When
        bookings = booking_queries.find_user_bookings_for_recommendation(user1.id)

        # Then
        assert bookings == [booking1]

    @clean_database
    def test_should_return_bookings_when_there_is_one_cancelled_booking(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        offer2 = create_offer_with_event_product(venue)
        stock2 = create_stock(offer=offer2)
        booking1 = create_booking(user=user, is_cancelled=True, stock=stock)
        booking2 = create_booking(user=user, is_cancelled=False, stock=stock)
        booking3 = create_booking(user=user, is_cancelled=False, stock=stock2)
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_user_bookings_for_recommendation(user.id)

        # Then
        assert booking1 not in bookings

    @clean_database
    def test_should_return_most_recent_booking_when_two_cancelled_on_same_stock(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking1 = create_booking(user=user, date_created=TWO_DAYS_AGO, is_cancelled=True, stock=stock)
        booking2 = create_booking(user=user, date_created=THREE_DAYS_AGO, is_cancelled=True, stock=stock)
        repository.save(booking1, booking2)

        # When
        bookings = booking_queries.find_user_bookings_for_recommendation(user.id)

        # Then
        assert bookings == [booking1]

    @clean_database
    def test_should_return_bookings_ordered_by_beginning_date_time_ascendant(self, app: fixture):
        # Given
        two_days = NOW + timedelta(days=2, hours=10)
        two_days_bis = NOW + timedelta(days=2, hours=20)
        three_days = NOW + timedelta(days=3)
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(venue)
        stock1 = create_stock(beginning_datetime=three_days, booking_limit_datetime=NOW, offer=offer1)
        offer2 = create_offer_with_event_product(venue)
        stock2 = create_stock(beginning_datetime=two_days, booking_limit_datetime=NOW, offer=offer2)
        offer3 = create_offer_with_event_product(venue)
        stock3 = create_stock(beginning_datetime=two_days_bis, booking_limit_datetime=NOW, offer=offer3)
        booking1 = create_booking(user=user, stock=stock1,
                                  recommendation=create_recommendation(user=user, offer=offer1))
        booking2 = create_booking(user=user, stock=stock2,
                                  recommendation=create_recommendation(user=user, offer=offer2))
        booking3 = create_booking(user=user, stock=stock3,
                                  recommendation=create_recommendation(user=user, offer=offer3))
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_user_bookings_for_recommendation(user.id)

        # Then
        assert bookings == [booking1, booking3, booking2]


class FindNotUsedAndNotCancelledBookingsAssociatedToOutdatedStocksTest:
    @clean_database
    @freeze_time('2020-01-10')
    def test_should_return_bookings_which_are_not_cancelled(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, quantity=10)
        booking1 = create_booking(user=user, is_cancelled=False, stock=stock)
        booking2 = create_booking(user=user, is_cancelled=True, stock=stock)
        repository.save(booking1, booking2)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock()

        # Then
        assert booking1 in bookings
        assert booking2 not in bookings

    @clean_database
    @freeze_time('2020-01-10')
    def test_should_return_bookings_which_are_not_used(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, quantity=10)
        booking1 = create_booking(user=user, is_used=False, stock=stock)
        booking2 = create_booking(user=user, is_used=True, stock=stock)
        repository.save(booking1, booking2)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock()

        # Then
        assert booking1 in bookings
        assert booking2 not in bookings

    @clean_database
    @freeze_time('2020-01-10')
    def test_should_return_bookings_associated_to_outdated_stock(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        outdated_stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, quantity=10)
        valid_stock = create_stock(beginning_datetime=datetime(2020, 1, 30), offer=offer, quantity=10)
        booking1 = create_booking(user=user, is_used=False, is_cancelled=False, stock=outdated_stock)
        booking2 = create_booking(user=user, is_used=False, is_cancelled=False, stock=outdated_stock)
        booking3 = create_booking(user=user, is_used=False, is_cancelled=False, stock=valid_stock)
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_queries.find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock()

        # Then
        assert booking1 in bookings
        assert booking2 in bookings
        assert booking3 not in bookings


class FindByTokenTest:
    @clean_database
    def test_should_return_a_booking_when_valid_token_is_given(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token='123456', is_used=True)
        repository.save(valid_booking)

        # When
        booking = booking_queries.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking == valid_booking

    @clean_database
    def test_should_return_nothing_when_invalid_token_is_given(self, app: fixture):
        # Given
        invalid_token = 'fake_token'
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token='123456', is_used=True)
        repository.save(valid_booking)

        # When
        booking = booking_queries.find_used_by_token(token=invalid_token)

        # Then
        assert booking is None

    @clean_database
    def test_should_return_nothing_when_valid_token_is_given_but_its_not_used(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token='123456', is_used=False)
        repository.save(valid_booking)

        # When
        booking = booking_queries.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking is None


class IsOfferAlreadyBookedByUserTest:
    @clean_database
    def test_should_return_true_when_booking_exists_for_user_and_offer(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user=user, stock=stock)
        repository.save(booking)

        # When
        is_offer_already_booked = booking_queries.is_offer_already_booked_by_user(user.id, offer)

        # Then
        assert is_offer_already_booked

    @clean_database
    def test_should_return_false_when_no_booking_exists_for_same_user_and_offer(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        repository.save(offer)

        # When
        is_offer_already_booked = booking_queries.is_offer_already_booked_by_user(user.id, offer)

        # Then
        assert not is_offer_already_booked

    @clean_database
    def test_should_return_false_when_there_is_a_booking_on_offer_but_from_different_user(self, app: fixture):
        # Given
        user = create_user()
        user2 = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        repository.save(offer)

        # When
        is_offer_already_booked = booking_queries.is_offer_already_booked_by_user(user2.id, offer)

        # Then
        assert not is_offer_already_booked

    @clean_database
    def test_should_return_false_when_a_booking_exists_for_same_user_and_offer_but_is_cancelled(self,
                                                                                                app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user=user, stock=stock, is_cancelled=True)
        repository.save(booking)

        # When
        is_offer_already_booked = booking_queries.is_offer_already_booked_by_user(user.id, offer)

        # Then
        assert not is_offer_already_booked


class CountNotCancelledBookingsQuantityByStocksTest:
    @clean_database
    def test_should_return_sum_of_bookings_quantity_that_are_not_cancelled_for_given_stock(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, quantity=20)

        booking1 = create_booking(user=user, is_cancelled=True, stock=stock, quantity=2)
        booking2 = create_booking(user=user, is_cancelled=False, stock=stock, quantity=7)
        booking3 = create_booking(user=user, is_cancelled=False, stock=stock, quantity=8)
        repository.save(booking1, booking2, booking3)

        # When
        result = booking_queries.count_not_cancelled_bookings_quantity_by_stock_id(stock.id)

        # Then
        assert result == 15

    @clean_database
    def test_should_return_0_when_no_bookings_found(self, app: fixture):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)

        repository.save(stock)

        # When
        result = booking_queries.count_not_cancelled_bookings_quantity_by_stock_id(stock.id)

        # Then
        assert result == 0

    def test_should_return_0_when_no_stock_id_given(self, app: fixture):
        # When
        result = booking_queries.count_not_cancelled_bookings_quantity_by_stock_id(None)

        # Then
        assert result == 0


class FindByProUserIdTest:
    @clean_database
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com', first_name='Ron', last_name='Weasley')
        create_deposit(beneficiary, 500)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name='Harry Potter')
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=booking_date,
                                 token='ABCDEF', is_used=True, amount=12)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == 'Harry Potter'
        assert expected_booking_recap.offerer_name == offerer.name
        assert expected_booking_recap.beneficiary_firstname == 'Ron'
        assert expected_booking_recap.beneficiary_lastname == 'Weasley'
        assert expected_booking_recap.beneficiary_email == 'beneficiary@example.com'
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz('Europe/Paris'))
        assert expected_booking_recap.booking_token == 'ABCDEF'
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_is_duo is False
        assert expected_booking_recap.venue_identifier == venue.id
        assert expected_booking_recap.booking_amount == 12
        assert expected_booking_recap.booking_status_history.booking_date == booking_date.astimezone(
            tz.gettz('Europe/Paris'))
        assert expected_booking_recap.venue_is_virtual == venue.isVirtual

    @clean_database
    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=beneficiary, stock=stock, quantity=2)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    @clean_database
    def test_should_return_booking_with_reimbursed_when_a_payment_was_sent(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name='Harry Potter')
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token='ABCDEF',
                                 is_cancelled=True)
        payment = create_payment(booking=booking, offerer=offerer, status=TransactionStatus.SENT)
        repository.save(user_offerer, payment)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert not isinstance(expected_booking_recap, EventBookingRecap)
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == 'Harry Potter'
        assert expected_booking_recap.beneficiary_firstname == 'Ron'
        assert expected_booking_recap.beneficiary_lastname == 'Weasley'
        assert expected_booking_recap.beneficiary_email == 'beneficiary@example.com'
        assert expected_booking_recap.booking_date == yesterday.astimezone(tz.gettz('Europe/Paris'))
        assert expected_booking_recap.booking_token == 'ABCDEF'
        assert expected_booking_recap.booking_is_used is False
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_is_reimbursed is True

    @clean_database
    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx='15')
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token='ABCDEF')
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert isinstance(expected_booking_recap, EventBookingRecap)
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == stock.offer.name
        assert expected_booking_recap.beneficiary_firstname == 'Ron'
        assert expected_booking_recap.beneficiary_lastname == 'Weasley'
        assert expected_booking_recap.beneficiary_email == 'beneficiary@example.com'
        assert expected_booking_recap.booking_date == yesterday.astimezone(tz.gettz('Europe/Paris'))
        assert expected_booking_recap.booking_token == 'ABCDEF'
        assert expected_booking_recap.booking_is_used is False
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.event_beginning_datetime == stock.beginningDatetime.astimezone(
            tz.gettz('Europe/Paris'))
        assert expected_booking_recap.venue_identifier == venue.id

    @clean_database
    def test_should_return_payment_date_when_booking_has_been_reimbursed(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx='15')
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token='ABCDEF', amount=5,
                                 is_used=True, date_used=yesterday)
        payment = create_payment(booking=booking, offerer=offerer, amount=5, status=TransactionStatus.SENT,
                                 status_date=yesterday)
        repository.save(user_offerer, payment)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_reimbursed is True
        assert expected_booking_recap.booking_status_history.payment_date == yesterday.astimezone(
            tz.gettz('Europe/Paris'))

    @clean_database
    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx='15')
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token='ABCDEF', amount=5,
                                 is_used=True, date_used=yesterday, is_cancelled=True)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_status_history.cancellation_date is not None

    @clean_database
    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(self,
                                                                                                       app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx='15')
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token='ABCDEF', amount=5,
                                 is_used=True, date_used=yesterday, is_cancelled=False)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_status_history.date_used is not None

    @clean_database
    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        today = datetime.utcnow()
        booking = create_booking(user=beneficiary, stock=stock, token="ABCD", date_created=today)
        offerer2 = create_offerer(siren='8765432')
        user_offerer2 = create_user_offerer(user, offerer2)
        venue2 = create_venue(offerer2, siret='8765432098765')
        offer2 = create_offer_with_thing_product(venue2)
        stock2 = create_stock(offer=offer2, price=0)
        booking2 = create_booking(user=beneficiary, stock=stock2, token="FGHI", date_created=today)
        repository.save(user_offerer, user_offerer2, booking, booking2)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2

    @clean_database
    def test_should_return_bookings_from_first_page(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)

        today = datetime.utcnow()
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, token="ABCD", date_created=yesterday)
        booking2 = create_booking(user=beneficiary, stock=stock, token="FGHI", date_created=today)
        repository.save(user_offerer, booking, booking2)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id, page=1, per_page_limit=1)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking2.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 2
        assert bookings_recap_paginated.total == 2

    @clean_database
    def test_should_return_bookings_from_second_page(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)

        today = datetime.utcnow()
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, token="ABCD", date_created=yesterday)
        booking2 = create_booking(user=beneficiary, stock=stock, token="FGHI", date_created=today)
        repository.save(user_offerer, booking, booking2)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id, page=2, per_page_limit=1)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.page == 2
        assert bookings_recap_paginated.pages == 2
        assert bookings_recap_paginated.total == 2

    @clean_database
    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer, validation_token='token')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=beneficiary, stock=stock)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap == []

    @clean_database
    def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_duo=True)
        stock = create_stock(beginning_datetime=datetime.utcnow(), offer=offer, price=0)

        today = datetime.utcnow()
        booking = create_booking(idx=2, user=beneficiary, stock=stock, token="FGHI", date_created=today)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id, page=1, per_page_limit=4)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 1

    @clean_database
    def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_duo=True)
        stock = create_stock(beginning_datetime=datetime.utcnow(), offer=offer, price=0)

        today = datetime.utcnow()
        booking = create_booking(idx=2, user=beneficiary, stock=stock, token="FGHI", date_created=today, quantity=2)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id, page=1, per_page_limit=4)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.bookings_recap[1].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 2

    @clean_database
    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer(postal_code='97300')
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15, is_virtual=True, siret=None)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name='Harry Potter')
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=booking_date, token='ABCDEF', is_used=True)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz('America/Cayenne'))

    @clean_database
    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = create_user(email='beneficiary@example.com',
                                  first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer(postal_code='97300')
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(thing_name='Harry Potter', venue=venue,
                                                extra_data=dict({'isbn': '9876543234'}))
        stock = create_stock(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=booking_date, token='ABCDEF', is_used=True)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert isinstance(expected_booking_recap, BookBookingRecap)
        assert expected_booking_recap.offer_isbn == '9876543234'

    @clean_database
    def test_should_return_booking_with_venue_name_when_public_name_is_not_provided(self, app):
        # Given
        beneficiary = create_user(email='beneficiary@example.com', first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        venue_for_event = create_venue(offerer, idx=17, name="Lieu pour un événement", siret="11816909600069")
        offer_for_event = create_offer_with_event_product(
            event_name='Shutter Island',
            venue=venue_for_event,
        )
        stock_for_event = create_stock(offer=offer_for_event, price=0)
        booking_for_event = create_booking(user=beneficiary,
                                           stock=stock_for_event,
                                           date_created=datetime(2020, 1, 3),
                                           token='BBBBBB',
                                           is_used=True)
        venue_for_book = create_venue(offerer, idx=15, name="Lieu pour un livre", siret="41816609600069")
        offer_for_book = create_offer_with_thing_product(
            thing_name='Harry Potter',
            venue=venue_for_book,
            extra_data=dict({'isbn': '9876543234'})
        )
        stock_for_book = create_stock(offer=offer_for_book, price=0)
        booking_for_book = create_booking(user=beneficiary,
                                          stock=stock_for_book,
                                          date_created=datetime(2020, 1, 2),
                                          token='AAAAAA',
                                          is_used=True)

        venue_for_thing = create_venue(offerer, idx=16, name="Lieu pour un bien qui n'est pas un livre",
                                       siret="83994784300018")
        stock_for_thing = create_stock_with_thing_offer(
            offerer=offerer,
            venue=venue_for_thing,
            price=0,
            name='Harry Potter'
        )
        booking_for_thing = create_booking(user=beneficiary,
                                           stock=stock_for_thing,
                                           date_created=(datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)),
                                           token='ABCDEF',
                                           is_used=True)
        repository.save(user_offerer, booking_for_thing, booking_for_book, booking_for_event)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.name
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.name
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.name

    @clean_database
    def test_should_return_booking_with_venue_public_name_when_public_name_is_provided(self, app):
        # Given
        beneficiary = create_user(email='beneficiary@example.com', first_name='Ron', last_name='Weasley')
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        venue_for_event = create_venue(offerer, idx=17, name="Opéra paris", public_name="Super Opéra de Paris",
                                       siret="11816909600069")
        offer_for_event = create_offer_with_event_product(
            event_name='Shutter Island',
            venue=venue_for_event,
        )
        stock_for_event = create_stock(offer=offer_for_event, price=0)
        booking_for_event = create_booking(user=beneficiary,
                                           stock=stock_for_event,
                                           date_created=datetime(2020, 1, 3),
                                           token='BBBBBB',
                                           is_used=True)
        venue_for_book = create_venue(offerer, idx=15, name="Lieu pour un livre", public_name="Librairie Châtelet",
                                      siret="41816609600069")
        offer_for_book = create_offer_with_thing_product(
            thing_name='Harry Potter',
            venue=venue_for_book,
            extra_data=dict({'isbn': '9876543234'})
        )
        stock_for_book = create_stock(offer=offer_for_book, price=0)
        booking_for_book = create_booking(user=beneficiary,
                                          stock=stock_for_book,
                                          date_created=datetime(2020, 1, 2),
                                          token='AAAAAA',
                                          is_used=True)

        venue_for_thing = create_venue(offerer, idx=16, name="Lieu pour un bien qui n'est pas un livre",
                                       public_name="Guitar Center",
                                       siret="83994784300018")
        stock_for_thing = create_stock_with_thing_offer(
            offerer=offerer,
            venue=venue_for_thing,
            price=0,
            name='Harry Potter'
        )
        booking_for_thing = create_booking(user=beneficiary,
                                           stock=stock_for_thing,
                                           date_created=(datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)),
                                           token='ABCDEF',
                                           is_used=True)
        repository.save(user_offerer, booking_for_thing, booking_for_book, booking_for_event)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.publicName
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.publicName
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.publicName


class FindFirstMatchingFromOfferByUserTest:
    @clean_database
    def test_should_return_nothing_when_no_bookings(self, app: fixture):
        # Given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        repository.save(beneficiary, offer)

        # When
        booking = find_first_matching_from_offer_by_user(offer.id, beneficiary.id)

        # Then
        assert booking is None

    @clean_database
    def test_should_return_nothing_when_beneficiary_has_no_bookings(self, app: fixture):
        # Given
        beneficiary = create_user(idx=1)
        other_beneficiary = create_user(email='other_beneficiary@example.com', idx=2)
        create_deposit(user=other_beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock = create_stock(offer=offer)
        my_booking = create_booking(user=other_beneficiary, stock=stock, date_created=datetime(2020, 1, 1))
        repository.save(beneficiary, my_booking)

        # When
        booking = find_first_matching_from_offer_by_user(offer.id, beneficiary.id)

        # Then
        assert booking is None

    @clean_database
    def test_should_return_first_booking_for_user(self, app: fixture):
        # Given
        beneficiary = create_user(idx=1)
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock = create_stock(offer=offer)
        other_booking = create_booking(user=beneficiary, stock=stock, date_created=datetime(2020, 1, 3))
        my_booking = create_booking(user=beneficiary, stock=stock, date_created=datetime(2020, 1, 10))
        repository.save(beneficiary, other_booking, my_booking)

        # When
        booking = find_first_matching_from_offer_by_user(offer.id, beneficiary.id)

        # Then
        assert booking.userId == beneficiary.id
        assert booking.dateCreated == my_booking.dateCreated
