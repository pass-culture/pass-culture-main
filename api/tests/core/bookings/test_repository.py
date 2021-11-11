import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import StringIO

from dateutil import tz
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
from pytest import fixture

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.bookings.repository import get_bookings_from_deposit
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments.api import create_deposit
from pcapi.core.payments.factories import PaymentFactory
from pcapi.core.payments.factories import PaymentStatusFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.model_creators.generic_creators import create_payment
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import FeatureToggle
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.utils.date import utc_datetime_to_department_timezone


pytestmark = pytest.mark.usefixtures("db_session")


NOW = datetime.utcnow()
YESTERDAY = NOW - timedelta(days=1)
TWO_DAYS_AGO = NOW - timedelta(days=2)
THREE_DAYS_AGO = NOW - timedelta(days=3)
FOUR_DAYS_AGO = NOW - timedelta(days=4)
FIVE_DAYS_AGO = NOW - timedelta(days=5)
ONE_WEEK_FROM_NOW = NOW + timedelta(weeks=1)


def test_find_all_ongoing_bookings(app):
    # Given
    user = users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.StockFactory(price=0, quantity=10)
    bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user, stock=stock)
    bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, stock=stock)
    ongoing_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user, stock=stock)

    # When
    all_ongoing_bookings = booking_repository.find_ongoing_bookings_by_stock(stock.id)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]


def test_find_not_cancelled_bookings_by_stock(app):
    # Given
    user = users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.ThingStockFactory(price=0)
    bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user, stock=stock)
    used_booking = bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, stock=stock)
    not_cancelled_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user, stock=stock)

    # When
    all_not_cancelled_bookings = booking_repository.find_not_cancelled_bookings_by_stock(stock)

    # Then
    assert set(all_not_cancelled_bookings) == {used_booking, not_cancelled_booking}


class FindPaymentEligibleBookingsForVenueTest:
    def test_basics(self, app: fixture):
        # Given
        cutoff = datetime.now()
        before_cutoff = cutoff - timedelta(days=1)
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offerer = offers_factories.OffererFactory(siren="123456789")

        venue = offers_factories.VenueFactory(managingOfferer=offerer, siret=f"{offerer.siren}12345")
        offer = offers_factories.ThingOfferFactory(venue=venue)
        past_event_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=TWO_DAYS_AGO, bookingLimitDatetime=THREE_DAYS_AGO
        )
        future_event_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=ONE_WEEK_FROM_NOW)

        past_event_booking = bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=past_event_stock,
            dateCreated=YESTERDAY,
            dateUsed=before_cutoff - timedelta(seconds=2),
        )

        future_event_booking = bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=future_event_stock,
            dateCreated=YESTERDAY,
            dateUsed=before_cutoff,
        )

        offer_thing = offers_factories.ThingOfferFactory(venue=venue)
        stock_thing = offers_factories.ThingStockFactory(offer=offer_thing)
        thing_booking = bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_thing,
            dateCreated=NOW,
            dateUsed=before_cutoff - timedelta(seconds=1),
        )

        another_offerer = offers_factories.OffererFactory(siren="987654321")
        another_venue = offers_factories.VenueFactory(managingOfferer=offerer, siret=f"{another_offerer.siren}12345")
        another_offer = offers_factories.ThingOfferFactory(venue=another_venue)
        another_past_event_stock = offers_factories.ThingStockFactory(
            offer=another_offer, beginningDatetime=TWO_DAYS_AGO, bookingLimitDatetime=THREE_DAYS_AGO
        )
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=another_past_event_stock,
            dateCreated=NOW,
            dateUsed=before_cutoff,
        )

        # When
        bookings = booking_repository.find_bookings_eligible_for_payment_for_venue(venue.id, cutoff)

        # Then
        assert len(bookings) == 2
        assert bookings[0] == past_event_booking
        assert bookings[1] == thing_booking
        assert future_event_booking not in bookings

    def test_cutoff_date(self, app):
        venue = offers_factories.VenueFactory()
        cutoff = datetime.now()
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            dateUsed=cutoff - timedelta(days=1), stock__offer__venue=venue
        )
        bookings_factories.UsedIndividualBookingFactory(dateUsed=cutoff, stock__offer__venue=venue)

        bookings = booking_repository.find_bookings_eligible_for_payment_for_venue(venue.id, cutoff)
        assert bookings == [booking1]


class FindByTest:
    class ByTokenTest:
        def test_returns_booking_if_token_is_known(self, app: fixture):
            # given
            pro = users_factories.ProFactory()
            offerer = offers_factories.OffererFactory()
            offers_factories.UserOffererFactory(user=pro, offerer=offerer)

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            stock = offers_factories.ThingStockFactory(price=0)
            booking = bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock)

            # when
            result = booking_repository.find_by(booking.token)

            # then
            assert result.id == booking.id

        def test_raises_an_exception_if_token_is_unknown(self, app: fixture):
            # given
            pro = users_factories.ProFactory()
            offerer = offers_factories.OffererFactory()
            offers_factories.UserOffererFactory(user=pro, offerer=offerer)

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            stock = offers_factories.ThingStockFactory(price=0)
            bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock)

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_repository.find_by("UNKNOWN")

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailTest:
        def test_returns_booking_if_token_and_email_are_known(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory()

            # when
            result = booking_repository.find_by(booking.token, email=booking.individualBooking.user.email)

            # then
            assert result.id == booking.id

        def test_returns_booking_if_token_is_known_and_email_is_known_case_insensitively(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory(
                individualBooking__user__email="jeanne.doux@example.com"
            )

            # when
            result = booking_repository.find_by(booking.token, email="JeaNNe.DouX@exAMple.cOm")

            # then
            assert result.id == booking.id

        def test_returns_booking_if_token_is_known_and_email_is_known_with_trailing_spaces(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory(individualBooking__user__email="user@example.com")

            # when
            result = booking_repository.find_by(booking.token, email="   user@example.com  ")

            # then
            assert result.id == booking.id

        def test_raises_an_exception_if_token_is_known_but_email_is_unknown(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory()

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_repository.find_by(booking.token, email="other.user@example.com")

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]

    class ByTokenAndEmailAndOfferIdTest:
        def test_returns_booking_if_token_and_email_and_offer_id_for_thing_are_known(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory(stock=offers_factories.ThingStockFactory())

            # when
            result = booking_repository.find_by(booking.token, email=booking.email, offer_id=booking.stock.offer.id)

            # then
            assert result.id == booking.id

        def test_returns_booking_if_token_and_email_and_offer_id_for_event_are_known(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory(stock=offers_factories.EventStockFactory())

            # when
            result = booking_repository.find_by(booking.token, email=booking.email, offer_id=booking.stock.offer.id)

            # then
            assert result.id == booking.id

        def test_returns_booking_if_token_and_email_are_known_but_offer_id_is_unknown(self, app: fixture):
            # given
            booking = bookings_factories.IndividualBookingFactory()

            # when
            with pytest.raises(ResourceNotFoundError) as resource_not_found_error:
                booking_repository.find_by(booking.token, email=booking.email, offer_id=1234)

            # then
            assert resource_not_found_error.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]


class FindAllNotUsedAndNotCancelledTest:
    def test_find_not_used_and_not_cancelled(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        bookings_factories.CancelledIndividualBookingFactory()
        bookings_factories.UsedIndividualBookingFactory()

        # When
        bookings = booking_repository.find_not_used_and_not_cancelled()

        # Then
        assert bookings == [booking]


class FindByTokenTest:
    def test_should_return_a_booking_when_valid_token_is_given(self, app: fixture):
        # Given
        valid_booking = bookings_factories.UsedIndividualBookingFactory()

        # When
        booking = booking_repository.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking == valid_booking

    def test_should_return_nothing_when_invalid_token_is_given(self, app: fixture):
        # Given
        invalid_token = "fake_token"
        bookings_factories.UsedIndividualBookingFactory()

        # When
        booking = booking_repository.find_used_by_token(token=invalid_token)

        # Then
        assert booking is None

    def test_should_return_nothing_when_valid_token_is_given_but_its_not_used(self, app: fixture):
        # Given
        valid_booking = bookings_factories.IndividualBookingFactory()

        # When
        booking = booking_repository.find_used_by_token(token=valid_booking.token)

        # Then
        assert booking is None


default_booking_date = date.today()
one_year_before_booking = default_booking_date - timedelta(weeks=52)
one_year_after_booking = default_booking_date + timedelta(weeks=52)


class FindByProUserLegacyTest:
    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
            amount=12,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

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

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock, quantity=2)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(
        self, app: fixture
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.UserOffererFactory(offerer=offerer)

        bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_with_reimbursed_when_a_payment_was_sent(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=yesterday, token="ABCDEF", dateUsed=yesterday
        )
        payment = PaymentFactory(booking=booking)
        PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_used
        assert expected_booking_recap.booking_is_reimbursed

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
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

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        more_than_two_days_ago = datetime.utcnow() - timedelta(days=3)
        bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=more_than_two_days_ago, token="ABCDEF"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_confirmed is True
        assert isinstance(expected_booking_recap.booking_status_history, BookingRecapHistory)

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_payment_date_when_booking_has_been_reimbursed(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.EventProductFactory(name="Harry Potter")
        offer = offers_factories.EventOfferFactory(venue=venue, product=product)
        stock = offers_factories.EventStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        payment = create_payment(
            booking=booking, offerer=offerer, amount=5, status=TransactionStatus.SENT, status_date=yesterday
        )
        repository.save(payment, payment)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_reimbursed is True
        assert expected_booking_recap.booking_status_history.payment_date == yesterday.astimezone(
            tz.gettz("Europe/Paris")
        )

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.CancelledIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_status_history.cancellation_date is not None

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product)
        stock = offers_factories.EventStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_status_history.date_confirmed is not None
        assert expected_booking_recap.booking_status_history.date_used is not None

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, dateCreated=today, token="ABCD"
        )

        offerer2 = offers_factories.OffererFactory(siren="8765432")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        venue2 = offers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock2, dateCreated=today, token="FGHI"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_bookings_from_first_page(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, dateCreated=yesterday, token="ABCD"
        )
        booking2 = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=1
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking2.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 2
        assert bookings_recap_paginated.total == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_bookings_from_second_page_without_page_count(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(offer=offer, price=0)

        today = datetime.utcnow()
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, token="ABCD", dateCreated=yesterday
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, token="FGHI", dateCreated=today
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=2, per_page_limit=1
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.page == 2
        assert bookings_recap_paginated.pages == 0
        assert bookings_recap_paginated.total == 0

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert bookings_recap_paginated.bookings_recap == []

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
        stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
        today = datetime.utcnow()
        booking = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 1

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
        stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
        today = datetime.utcnow()
        booking = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI", quantity=2
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.bookings_recap[1].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("America/Cayenne"))

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_isbn == "9876543234"

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_with_venue_name_when_public_name_is_not_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un événement", siret="11816909600069"
        )
        product = offers_factories.EventProductFactory(name="Shutter Island")
        offer_for_event = offers_factories.EventOfferFactory(venue=venue_for_event, product=product)
        stock_for_event = offers_factories.EventStockFactory(offer=offer_for_event, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_event,
            dateCreated=(default_booking_date + timedelta(days=1)),
            token="BBBBBB",
        )

        venue_for_book = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un livre", siret="41816609600069"
        )
        product_book = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_book = offers_factories.ThingOfferFactory(
            venue=venue_for_book, product=product_book, extraData=dict({"isbn": "9876543234"})
        )
        stock_for_book = offers_factories.ThingStockFactory(offer=offer_for_book, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_book,
            dateCreated=default_booking_date,
            token="AAAAAA",
        )

        venue_for_thing = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un bien qui n'est pas un livre", siret="83994784300018"
        )
        product_thing = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_thing = offers_factories.ThingOfferFactory(venue=venue_for_thing, product=product_thing)
        stock_for_thing = offers_factories.ThingStockFactory(offer=offer_for_thing, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_thing,
            dateCreated=(default_booking_date - timedelta(days=1)),
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.name
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.name
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.name

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_booking_with_venue_public_name_when_public_name_is_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Opéra paris", publicName="Super Opéra de Paris", siret="11816909600069"
        )
        product = offers_factories.EventProductFactory(name="Shutter Island")
        offer_for_event = offers_factories.EventOfferFactory(venue=venue_for_event, product=product)
        stock_for_event = offers_factories.EventStockFactory(offer=offer_for_event, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_event,
            dateCreated=(default_booking_date + timedelta(days=1)),
            token="BBBBBB",
        )

        venue_for_book = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un livre", publicName="Librairie Châtelet", siret="41816609600069"
        )
        product_book = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_book = offers_factories.ThingOfferFactory(
            venue=venue_for_book, product=product_book, extraData=dict({"isbn": "9876543234"})
        )
        stock_for_book = offers_factories.ThingStockFactory(offer=offer_for_book, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_book,
            dateCreated=default_booking_date,
            token="AAAAAA",
        )

        venue_for_thing = offers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Lieu pour un bien qui n'est pas un livre",
            publicName="Guitar Center",
            siret="83994784300018",
        )
        product_thing = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_thing = offers_factories.ThingOfferFactory(venue=venue_for_thing, product=product_thing)
        stock_for_thing = offers_factories.ThingStockFactory(offer=offer_for_thing, price=0)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock_for_thing,
            dateCreated=(default_booking_date - timedelta(days=1)),
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert bookings_recap_paginated.bookings_recap[0].venue_name == venue_for_event.publicName
        assert bookings_recap_paginated.bookings_recap[1].venue_name == venue_for_book.publicName
        assert bookings_recap_paginated.bookings_recap[2].venue_name == venue_for_thing.publicName

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_only_booking_for_requested_venue(self, app: fixture):
        # Given
        pro_user = users_factories.ProFactory()
        user_offerer = offers_factories.UserOffererFactory(user=pro_user)

        bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        booking_two = bookings_factories.IndividualBookingFactory(
            stock__offer__venue__managingOfferer=user_offerer.offerer
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro_user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            venue_id=booking_two.venue.id,
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_identifier == booking_two.stock.offer.id
        assert expected_booking_recap.offer_name == booking_two.stock.offer.name
        assert expected_booking_recap.venue_identifier == booking_two.venue.id
        assert expected_booking_recap.booking_amount == booking_two.amount

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_only_booking_for_requested_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_date = datetime(2020, 12, 24, 10, 30)
        expected_booking = bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=event_date, offer__venue__managingOfferer=user_offerer.offerer
            )
        )
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_date.date(),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert resulting_booking_recap.booking_token == expected_booking.token

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_datetime = datetime(2020, 4, 21, 20, 00)

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime
        )
        cayenne_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_cayenne)

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime
        )
        mayotte_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_mayotte)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_datetime.date(),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
        assert cayenne_booking.token in bookings_tokens
        assert mayotte_booking.token in bookings_tokens

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def test_should_return_only_bookings_for_requested_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
        booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
        expected_booking = bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 26, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 29, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 22, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_beginning_period, booking_ending_period),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert resulting_booking_recap.booking_date == utc_datetime_to_department_timezone(
            expected_booking.dateCreated, expected_booking.venue.departementCode
        )

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: False})
    def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        requested_booking_period_beginning = datetime(2020, 4, 21, 20, 00).date()
        requested_booking_period_ending = datetime(2020, 4, 22, 20, 00).date()

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_booking_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne,
        )
        cayenne_booking = bookings_factories.IndividualBookingFactory(
            stock=stock_in_cayenne, dateCreated=cayenne_booking_datetime
        )

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_booking_datetime = datetime(2020, 4, 20, 23, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte,
        )
        mayotte_booking = bookings_factories.IndividualBookingFactory(
            stock=stock_in_mayotte, dateCreated=mayotte_booking_datetime
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
        assert cayenne_booking.token in bookings_tokens
        assert mayotte_booking.token in bookings_tokens


class FindByProUserTest:
    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
            amount=12,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_identifier == stock.offer.id
        assert expected_booking_recap.offer_name == "Harry Potter"
        assert expected_booking_recap.beneficiary_firstname == "Ron"
        assert expected_booking_recap.beneficiary_lastname == "Weasley"
        assert expected_booking_recap.beneficiary_email == "beneficiary@example.com"
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.booking_token == "ABCDEF"
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_is_duo is False
        assert expected_booking_recap.booking_amount == 12
        assert expected_booking_recap.booking_status_history.booking_date == booking_date.astimezone(
            tz.gettz("Europe/Paris")
        )

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, quantity=2)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(
        self, app: fixture
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.UserOffererFactory(offerer=offerer)

        bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            status=BookingStatus.PENDING,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
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
        assert isinstance(expected_booking_recap.booking_status_history, BookingRecapHistory)

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        more_than_two_days_ago = datetime.utcnow() - timedelta(days=3)
        bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=more_than_two_days_ago, token="ABCDEF"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_confirmed is True
        assert isinstance(expected_booking_recap.booking_status_history, BookingRecapHistory)

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.CancelledIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_cancelled is True
        assert expected_booking_recap.booking_status_history.cancellation_date is not None

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product)
        stock = offers_factories.EventStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_used is True
        assert expected_booking_recap.booking_is_cancelled is False
        assert expected_booking_recap.booking_is_reimbursed is False
        assert expected_booking_recap.booking_status_history.date_confirmed is not None
        assert expected_booking_recap.booking_status_history.date_used is not None

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, dateCreated=today, token="ABCD")

        offerer2 = offers_factories.OffererFactory(siren="8765432")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        venue2 = offers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock2, dateCreated=today, token="FGHI")

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_bookings_from_first_page(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, dateCreated=yesterday, token="ABCD")
        booking2 = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=1
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking2.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 2
        assert bookings_recap_paginated.total == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert bookings_recap_paginated.bookings_recap == []

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
        stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
        today = datetime.utcnow()
        booking = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 1

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
        stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
        today = datetime.utcnow()
        booking = bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock, dateCreated=today, token="FGHI", quantity=2
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
        assert bookings_recap_paginated.bookings_recap[1].booking_token == booking.token
        assert bookings_recap_paginated.page == 1
        assert bookings_recap_paginated.pages == 1
        assert bookings_recap_paginated.total == 2

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("America/Cayenne"))

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedIndividualBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_isbn == "9876543234"

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_only_booking_for_requested_venue(self, app: fixture):
        # Given
        pro_user = users_factories.ProFactory()
        user_offerer = offers_factories.UserOffererFactory(user=pro_user)

        bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        booking_two = bookings_factories.IndividualBookingFactory(
            stock__offer__venue__managingOfferer=user_offerer.offerer
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro_user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            venue_id=booking_two.venue.id,
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.offer_identifier == booking_two.stock.offer.id
        assert expected_booking_recap.offer_name == booking_two.stock.offer.name
        assert expected_booking_recap.booking_amount == booking_two.amount

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_only_booking_for_requested_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_date = datetime(2020, 12, 24, 10, 30)
        expected_booking = bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=event_date, offer__venue__managingOfferer=user_offerer.offerer
            )
        )
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_date.date(),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert resulting_booking_recap.booking_token == expected_booking.token

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_datetime = datetime(2020, 4, 21, 20, 00)

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime
        )
        cayenne_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_cayenne)

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime
        )
        mayotte_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_mayotte)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_datetime.date(),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
        assert cayenne_booking.token in bookings_tokens
        assert mayotte_booking.token in bookings_tokens

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def test_should_return_only_bookings_for_requested_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
        booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
        expected_booking = bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 26, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 29, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=datetime(2020, 12, 22, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_beginning_period, booking_ending_period),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert resulting_booking_recap.booking_date == utc_datetime_to_department_timezone(
            expected_booking.dateCreated, expected_booking.venue.departementCode
        )

    @override_features(**{FeatureToggle.IMPROVE_BOOKINGS_PERF.name: True})
    def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        requested_booking_period_beginning = datetime(2020, 4, 21, 20, 00).date()
        requested_booking_period_ending = datetime(2020, 4, 22, 20, 00).date()

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_booking_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne,
        )
        cayenne_booking = bookings_factories.IndividualBookingFactory(
            stock=stock_in_cayenne, dateCreated=cayenne_booking_datetime
        )

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_booking_datetime = datetime(2020, 4, 20, 23, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte,
        )
        mayotte_booking = bookings_factories.IndividualBookingFactory(
            stock=stock_in_mayotte, dateCreated=mayotte_booking_datetime
        )

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
        assert cayenne_booking.token in bookings_tokens
        assert mayotte_booking.token in bookings_tokens


class GetCsvReportTest:
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
            amount=12,
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert headers == [
            "Lieu",
            "Nom de l’offre",
            "Date de l'évènement",
            "ISBN",
            "Nom et prénom du bénéficiaire",
            "Email du bénéficiaire",
            "Téléphone du bénéficiaire",
            "Date et heure de réservation",
            "Date et heure de validation",
            "Contremarque",
            "Prix de la réservation",
            "Statut de la contremarque",
            "Date et heure de remboursement",
        ]
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Lieu"] == venue.name
        assert data_dict["Nom de l’offre"] == offer.name
        assert data_dict["Date de l'évènement"] == ""
        assert data_dict["ISBN"] == ((offer.extraData or {}).get("isbn") or "")
        assert data_dict["Nom et prénom du bénéficiaire"] == " ".join((beneficiary.lastName, beneficiary.firstName))
        assert data_dict["Email du bénéficiaire"] == beneficiary.email
        assert data_dict["Téléphone du bénéficiaire"] == (beneficiary.phoneNumber or "")
        assert data_dict["Date et heure de réservation"] == str(
            booking.dateCreated.astimezone(tz.gettz("Europe/Paris"))
        )
        assert data_dict["Date et heure de validation"] == str(booking.dateUsed.astimezone(tz.gettz("Europe/Paris")))
        assert data_dict["Contremarque"] == booking.token
        assert data_dict["Prix de la réservation"] == f"{booking.amount:.2f}"
        assert data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[booking.status]
        assert data_dict["Date et heure de remboursement"] == ""

    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock, quantity=2)

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 2

    def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(
        self, app: fixture
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.UserOffererFactory(offerer=offerer)

        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 2

    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.BookingFactory(
            user=beneficiary, stock=stock, dateCreated=yesterday, token="ABCDEF", status=BookingStatus.PENDING
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert headers == [
            "Lieu",
            "Nom de l’offre",
            "Date de l'évènement",
            "ISBN",
            "Nom et prénom du bénéficiaire",
            "Email du bénéficiaire",
            "Téléphone du bénéficiaire",
            "Date et heure de réservation",
            "Date et heure de validation",
            "Contremarque",
            "Prix de la réservation",
            "Statut de la contremarque",
            "Date et heure de remboursement",
        ]
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Lieu"] == venue.name
        assert data_dict["Nom de l’offre"] == offer.name
        assert data_dict["Date de l'évènement"] == str(stock.beginningDatetime.astimezone(tz.gettz("Europe/Paris")))
        assert data_dict["ISBN"] == ((offer.extraData or {}).get("isbn") or "")
        assert data_dict["Nom et prénom du bénéficiaire"] == " ".join((beneficiary.lastName, beneficiary.firstName))
        assert data_dict["Email du bénéficiaire"] == beneficiary.email
        assert data_dict["Téléphone du bénéficiaire"] == (beneficiary.phoneNumber or "")
        assert data_dict["Date et heure de réservation"] == str(
            booking.dateCreated.astimezone(tz.gettz("Europe/Paris"))
        )
        assert data_dict["Date et heure de validation"] == ""
        assert data_dict["Contremarque"] == booking.token
        assert data_dict["Prix de la réservation"] == f"{booking.amount:.2f}"
        assert data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[booking.status]
        assert data_dict["Date et heure de remboursement"] == ""

    def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(
            offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
        )
        more_than_two_days_ago = datetime.utcnow() - timedelta(days=3)
        bookings_factories.BookingFactory(
            user=beneficiary, stock=stock, dateCreated=more_than_two_days_ago, token="ABCDEF"
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert (
            data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[BookingStatus.CONFIRMED]
        )

    def test_should_return_cancelled_status_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.CancelledBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert (
            data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[BookingStatus.CANCELLED]
        )

    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product)
        stock = offers_factories.EventStockFactory(offer=offer, price=5)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=yesterday,
            token="ABCDEF",
            amount=5,
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[BookingStatus.USED]
        assert data_dict["Date et heure de validation"] == str(booking.dateUsed.astimezone(tz.gettz("Europe/Paris")))

    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        bookings_factories.BookingFactory(user=beneficiary, stock=stock, dateCreated=today, token="ABCD")

        offerer2 = offers_factories.OffererFactory(siren="8765432")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        venue2 = offers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock2, dateCreated=today, token="FGHI")

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 2

    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock)

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 0

    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Date et heure de réservation"] == str(booking_date.astimezone(tz.gettz("America/Cayenne")))

    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory(postalCode="97300")
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["ISBN"] == "9876543234"

    def test_should_return_booking_with_venue_name_when_public_name_is_not_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un événement", siret="11816909600069"
        )
        product = offers_factories.EventProductFactory(name="Shutter Island")
        offer_for_event = offers_factories.EventOfferFactory(venue=venue_for_event, product=product)
        stock_for_event = offers_factories.EventStockFactory(offer=offer_for_event, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_event,
            dateCreated=(default_booking_date + timedelta(days=1)),
            token="BBBBBB",
        )

        venue_for_book = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un livre", siret="41816609600069"
        )
        product_book = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_book = offers_factories.ThingOfferFactory(
            venue=venue_for_book, product=product_book, extraData=dict({"isbn": "9876543234"})
        )
        stock_for_book = offers_factories.ThingStockFactory(offer=offer_for_book, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_book,
            dateCreated=default_booking_date,
            token="AAAAAA",
        )

        venue_for_thing = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un bien qui n'est pas un livre", siret="83994784300018"
        )
        product_thing = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_thing = offers_factories.ThingOfferFactory(venue=venue_for_thing, product=product_thing)
        stock_for_thing = offers_factories.ThingStockFactory(offer=offer_for_thing, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_thing,
            dateCreated=(default_booking_date - timedelta(days=1)),
            token="ABCDEF",
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 3
        data_dicts = [dict(zip(headers, line)) for line in data]
        assert data_dicts[0]["Lieu"] == venue_for_event.name
        assert data_dicts[1]["Lieu"] == venue_for_book.name
        assert data_dicts[2]["Lieu"] == venue_for_thing.name

    def test_should_return_booking_with_venue_public_name_when_public_name_is_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Opéra paris", publicName="Super Opéra de Paris", siret="11816909600069"
        )
        product = offers_factories.EventProductFactory(name="Shutter Island")
        offer_for_event = offers_factories.EventOfferFactory(venue=venue_for_event, product=product)
        stock_for_event = offers_factories.EventStockFactory(offer=offer_for_event, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_event,
            dateCreated=(default_booking_date + timedelta(days=1)),
            token="BBBBBB",
        )

        venue_for_book = offers_factories.VenueFactory(
            managingOfferer=offerer, name="Lieu pour un livre", publicName="Librairie Châtelet", siret="41816609600069"
        )
        product_book = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_book = offers_factories.ThingOfferFactory(
            venue=venue_for_book, product=product_book, extraData=dict({"isbn": "9876543234"})
        )
        stock_for_book = offers_factories.ThingStockFactory(offer=offer_for_book, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_book,
            dateCreated=default_booking_date,
            token="AAAAAA",
        )

        venue_for_thing = offers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Lieu pour un bien qui n'est pas un livre",
            publicName="Guitar Center",
            siret="83994784300018",
        )
        product_thing = offers_factories.ThingProductFactory(name="Harry Potter")
        offer_for_thing = offers_factories.ThingOfferFactory(venue=venue_for_thing, product=product_thing)
        stock_for_thing = offers_factories.ThingStockFactory(offer=offer_for_thing, price=0)
        bookings_factories.UsedBookingFactory(
            user=beneficiary,
            stock=stock_for_thing,
            dateCreated=(default_booking_date - timedelta(days=1)),
            token="ABCDEF",
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 3
        data_dicts = [dict(zip(headers, line)) for line in data]
        assert data_dicts[0]["Lieu"] == venue_for_event.publicName
        assert data_dicts[1]["Lieu"] == venue_for_book.publicName
        assert data_dicts[2]["Lieu"] == venue_for_thing.publicName

    def test_should_return_only_booking_for_requested_venue(self, app: fixture):
        # Given
        pro_user = users_factories.ProFactory()
        user_offerer = offers_factories.UserOffererFactory(user=pro_user)

        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        booking_two = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=pro_user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            venue_id=booking_two.venue.id,
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Nom de l’offre"] == booking_two.stock.offer.name

    def test_should_return_only_booking_for_requested_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_date = datetime(2020, 12, 24, 10, 30)
        expected_booking = bookings_factories.BookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=event_date, offer__venue__managingOfferer=user_offerer.offerer
            )
        )
        bookings_factories.BookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )
        bookings_factories.BookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_date.date(),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Contremarque"] == expected_booking.token

    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        event_datetime = datetime(2020, 4, 21, 20, 00)

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime
        )
        cayenne_booking = bookings_factories.BookingFactory(stock=stock_in_cayenne)

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime
        )
        mayotte_booking = bookings_factories.BookingFactory(stock=stock_in_mayotte)

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_datetime.date(),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 2
        data_dicts = [dict(zip(headers, line)) for line in data]
        tokens = [booking["Contremarque"] for booking in data_dicts]
        assert sorted(tokens) == sorted([cayenne_booking.token, mayotte_booking.token])

    def test_should_return_only_bookings_for_requested_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
        booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
        expected_booking = bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 12, 26, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 12, 29, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )
        bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 12, 22, 15, 30),
            stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=user_offerer.user,
            booking_period=(booking_beginning_period, booking_ending_period),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Date et heure de réservation"] == str(
            expected_booking.dateCreated.astimezone(tz.gettz("Europe/Paris"))
        )

    def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app: fixture):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        requested_booking_period_beginning = datetime(2020, 4, 21, 20, 00).date()
        requested_booking_period_ending = datetime(2020, 4, 22, 20, 00).date()

        offer_in_cayenne = offers_factories.OfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_booking_datetime = datetime(2020, 4, 22, 2, 0)
        stock_in_cayenne = offers_factories.EventStockFactory(
            offer=offer_in_cayenne,
        )
        cayenne_booking = bookings_factories.BookingFactory(
            stock=stock_in_cayenne, dateCreated=cayenne_booking_datetime
        )

        offer_in_mayotte = offers_factories.OfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_booking_datetime = datetime(2020, 4, 20, 23, 0)
        stock_in_mayotte = offers_factories.EventStockFactory(
            offer=offer_in_mayotte,
        )
        mayotte_booking = bookings_factories.BookingFactory(
            stock=stock_in_mayotte, dateCreated=mayotte_booking_datetime
        )

        # When
        bookings_csv = booking_repository.get_csv_report(
            user=user_offerer.user,
            booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv))
        assert len(data) == 2
        data_dicts = [dict(zip(headers, line)) for line in data]
        tokens = [booking["Contremarque"] for booking in data_dicts]
        assert sorted(tokens) == sorted([cayenne_booking.token, mayotte_booking.token])


class FindSoonToBeExpiredBookingsTest:
    def test_should_return_only_soon_to_be_expired_individual_bookings(self, app: fixture):
        # Given
        expired_creation_date = date.today() - timedelta(days=23)
        expired_creation_date = datetime.combine(expired_creation_date, time(12, 34, 17))
        non_expired_creation_date = date.today() - timedelta(days=24)
        non_expired_creation_date = datetime.combine(non_expired_creation_date, time(12, 34, 17))
        too_old_expired_creation_date = date.today() - timedelta(days=22)
        too_old_expired_creation_date = datetime.combine(too_old_expired_creation_date, time(12, 34, 17))

        expected_booking = bookings_factories.IndividualBookingFactory(
            dateCreated=expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        # offer type not expirable
        bookings_factories.IndividualBookingFactory(
            dateCreated=expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=non_expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=too_old_expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        # educational booking : not concerned with notifications
        bookings_factories.EducationalBookingFactory(
            dateCreated=expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        # When
        expired_bookings = booking_repository.find_soon_to_be_expiring_individual_bookings_ordered_by_user().all()

        # Then
        assert expired_bookings == [expected_booking.individualBooking]

    def test_should_return_only_soon_to_be_expired_bookings_books_case(self):
        soon_expired_creation_date = datetime.combine(date.today() - timedelta(days=5), time(12, 34, 17))
        too_old_creation_date = datetime.combine(date.today() - timedelta(days=6), time(12, 34, 17))
        non_expired_creation_date = datetime.combine(date.today() - timedelta(days=4), time(12, 34, 17))

        soon_expired_books_booking = bookings_factories.IndividualBookingFactory(
            dateCreated=soon_expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=soon_expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=too_old_creation_date,
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        bookings_factories.IndividualBookingFactory(
            dateCreated=non_expired_creation_date,
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        assert booking_repository.find_soon_to_be_expiring_individual_bookings_ordered_by_user().all() == [
            soon_expired_books_booking.individualBooking
        ]


class GetActiveBookingsQuantityForOffererTest:
    def test_return_active_bookings_by_venues_for_offerer(self):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offerer = offers_factories.OffererFactory()

        venue_1 = offers_factories.VenueFactory(managingOfferer=offerer)
        offer_1 = offers_factories.ThingOfferFactory(venue=venue_1)
        stock_1 = offers_factories.ThingStockFactory(offer=offer_1)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)

        venue_2 = offers_factories.VenueFactory(managingOfferer=offerer)
        offer_2 = offers_factories.ThingOfferFactory(venue=venue_2)
        stock_2 = offers_factories.ThingStockFactory(offer=offer_2)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_2)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_2)
        bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_2)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock_2, cancellation_limit_date=yesterday, quantity=2
        )

        # When
        active_bookings_by_venue = booking_repository.get_active_bookings_quantity_for_offerer(offerer.id)

        # Then
        assert active_bookings_by_venue == {venue_1.id: 2, venue_2.id: 2}


class GetLegacyActiveBookingsQuantityForVenueTest:
    def test_return_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(quantity=2)
        venue = booking.venue
        bookings_factories.IndividualBookingFactory(stock__offer__venue=venue)

        # When
        active_bookings_quantity = booking_repository.get_legacy_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 3

    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offers_factories.VenueFactory()

        # When
        active_bookings_quantity = booking_repository.get_legacy_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 0

    def test_excludes_confirmed_used_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        venue = booking.venue
        bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue)
        bookings_factories.CancelledIndividualBookingFactory(stock__offer__venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            cancellation_limit_date=yesterday, quantity=2, stock__offer__venue=venue
        )

        # When
        active_bookings_quantity = booking_repository.get_legacy_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1

    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        venue = booking.venue
        another_venue = offers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.IndividualBookingFactory(stock__offer__venue=another_venue)

        # When
        active_bookings_quantity = booking_repository.get_legacy_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1


class GetValidatedBookingsQuantityForOffererTest:
    def test_return_validated_bookings_by_venues_for_offerer(self):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offerer = offers_factories.OffererFactory()

        venue_1 = offers_factories.VenueFactory(managingOfferer=offerer)
        offer_1 = offers_factories.ThingOfferFactory(venue=venue_1)
        stock_1 = offers_factories.ThingStockFactory(offer=offer_1, price=0)
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)
        bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_1)

        venue_2 = offers_factories.VenueFactory(managingOfferer=offerer)
        offer_2 = offers_factories.ThingOfferFactory(venue=venue_2)
        stock_2 = offers_factories.ThingStockFactory(offer=offer_2, price=0)
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary, stock=stock_2)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            user=beneficiary, stock=stock_2, cancellation_limit_date=yesterday, quantity=2
        )

        # When
        validated_bookings_quantity_by_venue = booking_repository.get_validated_bookings_quantity_for_offerer(
            offerer.id
        )

        # Then
        assert validated_bookings_quantity_by_venue == {venue_1.id: 1, venue_2.id: 2}


class GetLegacyValidatedBookingsQuantityForVenueTest:
    def test_return_used_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory(quantity=2)
        venue = booking.venue
        bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_legacy_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 3

    def test_return_confirmed_bookings_quantity_for_venue(self):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.IndividualBookingFactory(cancellation_limit_date=yesterday, quantity=2)
        venue = booking.venue

        # When
        validated_bookings_quantity = booking_repository.get_legacy_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 2

    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offers_factories.VenueFactory()

        # When
        validated_bookings_quantity = booking_repository.get_legacy_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 0

    def test_excludes_unused_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory()
        venue = booking.venue
        bookings_factories.IndividualBookingFactory(stock__offer__venue=venue)
        bookings_factories.CancelledIndividualBookingFactory(stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_legacy_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 1

    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory()
        venue = booking.venue
        another_venue = offers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=another_venue)

        # When
        validated_bookings_quantity = booking_repository.get_legacy_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 1


class GetOffersBookedByFraudulentUsersTest:
    def test_returns_only_offers_booked_by_fraudulent_users(self):
        # Given
        fraudulent_beneficiary_user = users_factories.BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        another_fraudulent_beneficiary_user = users_factories.BeneficiaryGrant18Factory(
            email="jesuisuneautrefraude@example.com"
        )
        beneficiary_user = users_factories.BeneficiaryGrant18Factory(email="jenesuispasunefraude@EXAmple.com")
        offer_booked_by_fraudulent_users = offers_factories.OfferFactory()
        offer_booked_by_non_fraudulent_users = offers_factories.OfferFactory()
        offer_booked_by_both = offers_factories.OfferFactory()

        bookings_factories.IndividualBookingFactory(
            individualBooking__user=fraudulent_beneficiary_user, stock__offer=offer_booked_by_fraudulent_users
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=another_fraudulent_beneficiary_user, stock__offer=offer_booked_by_both
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary_user, stock__offer=offer_booked_by_both
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=beneficiary_user, stock__offer=offer_booked_by_non_fraudulent_users
        )

        # When
        offers = booking_repository.find_offers_booked_by_beneficiaries(
            [fraudulent_beneficiary_user, another_fraudulent_beneficiary_user]
        )

        # Then
        assert len(offers) == 2
        assert set(offers) == {offer_booked_by_both, offer_booked_by_fraudulent_users}


class FindBookingsByFraudulentUsersTest:
    def test_returns_only_bookings_by_fraudulent_users(self):
        # Given
        fraudulent_beneficiary_user = users_factories.BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        another_fraudulent_beneficiary_user = users_factories.BeneficiaryGrant18Factory(
            email="jesuisuneautrefraude@example.com"
        )
        beneficiary_user = users_factories.BeneficiaryGrant18Factory(email="jenesuispasunefraude@EXAmple.com")

        booking_booked_by_fraudulent_user = bookings_factories.IndividualBookingFactory(
            individualBooking__user=fraudulent_beneficiary_user
        )
        another_booking_booked_by_fraudulent_user = bookings_factories.IndividualBookingFactory(
            individualBooking__user=another_fraudulent_beneficiary_user
        )
        bookings_factories.IndividualBookingFactory(individualBooking__user=beneficiary_user, stock__price=1)

        # When
        bookings = booking_repository.find_cancellable_bookings_by_beneficiaries(
            [fraudulent_beneficiary_user, another_fraudulent_beneficiary_user]
        )

        # Then
        assert len(bookings) == 2
        assert set(bookings) == {booking_booked_by_fraudulent_user, another_booking_booked_by_fraudulent_user}


class FindExpiringBookingsTest:
    def test_find_expired_bookings_before_and_after_enabling_feature_flag(self):
        with freeze_time("2021-08-01 15:00:00") as frozen_time:
            book_offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
            movie_offer = offers_factories.OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)

            movie_booking = bookings_factories.IndividualBookingFactory(
                stock__offer=movie_offer, dateCreated=datetime.utcnow()
            )

            frozen_time.move_to("2021-08-06 15:00:00")
            book_booking_new_expiry_delay = bookings_factories.IndividualBookingFactory(
                stock__offer=book_offer, dateCreated=datetime.utcnow()
            )
            bookings_factories.IndividualBookingFactory(stock__offer=movie_offer, dateCreated=datetime.utcnow())

            frozen_time.move_to("2021-08-17 17:00:00")

            bookings = booking_repository.find_expiring_individual_bookings_query().all()
            assert bookings == [book_booking_new_expiry_delay.individualBooking]

            frozen_time.move_to("2021-09-01 17:00:00")

            bookings = booking_repository.find_expiring_individual_bookings_query().all()
            assert set(bookings) == {book_booking_new_expiry_delay.individualBooking, movie_booking.individualBooking}


def test_get_deposit_booking():
    with freeze_time(datetime.utcnow() - relativedelta(years=2, days=2)):
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
        # disable trigger because deposit.expirationDate > now() is False in database time
        db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
        previous_deposit_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
        db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

    create_deposit(user, "test")

    current_deposit_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
    current_deposit_booking_2 = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
    bookings_factories.IndividualBookingFactory(
        individualBooking__user=user, individualBooking__attached_deposit="forced_none", amount=0
    )

    previous_deposit_id = user.deposits[0].id
    current_deposit_id = user.deposit.id

    with assert_num_queries(1):
        previous_deposit_bookings = get_bookings_from_deposit(previous_deposit_id)

    assert previous_deposit_bookings == [previous_deposit_booking]

    with assert_num_queries(1):
        current_deposit_bookings = get_bookings_from_deposit(current_deposit_id)

    assert set(current_deposit_bookings) == {current_deposit_booking, current_deposit_booking_2}
