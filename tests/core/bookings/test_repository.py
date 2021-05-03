from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

from dateutil import tz
import pytest
from pytest import fixture

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.bookings.repository import find_by_pro_user_id
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.domain.booking_recap.booking_recap import BookBookingRecap
from pcapi.domain.booking_recap.booking_recap import EventBookingRecap
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
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
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.offer_type import ThingType
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


NOW = datetime.utcnow()
YESTERDAY = NOW - timedelta(days=1)
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


class FindPaymentEligibleBookingsForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_used_past_event_and_thing_bookings_ordered_by_date_created(self, app: fixture):
        # Given
        beneficiary = users_factories.UserFactory()

        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret=f"{offerer.siren}12345")
        past_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=TWO_DAYS_AGO, booking_limit_datetime=THREE_DAYS_AGO
        )
        future_event_stock = create_stock_with_event_offer(
            offerer=offerer, venue=venue, beginning_datetime=ONE_WEEK_FROM_NOW
        )
        past_event_booking = create_booking(
            user=beneficiary, is_used=True, stock=past_event_stock, venue=venue, date_created=YESTERDAY
        )
        future_event_booking = create_booking(user=beneficiary, is_used=True, stock=future_event_stock, venue=venue)
        thing_booking = create_booking(user=beneficiary, is_used=True, venue=venue, date_created=NOW)

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
    def test_find_not_used_and_not_cancelled(self):
        # Given
        booking = bookings_factories.BookingFactory()
        bookings_factories.BookingFactory(isCancelled=True)
        bookings_factories.BookingFactory(isUsed=True)

        # When
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert bookings == [booking]


class FindByTokenTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_a_booking_when_valid_token_is_given(self, app: fixture):
        # Given
        beneficiary = users_factories.UserFactory()

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
        beneficiary = users_factories.UserFactory()
        valid_booking = create_booking(user=beneficiary, token="123456", is_used=True)
        repository.save(valid_booking)

        # When
        booking = booking_repository.find_used_by_token(token=invalid_token)

        # Then
        assert booking is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_valid_token_is_given_but_its_not_used(self, app: fixture):
        # Given
        beneficiary = users_factories.UserFactory()
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
        user = users_factories.UserFactory()
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
        users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory(email="beneficiary@example.com", firstName="Ron", lastName="Weasley")
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory(email="beneficiary@example.com", firstName="Ron", lastName="Weasley")
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory(email="beneficiary@example.com", firstName="Ron", lastName="Weasley")
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory(email="beneficiary@example.com")
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        user = users_factories.UserFactory()
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
    def test_should_return_bookings_from_second_page_without_page_count(self, app: fixture):
        # Given
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        assert bookings_recap_paginated.pages == 0
        assert bookings_recap_paginated.total == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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
        beneficiary = users_factories.UserFactory()
        user = users_factories.UserFactory()
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


class FindSoonToBeExpiredBookingsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_only_soon_to_be_expired_bookings(self, app: fixture):
        # Given
        expired_creation_date = date.today() - timedelta(days=23)
        expired_creation_date = datetime.combine(expired_creation_date, time(12, 34, 17))
        non_expired_creation_date = date.today() - timedelta(days=24)
        non_expired_creation_date = datetime.combine(non_expired_creation_date, time(12, 34, 17))
        too_old_expired_creation_date = date.today() - timedelta(days=22)
        too_old_expired_creation_date = datetime.combine(too_old_expired_creation_date, time(12, 34, 17))

        expected_booking = bookings_factories.BookingFactory(
            dateCreated=expired_creation_date, stock__offer__product__type=str(ThingType.AUDIOVISUEL)
        )
        # offer type not expirable
        bookings_factories.BookingFactory(
            dateCreated=expired_creation_date, stock__offer__product__type=str(ThingType.LIVRE_AUDIO)
        )
        bookings_factories.BookingFactory(
            dateCreated=non_expired_creation_date, stock__offer__product__type=str(ThingType.AUDIOVISUEL)
        )
        bookings_factories.BookingFactory(
            dateCreated=too_old_expired_creation_date, stock__offer__product__type=str(ThingType.AUDIOVISUEL)
        )

        # When
        expired_bookings = booking_repository.find_soon_to_be_expiring_booking_ordered_by_user().all()

        # Then
        assert expired_bookings == [expected_booking]


class GetActiveBookingsQuantityForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.BookingFactory(quantity=2)
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(stock__offer__venue=venue)

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 3

    @pytest.mark.usefixtures("db_session")
    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offers_factories.VenueFactory()

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 0

    @pytest.mark.usefixtures("db_session")
    def test_excludes_confirmed_used_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue)
        bookings_factories.BookingFactory(isCancelled=True, stock__offer__venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.BookingFactory(confirmation_date=yesterday, quantity=2, stock__offer__venue=venue)

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1

    @pytest.mark.usefixtures("db_session")
    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        another_venue = offers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.BookingFactory(stock__offer__venue=another_venue)

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1


class GetValidatedBookingsQuantityForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_used_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.BookingFactory(isUsed=True, quantity=2)
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 3

    @pytest.mark.usefixtures("db_session")
    def test_return_confirmed_bookings_quantity_for_venue(self):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.BookingFactory(confirmation_date=yesterday, quantity=2)
        venue = booking.stock.offer.venue

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 2

    @pytest.mark.usefixtures("db_session")
    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offers_factories.VenueFactory()

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 0

    @pytest.mark.usefixtures("db_session")
    def test_excludes_unused_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory(isUsed=True)
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(isUsed=False, stock__offer__venue=venue)
        bookings_factories.BookingFactory(isCancelled=True, isUsed=True, stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 1

    @pytest.mark.usefixtures("db_session")
    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory(isUsed=True)
        venue = booking.stock.offer.venue
        another_venue = offers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=another_venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 1


class GetOffersBookedByFraudulentUsersTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_only_offers_booked_by_fraudulent_users(self):
        # Given
        fraudulent_beneficiary_user = users_factories.UserFactory(
            isBeneficiary=True, email="jesuisunefraude@example.com"
        )
        another_fraudulent_beneficiary_user = users_factories.UserFactory(
            isBeneficiary=True, email="jesuisuneautrefraude@example.com"
        )
        beneficiary_user = users_factories.UserFactory(isBeneficiary=True, email="jenesuispasunefraude@EXAmple.com")
        offer_booked_by_fraudulent_users = offers_factories.OfferFactory()
        offer_booked_by_non_fraudulent_users = offers_factories.OfferFactory()
        offer_booked_by_both = offers_factories.OfferFactory()

        bookings_factories.BookingFactory(
            user=fraudulent_beneficiary_user, stock__price=1, stock__offer=offer_booked_by_fraudulent_users
        )
        bookings_factories.BookingFactory(
            user=another_fraudulent_beneficiary_user, stock__price=1, stock__offer=offer_booked_by_both
        )
        bookings_factories.BookingFactory(user=beneficiary_user, stock__price=1, stock__offer=offer_booked_by_both)
        bookings_factories.BookingFactory(
            user=beneficiary_user, stock__price=1, stock__offer=offer_booked_by_non_fraudulent_users
        )

        # When
        offers = booking_repository.find_offers_booked_by_beneficiaries(
            [fraudulent_beneficiary_user, another_fraudulent_beneficiary_user]
        )

        # Then
        assert len(offers) == 2
        assert set(offers) == {offer_booked_by_both, offer_booked_by_fraudulent_users}


class FindBookingsByFraudulentUsersTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_only_bookings_by_fraudulent_users(self):
        # Given
        fraudulent_beneficiary_user = users_factories.UserFactory(
            isBeneficiary=True, email="jesuisunefraude@example.com"
        )
        another_fraudulent_beneficiary_user = users_factories.UserFactory(
            isBeneficiary=True, email="jesuisuneautrefraude@example.com"
        )
        beneficiary_user = users_factories.UserFactory(isBeneficiary=True, email="jenesuispasunefraude@EXAmple.com")
        offer_booked_by_fraudulent_users = offers_factories.OfferFactory()
        other_offer_booked_by_fraudulent_users = offers_factories.OfferFactory()
        offer_booked_by_non_fraudulent_users = offers_factories.OfferFactory()

        booking_booked_by_fraudulent_user = bookings_factories.BookingFactory(
            user=fraudulent_beneficiary_user, stock__price=1, stock__offer=offer_booked_by_fraudulent_users
        )
        another_booking_booked_by_fraudulent_user = bookings_factories.BookingFactory(
            user=another_fraudulent_beneficiary_user,
            stock__price=1,
            stock__offer=other_offer_booked_by_fraudulent_users,
        )
        bookings_factories.BookingFactory(
            user=beneficiary_user, stock__price=1, stock__offer=offer_booked_by_non_fraudulent_users
        )

        # When
        bookings = booking_repository.find_cancellable_bookings_by_beneficiaries(
            [fraudulent_beneficiary_user, another_fraudulent_beneficiary_user]
        )

        # Then
        assert len(bookings) == 2
        assert set(bookings) == {booking_booked_by_fraudulent_user, another_booking_booked_by_fraudulent_user}
