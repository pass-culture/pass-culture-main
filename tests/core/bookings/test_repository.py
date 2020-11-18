from datetime import datetime
from datetime import timedelta

from dateutil import tz
from freezegun import freeze_time
import pytest
from pytest import fixture

import pcapi.core.bookings.repository as booking_repository
from pcapi.core.bookings.repository import find_by_pro_user_id
from pcapi.core.bookings.repository import find_first_matching_from_offer_by_user
from pcapi.core.offers.models import EVENT_AUTOMATIC_REFUND_DELAY
from pcapi.domain.booking_recap.booking_recap import BookBookingRecap
from pcapi.domain.booking_recap.booking_recap import EventBookingRecap
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.model_creators.activity_creators import create_booking_activity
from pcapi.model_creators.activity_creators import save_all_activities
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_recommendation
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models import Booking
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


NOW = datetime.utcnow()
TWO_DAYS_AGO = NOW - timedelta(days=2)
THREE_DAYS_AGO = NOW - timedelta(days=3)
FOUR_DAYS_AGO = NOW - timedelta(days=4)
FIVE_DAYS_AGO = NOW - timedelta(days=5)
ONE_WEEK_FROM_NOW = NOW + timedelta(weeks=1)


@pytest.mark.usefixtures("db_session")
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
    all_ongoing_bookings = booking_repository.find_ongoing_bookings_by_stock(stock.id)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]


@pytest.mark.usefixtures("db_session")
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
    all_not_cancelled_bookings = booking_repository.find_not_cancelled_bookings_by_stock(stock)

    # Then
    assert set(all_not_cancelled_bookings) == {validated_booking, not_cancelled_booking}


class FindPaymentEligibleBookingsForOffererTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_used_past_event_and_thing_bookings(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)

        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret=f"{offerer.siren}12345")
        past_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=TWO_DAYS_AGO, booking_limit_datetime=THREE_DAYS_AGO
        )
        future_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=ONE_WEEK_FROM_NOW
        )
        past_event_booking = create_booking(user=beneficiary, is_used=True, stock=past_event_stock, venue=venue)
        future_event_booking = create_booking(user=beneficiary, is_used=True, stock=future_event_stock, venue=venue)
        thing_booking = create_booking(user=beneficiary, is_used=True, venue=venue)

        another_offerer = create_offerer(siren="987654321")
        another_venue = create_venue(another_offerer, siret=f"{another_offerer.siren}12345")
        another_thing_booking = create_booking(user=beneficiary, is_used=True, venue=another_venue)
        another_past_event_stock = create_stock_with_event_offer(
            offerer=another_offerer,
            venue=another_venue,
            beginning_datetime=TWO_DAYS_AGO,
            booking_limit_datetime=THREE_DAYS_AGO,
        )
        another_past_event_booking = create_booking(
            user=beneficiary, is_used=True, stock=another_past_event_stock, venue=venue
        )

        repository.save(
            past_event_booking, future_event_booking, thing_booking, another_thing_booking, another_past_event_booking
        )

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 2
        assert past_event_booking in bookings
        assert thing_booking in bookings

    @pytest.mark.usefixtures("db_session")
    def test_returns_bookings_with_payment_first_ordered_by_date_created(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user=beneficiary, date_created=FIVE_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=beneficiary, date_created=TWO_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking3 = create_booking(user=beneficiary, date_created=FOUR_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        booking4 = create_booking(user=beneficiary, date_created=THREE_DAYS_AGO, is_used=True, stock=stock, venue=venue)
        payment1 = create_payment(booking4, offerer, 5)
        payment2 = create_payment(booking3, offerer, 5)
        repository.save(booking1, booking2, payment1, payment2)

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        assert bookings[0] == booking3
        assert bookings[1] == booking4
        assert bookings[2] == booking1
        assert bookings[3] == booking2

    @pytest.mark.usefixtures("db_session")
    def test_returns_not_cancelled_bookings_for_offerer(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking1 = create_booking(user=beneficiary, is_used=True, stock=stock, venue=venue)
        booking2 = create_booking(user=beneficiary, is_cancelled=True, is_used=True, stock=stock, venue=venue)
        repository.save(booking1, booking2)

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 1
        assert booking1 in bookings

    @pytest.mark.usefixtures("db_session")
    def test_returns_only_used_bookings(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_offer = create_offer_with_thing_product(venue)
        thing_stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
        thing_booking1 = create_booking(user=beneficiary, is_used=True, stock=thing_stock, venue=venue)
        thing_booking2 = create_booking(user=beneficiary, is_used=False, stock=thing_stock, venue=venue)
        repository.save(thing_booking1, thing_booking2)

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 1
        assert thing_booking1 in bookings

    @freeze_time(datetime(2020, 7, 2, 14, 0, 0))
    @pytest.mark.usefixtures("db_session")
    def test_returns_only_before_today_past_event_bookings(self, app: fixture):
        # Given
        now = datetime.utcnow()
        this_morning = now - timedelta(hours=4)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        beneficiary = create_user()
        create_deposit(beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        yesterday_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=yesterday, booking_limit_datetime=yesterday
        )
        today_past_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=this_morning, booking_limit_datetime=yesterday
        )
        future_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=tomorrow, booking_limit_datetime=tomorrow
        )
        yesterday_event_booking = create_booking(
            user=beneficiary, is_used=True, stock=yesterday_event_stock, venue=venue
        )
        today_past_event_booking = create_booking(
            user=beneficiary, is_used=True, stock=today_past_event_stock, venue=venue
        )
        future_event_booking = create_booking(user=beneficiary, is_used=True, stock=future_event_stock, venue=venue)
        repository.save(yesterday_event_booking, today_past_event_booking, future_event_booking)

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        # assert len(bookings) == 1
        assert yesterday_event_booking in bookings
        assert today_past_event_booking not in bookings

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_finished_for_more_than_the_automatic_refund_delay_bookings(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        in_the_past_less_than_automatic_refund_delay = (
            datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY + timedelta(days=1)
        )
        in_the_past_more_than_automatic_refund_delay = datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY

        event_stock_finished_more_than_automatic_refund_delay_ago = create_stock_with_event_offer(
            offerer=offerer,
            venue=venue,
            beginning_datetime=in_the_past_more_than_automatic_refund_delay,
            booking_limit_datetime=in_the_past_more_than_automatic_refund_delay,
        )
        event_stock_finished_less_than_automatic_refund_delay_ago = create_stock_with_event_offer(
            offerer=offerer,
            venue=venue,
            beginning_datetime=in_the_past_less_than_automatic_refund_delay,
            booking_limit_datetime=in_the_past_less_than_automatic_refund_delay,
        )
        event_booking1 = create_booking(
            user=beneficiary,
            is_used=False,
            stock=event_stock_finished_more_than_automatic_refund_delay_ago,
            venue=venue,
        )
        event_booking2 = create_booking(
            user=beneficiary,
            is_used=False,
            stock=event_stock_finished_less_than_automatic_refund_delay_ago,
            venue=venue,
        )
        repository.save(event_booking1, event_booking2)

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_offerer(offerer.id)

        # Then
        assert len(bookings) == 0


class FindPaymentEligibleBookingsForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_used_past_event_and_thing_bookings_ordered_by_date_created(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)

        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret=f"{offerer.siren}12345")
        past_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=TWO_DAYS_AGO, booking_limit_datetime=THREE_DAYS_AGO
        )
        future_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=ONE_WEEK_FROM_NOW
        )
        past_event_booking = create_booking(user=beneficiary, is_used=True, stock=past_event_stock, venue=venue)
        future_event_booking = create_booking(user=beneficiary, is_used=True, stock=future_event_stock, venue=venue)
        thing_booking = create_booking(user=beneficiary, is_used=True, venue=venue)

        another_offerer = create_offerer(siren="987654321")
        another_venue = create_venue(another_offerer, siret=f"{another_offerer.siren}12345")
        another_thing_booking = create_booking(user=beneficiary, is_used=True, venue=another_venue)
        another_past_event_stock = create_stock_with_event_offer(
            offerer=another_offerer,
            venue=another_venue,
            beginning_datetime=TWO_DAYS_AGO,
            booking_limit_datetime=THREE_DAYS_AGO,
        )
        another_past_event_booking = create_booking(
            user=beneficiary, is_used=True, stock=another_past_event_stock, venue=venue
        )

        repository.save(
            past_event_booking, future_event_booking, thing_booking, another_thing_booking, another_past_event_booking
        )

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_venue(venue.id)

        # Then
        assert len(bookings) == 2
        assert bookings[0] == past_event_booking
        assert bookings[1] == thing_booking
        assert future_event_booking not in bookings


class FindDateUsedTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_date_used_if_not_none(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user, date_used=datetime(2018, 2, 12), is_used=True)
        repository.save(booking)

        # when
        date_used = booking_repository.find_date_used(booking)

        # then
        assert date_used == datetime(2018, 2, 12)

    @pytest.mark.usefixtures("db_session")
    def test_returns_none_when_date_used_is_none(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user)
        repository.save(booking)

        # when
        date_used = booking_repository.find_date_used(booking)

        # then
        assert date_used is None

    @pytest.mark.usefixtures("db_session")
    def test_find_date_used_on_booking_returns_none_if_no_update_recorded_in_activity_table(self, app: fixture):
        # given
        user = create_user()
        create_deposit(user)
        booking = create_booking(user=user)
        repository.save(booking)
        activity_insert = create_booking_activity(booking, "booking", "insert", issued_at=datetime(2018, 1, 28))
        save_all_activities(activity_insert)

        # when
        date_used = booking_repository.find_date_used(booking)

        # then
        assert date_used is None


class FindUserActivationBookingTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_activation_thing_booking_linked_to_user(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, price=0, quantity=200)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        repository.save(activation_booking)

        # when
        booking = booking_repository.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @pytest.mark.usefixtures("db_session")
    def test_returns_activation_event_booking_linked_to_user(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_offer_with_event_product(venue_online, event_type=EventType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, price=0, quantity=200)
        activation_booking = create_booking(user=user, stock=activation_stock, venue=venue_online)
        repository.save(activation_booking)

        # when
        booking = booking_repository.find_user_activation_booking(user)

        # then
        assert booking == activation_booking

    @pytest.mark.usefixtures("db_session")
    def test_returns_false_is_no_booking_exists_on_such_stock(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        book_booking = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(book_booking)

        # when
        booking = booking_repository.find_user_activation_booking(user)

        # then
        assert booking is None


class GetExistingTokensTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_a_set_of_tokens(self, app: fixture):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        booking1 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking2 = create_booking(user=user, stock=book_stock, venue=venue_online)
        booking3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(booking1, booking2, booking3)

        # when
        tokens = booking_repository.find_existing_tokens()

        # then
        assert tokens == {booking1.token, booking2.token, booking3.token}

    @pytest.mark.usefixtures("db_session")
    def test_returns_an_empty_set_if_no_bookings(self, app: fixture):
        # when
        tokens = booking_repository.find_existing_tokens()

        # then
        assert tokens == set()


class FindByTest:
    class ByTokenTest:
        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_is_known(self, app: fixture):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token)

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
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
                booking_repository.find_by("UNKNOWN")

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailTest:
        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_and_email_are_known(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token, email="user@example.com")

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_is_known_and_email_is_known_case_insensitively(self, app: fixture):
            # given
            user = create_user(email="USer@eXAMple.COm")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token, email="USER@example.COM")

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_is_known_and_email_is_known_with_trailing_spaces(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token, email="   user@example.com  ")

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
        def test_raises_an_exception_if_token_is_known_but_email_is_unknown(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_repository.find_by(booking.token, email="other.user@example.com")

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailAndOfferIdTest:
        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_and_email_and_offer_id_for_thing_are_known(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token, email="user@example.com", offer_id=stock.offer.id)

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_and_email_and_offer_id_for_event_are_known(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)

            # when
            result = booking_repository.find_by(booking.token, email="user@example.com", offer_id=stock.offer.id)

            # then
            assert result.id == booking.id

        @pytest.mark.usefixtures("db_session")
        def test_returns_booking_if_token_and_email_are_known_but_offer_id_is_unknown(self, app: fixture):
            # given
            user = create_user(email="user@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_repository.find_by(booking.token, email="user@example.com", offer_id=1234)

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]


class SaveBookingTest:
    @pytest.mark.usefixtures("db_session")
    def test_saves_booking_when_enough_stocks_after_cancellation(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, quantity=1)
        user_cancelled = create_user(email="cancelled@example.com")
        user_booked = create_user(email="booked@example.com")
        cancelled_booking = create_booking(user=user_cancelled, stock=stock, is_cancelled=True)
        repository.save(cancelled_booking)
        booking = create_booking(user=user_booked, stock=stock, is_cancelled=False)

        # When
        repository.save(booking)

        # Then
        assert Booking.query.filter_by(isCancelled=False).count() == 1
        assert Booking.query.filter_by(isCancelled=True).count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_raises_too_many_bookings_error_when_not_enough_stocks(self, app: fixture):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0, quantity=1)
        user1 = create_user(email="cancelled@example.com")
        user2 = create_user(email="booked@example.com")
        booking1 = create_booking(user=user1, stock=stock, is_cancelled=False)
        repository.save(booking1)
        booking2 = create_booking(user=user2, stock=stock, is_cancelled=False)

        # When
        with pytest.raises(ApiErrors) as api_errors:
            repository.save(booking2)

        # Then
        assert api_errors.value.errors["global"] == ["La quantité disponible pour cette offre est atteinte."]


class FindAllNotUsedAndNotCancelledTest:
    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert len(bookings) == 0

    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert bookings == [booking1]


class GetValidBookingsByUserId:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_bookings_by_user_id(self, app: fixture):
        # Given
        user1 = create_user(email="me@example.net")
        deposit1 = create_deposit(user1)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        user2 = create_user(email="fa@example.net")
        deposit2 = create_deposit(user2)
        booking1 = create_booking(user=user1, stock=stock)
        booking2 = create_booking(user=user2, stock=stock)
        repository.save(booking1, booking2)

        # When
        bookings = booking_repository.find_user_bookings_for_recommendation(user1.id)

        # Then
        assert bookings == [booking1]

    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_user_bookings_for_recommendation(user.id)

        # Then
        assert booking1 not in bookings

    @pytest.mark.usefixtures("db_session")
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
        bookings = booking_repository.find_user_bookings_for_recommendation(user.id)

        # Then
        assert bookings == [booking1]

    @pytest.mark.usefixtures("db_session")
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
        booking1 = create_booking(
            user=user, stock=stock1, recommendation=create_recommendation(user=user, offer=offer1)
        )
        booking2 = create_booking(
            user=user, stock=stock2, recommendation=create_recommendation(user=user, offer=offer2)
        )
        booking3 = create_booking(
            user=user, stock=stock3, recommendation=create_recommendation(user=user, offer=offer3)
        )
        repository.save(booking1, booking2, booking3)

        # When
        bookings = booking_repository.find_user_bookings_for_recommendation(user.id)

        # Then
        assert bookings == [booking1, booking3, booking2]


class FindByTokenTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_booking_when_valid_token_is_given(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token="123456", is_used=True)
        repository.save(valid_booking)

        # When
        booking = booking_repository.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking == valid_booking

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_invalid_token_is_given(self, app: fixture):
        # Given
        invalid_token = "fake_token"
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token="123456", is_used=True)
        repository.save(valid_booking)

        # When
        booking = booking_repository.find_used_by_token(token=invalid_token)

        # Then
        assert booking is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_valid_token_is_given_but_its_not_used(self, app: fixture):
        # Given
        beneficiary = create_user()
        create_deposit(beneficiary)
        valid_booking = create_booking(user=beneficiary, token="123456", is_used=False)
        repository.save(valid_booking)

        # When
        booking = booking_repository.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking is None


class CountNotCancelledBookingsQuantityByStocksTest:
    @pytest.mark.usefixtures("db_session")
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
        result = booking_repository.count_not_cancelled_bookings_quantity_by_stock_id(stock.id)

        # Then
        assert result == 15

    @pytest.mark.usefixtures("db_session")
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
        result = booking_repository.count_not_cancelled_bookings_quantity_by_stock_id(stock.id)

        # Then
        assert result == 0

    def test_should_return_0_when_no_stock_id_given(self, app: fixture):
        # When
        result = booking_repository.count_not_cancelled_bookings_quantity_by_stock_id(None)

        # Then
        assert result == 0


class FindByProUserIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        create_deposit(beneficiary, 500)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name="Harry Potter")
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(
            user=beneficiary, stock=stock, date_created=booking_date, token="ABCDEF", is_used=True, amount=12
        )
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == "Harry Potter"
        assert expected_booking_recap.offerer_name == offerer.name
        assert expected_booking_recap.beneficiary_firstname == "Ron"
        assert expected_booking_recap.beneficiary_lastname == "Weasley"
        assert expected_booking_recap.beneficiary_email == "beneficiary@example.com"
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.booking_token == "ABCDEF"
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_is_duo is False
        assert expected_booking_recap.venue_identifier == venue.id
        assert expected_booking_recap.booking_amount == 12
        assert expected_booking_recap.booking_status_history.booking_date == booking_date.astimezone(
            tz.gettz("Europe/Paris")
        )
        assert expected_booking_recap.venue_is_virtual == venue.isVirtual

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_with_reimbursed_when_a_payment_was_sent(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name="Harry Potter")
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(
            user=beneficiary, stock=stock, date_created=yesterday, token="ABCDEF", is_cancelled=True
        )
        payment = create_payment(booking=booking, offerer=offerer, status=TransactionStatus.SENT)
        repository.save(user_offerer, payment)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert not isinstance(expected_booking_recap, EventBookingRecap)
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == "Harry Potter"
        assert expected_booking_recap.beneficiary_firstname == "Ron"
        assert expected_booking_recap.beneficiary_lastname == "Weasley"
        assert expected_booking_recap.beneficiary_email == "beneficiary@example.com"
        assert expected_booking_recap.booking_date == yesterday.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.booking_token == "ABCDEF"
        assert expected_booking_recap.booking_is_used is False
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_is_reimbursed is True

    @pytest.mark.usefixtures("db_session")
    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx="15")
        stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, price=0, beginning_datetime=datetime.utcnow() + timedelta(hours=98)
        )
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=yesterday, token="ABCDEF")
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert isinstance(expected_booking_recap, EventBookingRecap)
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == stock.offer.name
        assert expected_booking_recap.beneficiary_firstname == "Ron"
        assert expected_booking_recap.beneficiary_lastname == "Weasley"
        assert expected_booking_recap.beneficiary_email == "beneficiary@example.com"
        assert expected_booking_recap.booking_date == yesterday.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.booking_token == "ABCDEF"
        assert expected_booking_recap.booking_is_used is False
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_is_confirmed is False
        assert expected_booking_recap.event_beginning_datetime == stock.beginningDatetime.astimezone(
            tz.gettz("Europe/Paris")
        )
        assert expected_booking_recap.venue_identifier == venue.id
        assert isinstance(expected_booking_recap.booking_status_history, BookingRecapHistory)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(
        self, app: fixture
    ):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx="15")
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)
        more_than_two_days_ago = datetime.utcnow() - timedelta(days=3)
        booking = create_booking(user=beneficiary, stock=stock, date_created=more_than_two_days_ago, token="ABCDEF")
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_confirmed is True
        assert isinstance(expected_booking_recap.booking_status_history, BookingRecapHistory)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payment_date_when_booking_has_been_reimbursed(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx="15")
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(
            user=beneficiary,
            stock=stock,
            date_created=yesterday,
            token="ABCDEF",
            amount=5,
            is_used=True,
            date_used=yesterday,
        )
        payment = create_payment(
            booking=booking, offerer=offerer, amount=5, status=TransactionStatus.SENT, status_date=yesterday
        )
        repository.save(user_offerer, payment)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_reimbursed is True
        assert expected_booking_recap.booking_status_history.payment_date == yesterday.astimezone(
            tz.gettz("Europe/Paris")
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx="15")
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(
            user=beneficiary,
            stock=stock,
            date_created=yesterday,
            token="ABCDEF",
            amount=5,
            is_used=True,
            date_used=yesterday,
            is_cancelled=True,
        )
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_status_history.cancellation_date is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(
        self, app: fixture
    ):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        create_deposit(beneficiary)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx="15")
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(
            user=beneficiary,
            stock=stock,
            date_created=yesterday,
            token="ABCDEF",
            amount=5,
            is_used=True,
            date_used=yesterday,
            is_cancelled=False,
        )
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_status_history.date_confirmed is not None
        assert expected_booking_recap.booking_status_history.date_used is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        today = datetime.utcnow()
        booking = create_booking(user=beneficiary, stock=stock, token="ABCD", date_created=today)
        offerer2 = create_offerer(siren="8765432")
        user_offerer2 = create_user_offerer(user, offerer2)
        venue2 = create_venue(offerer2, siret="8765432098765")
        offer2 = create_offer_with_thing_product(venue2)
        stock2 = create_stock(offer=offer2, price=0)
        booking2 = create_booking(user=beneficiary, stock=stock2, token="FGHI", date_created=today)
        repository.save(user_offerer, user_offerer2, booking, booking2)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2

    @pytest.mark.usefixtures("db_session")
    def test_should_return_bookings_from_first_page(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_bookings_from_second_page(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer, validation_token="token")
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=beneficiary, stock=stock)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap == []

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer(postal_code="97300")
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15, is_virtual=True, siret=None)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0, name="Harry Potter")
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=booking_date, token="ABCDEF", is_used=True)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("America/Cayenne"))

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer(postal_code="97300")
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, idx=15, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(
            thing_name="Harry Potter", venue=venue, extra_data=dict({"isbn": "9876543234"})
        )
        stock = create_stock(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = create_booking(user=beneficiary, stock=stock, date_created=booking_date, token="ABCDEF", is_used=True)
        repository.save(user_offerer, booking)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert isinstance(expected_booking_recap, BookBookingRecap)
        assert expected_booking_recap.offer_isbn == "9876543234"

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_with_venue_name_when_public_name_is_not_provided(self, app):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        venue_for_event = create_venue(offerer, idx=17, name="Lieu pour un événement", siret="11816909600069")
        offer_for_event = create_offer_with_event_product(
            event_name="Shutter Island",
            venue=venue_for_event,
        )
        stock_for_event = create_stock(offer=offer_for_event, price=0)
        booking_for_event = create_booking(
            user=beneficiary, stock=stock_for_event, date_created=datetime(2020, 1, 3), token="BBBBBB", is_used=True
        )
        venue_for_book = create_venue(offerer, idx=15, name="Lieu pour un livre", siret="41816609600069")
        offer_for_book = create_offer_with_thing_product(
            thing_name="Harry Potter", venue=venue_for_book, extra_data=dict({"isbn": "9876543234"})
        )
        stock_for_book = create_stock(offer=offer_for_book, price=0)
        booking_for_book = create_booking(
            user=beneficiary, stock=stock_for_book, date_created=datetime(2020, 1, 2), token="AAAAAA", is_used=True
        )

        venue_for_thing = create_venue(
            offerer, idx=16, name="Lieu pour un bien qui n'est pas un livre", siret="83994784300018"
        )
        stock_for_thing = create_stock_with_thing_offer(
            offerer=offerer, venue=venue_for_thing, price=0, name="Harry Potter"
        )
        booking_for_thing = create_booking(
            user=beneficiary,
            stock=stock_for_thing,
            date_created=(datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)),
            token="ABCDEF",
            is_used=True,
        )
        repository.save(user_offerer, booking_for_thing, booking_for_book, booking_for_event)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.name
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.name
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.name

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_with_venue_public_name_when_public_name_is_provided(self, app):
        # Given
        beneficiary = create_user(email="beneficiary@example.com", first_name="Ron", last_name="Weasley")
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        venue_for_event = create_venue(
            offerer, idx=17, name="Opéra paris", public_name="Super Opéra de Paris", siret="11816909600069"
        )
        offer_for_event = create_offer_with_event_product(
            event_name="Shutter Island",
            venue=venue_for_event,
        )
        stock_for_event = create_stock(offer=offer_for_event, price=0)
        booking_for_event = create_booking(
            user=beneficiary, stock=stock_for_event, date_created=datetime(2020, 1, 3), token="BBBBBB", is_used=True
        )
        venue_for_book = create_venue(
            offerer, idx=15, name="Lieu pour un livre", public_name="Librairie Châtelet", siret="41816609600069"
        )
        offer_for_book = create_offer_with_thing_product(
            thing_name="Harry Potter", venue=venue_for_book, extra_data=dict({"isbn": "9876543234"})
        )
        stock_for_book = create_stock(offer=offer_for_book, price=0)
        booking_for_book = create_booking(
            user=beneficiary, stock=stock_for_book, date_created=datetime(2020, 1, 2), token="AAAAAA", is_used=True
        )

        venue_for_thing = create_venue(
            offerer,
            idx=16,
            name="Lieu pour un bien qui n'est pas un livre",
            public_name="Guitar Center",
            siret="83994784300018",
        )
        stock_for_thing = create_stock_with_thing_offer(
            offerer=offerer, venue=venue_for_thing, price=0, name="Harry Potter"
        )
        booking_for_thing = create_booking(
            user=beneficiary,
            stock=stock_for_thing,
            date_created=(datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)),
            token="ABCDEF",
            is_used=True,
        )
        repository.save(user_offerer, booking_for_thing, booking_for_book, booking_for_event)

        # When
        bookings_recap_paginated = find_by_pro_user_id(user_id=user.id)

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.publicName
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.publicName
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.publicName


class FindFirstMatchingFromOfferByUserTest:
    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_beneficiary_has_no_bookings(self, app: fixture):
        # Given
        beneficiary = create_user(idx=1)
        other_beneficiary = create_user(email="other_beneficiary@example.com", idx=2)
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

    @pytest.mark.usefixtures("db_session")
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
