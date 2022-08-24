import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO

from dateutil import tz
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import openpyxl
import pytest
from pytest import fixture

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.bookings.repository import get_bookings_from_deposit
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments.api import create_deposit
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import EligibilityType
from pcapi.domain.booking_recap import booking_recap_history
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.serialization.bookings_recap_serialize import OfferType
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


class FindByTest:
    class ByTokenTest:
        def test_returns_booking_if_token_is_known(self, app: fixture):
            # given
            pro = users_factories.ProFactory()
            offerer = offerers_factories.OffererFactory()
            offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

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
            offerer = offerers_factories.OffererFactory()
            offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

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


class FindByProUserTest:
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_return_only_validated_bookings_for_requested_period(self, app: fixture):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)

        booking_date = datetime(2020, 1, 1, 10, 0, 0)

        bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=1))
        )
        used_booking_2 = bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=4))
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=8))
        )

        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro,
            booking_period=((booking_date + timedelta(2)), (booking_date + timedelta(5))),
            status_filter=BookingStatusFilter.VALIDATED,
        )

        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0]._booking_token == used_booking_2.token

    def test_should_return_only_reimbursed_bookings_for_requested_period(self, app: fixture):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = offers_factories.ThingStockFactory(offer__venue=venue, price=10)

        booking_date = datetime(2020, 1, 1, 10, 0, 0)

        bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=1))
        )
        reimbursed_booking_1 = bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=2))
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=4))
        )

        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro,
            booking_period=((booking_date + timedelta(1)), (booking_date + timedelta(3))),
            status_filter=BookingStatusFilter.REIMBURSED,
        )

        assert len(bookings_recap_paginated.bookings_recap) == 1
        assert bookings_recap_paginated.bookings_recap[0]._booking_token == reimbursed_booking_1.token

    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(
        self, app: fixture
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer)

        bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2
        expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert expected_booking_recap.booking_is_duo is True

    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        assert isinstance(expected_booking_recap.booking_status_history, booking_recap_history.BookingRecapHistory)

    def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        assert isinstance(expected_booking_recap.booking_status_history, booking_recap_history.BookingRecapHistory)

    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(
        self, app: fixture
    ):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, dateCreated=today, token="ABCD")

        offerer2 = offerers_factories.OffererFactory(siren="8765432")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
        bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock2, dateCreated=today, token="FGHI")

        # When
        bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 2

    def test_should_return_bookings_from_first_page(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
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

    def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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

    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
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

    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
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

    def test_should_return_only_booking_for_requested_venue(self, app: fixture):
        # Given
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)

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

    def test_should_return_only_booking_for_requested_event_date(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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

    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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

    def test_should_return_only_bookings_for_requested_booking_period(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
        booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
        booking_status_filter = BookingStatusFilter.BOOKED
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
            status_filter=booking_status_filter,
        )

        # Then
        assert len(bookings_recap_paginated.bookings_recap) == 1
        resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
        assert resulting_booking_recap.booking_date == utc_datetime_to_department_timezone(
            expected_booking.dateCreated, expected_booking.venue.departementCode
        )

    def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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

    def test_should_return_only_bookings_for_requested_offer_type(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.IndividualBookingFactory(
            dateCreated=default_booking_date,
            stock__offer__venue__managingOfferer=user_offerer.offerer,
        )

        # When
        individual_bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            offer_type=OfferType.INDIVIDUAL_OR_DUO,
        )
        all_bookings_recap_paginated = booking_repository.find_by_pro_user(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
        )

        # Then
        assert len(individual_bookings_recap_paginated.bookings_recap) == 1
        assert len(all_bookings_recap_paginated.bookings_recap) == 1


class GetCsvReportTest:
    def test_should_return_only_expected_booking_attributes(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
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
            "Type d'offre",
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
        assert data_dict["Type d'offre"] == "offre grand public"

    def test_should_not_return_token_for_non_used_goods(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
        booking = bookings_factories.BookingFactory(
            user=beneficiary,
            stock=stock,
            dateCreated=booking_date,
            token="ABCDEF",
            amount=12,
        )

        # When
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
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
            "Type d'offre",
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
        assert data_dict["Date et heure de validation"] == ""
        assert data_dict["Contremarque"] == ""
        assert data_dict["Prix de la réservation"] == f"{booking.amount:.2f}"
        assert data_dict["Statut de la contremarque"] == booking_repository.BOOKING_STATUS_LABELS[booking.status]
        assert data_dict["Date et heure de remboursement"] == ""

    def test_should_return_only_validated_bookings_for_requested_period(self, app: fixture):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        booking_date = datetime(2020, 1, 1, 10, 0, 0)

        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            dateUsed=(booking_date + timedelta(days=1)),
            stock__offer__name="Harry Potter Vol 1",
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            dateUsed=(booking_date + timedelta(days=4)),
            stock__offer__name="Harry Potter Vol 2",
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            dateUsed=(booking_date + timedelta(days=8)),
            stock__offer__name="Harry Potter Vol 3",
        )
        bookings_csv = booking_repository.get_export(
            user=pro,
            booking_period=((booking_date + timedelta(2)), (booking_date + timedelta(5))),
            status_filter=BookingStatusFilter.VALIDATED,
        )

        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        # Check bookings offer name
        assert data[0][1] == "Harry Potter Vol 2"

    def test_should_return_only_reimbursed_bookings_for_requested_period(self, app: fixture):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        booking_date = datetime(2020, 1, 1, 10, 0, 0)

        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            reimbursementDate=(booking_date + timedelta(days=1)),
            stock__offer__name="Harry Potter Vol 1",
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            reimbursementDate=(booking_date + timedelta(days=2)),
            stock__offer__name="Harry Potter Vol 2",
        )
        bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            quantity=1,
            dateCreated=booking_date,
            reimbursementDate=(booking_date + timedelta(days=4)),
            stock__offer__name="Harry Potter Vol 3",
        )

        bookings_csv = booking_repository.get_export(
            user=pro,
            booking_period=((booking_date + timedelta(1)), (booking_date + timedelta(3))),
            status_filter=BookingStatusFilter.REIMBURSED,
        )

        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        # Check bookings offer name
        assert data[0][1] == "Harry Potter Vol 2"

    def test_should_return_booking_as_duo_when_quantity_is_two(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock, quantity=2)

        # When
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2

    def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(
        self, app: fixture
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer)

        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)

        # When
        bookings_csv = booking_repository.get_export(
            user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2

    def test_should_return_event_booking_when_booking_is_on_an_event(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
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
            "Type d'offre",
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
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Statut de la contremarque"] == "confirmé"

    def test_should_return_cancelled_status_when_booking_has_been_cancelled(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
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
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
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
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        today = datetime.utcnow()
        bookings_factories.BookingFactory(user=beneficiary, stock=stock, dateCreated=today, token="ABCD")

        offerer2 = offerers_factories.OffererFactory(siren="8765432")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock2, dateCreated=today, token="FGHI")

        # When
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2

    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
        product = offers_factories.ThingProductFactory(name="Harry Potter")
        offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=stock)

        # When
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        _, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 0

    def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Date et heure de réservation"] == str(booking_date.astimezone(tz.gettz("America/Cayenne")))

    def test_should_return_booking_isbn_when_information_is_available(self, app: fixture):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(postalCode="97300")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["ISBN"] == "9876543234"

    def test_should_return_booking_with_venue_name_when_public_name_is_not_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offerers_factories.VenueFactory(
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

        venue_for_book = offerers_factories.VenueFactory(
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

        venue_for_thing = offerers_factories.VenueFactory(
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 3
        data_dicts = [dict(zip(headers, line)) for line in data]
        assert data_dicts[0]["Lieu"] == venue_for_event.name
        assert data_dicts[1]["Lieu"] == venue_for_book.name
        assert data_dicts[2]["Lieu"] == venue_for_thing.name

    def test_should_return_booking_with_venue_public_name_when_public_name_is_provided(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_for_event = offerers_factories.VenueFactory(
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

        venue_for_book = offerers_factories.VenueFactory(
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

        venue_for_thing = offerers_factories.VenueFactory(
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
        bookings_csv = booking_repository.get_export(
            user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 3
        data_dicts = [dict(zip(headers, line)) for line in data]
        assert data_dicts[0]["Lieu"] == venue_for_event.publicName
        assert data_dicts[1]["Lieu"] == venue_for_book.publicName
        assert data_dicts[2]["Lieu"] == venue_for_thing.publicName

    def test_should_return_only_booking_for_requested_venue(self, app: fixture):
        # Given
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)

        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        booking_two = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)

        # When
        bookings_csv = booking_repository.get_export(
            user=pro_user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            venue_id=booking_two.venue.id,
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Nom de l’offre"] == booking_two.stock.offer.name

    def test_should_return_only_booking_for_requested_event_date(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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
        bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_date.date(),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Contremarque"] == expected_booking.token

    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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
        bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            event_date=event_datetime.date(),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2
        data_dicts = [dict(zip(headers, line)) for line in data]
        tokens = [booking["Contremarque"] for booking in data_dicts]
        assert sorted(tokens) == sorted([cayenne_booking.token, mayotte_booking.token])

    def test_should_return_only_bookings_for_requested_booking_period(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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
        bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(booking_beginning_period, booking_ending_period),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 1
        data_dict = dict(zip(headers, data[0]))
        assert data_dict["Date et heure de réservation"] == str(
            expected_booking.dateCreated.astimezone(tz.gettz("Europe/Paris"))
        )

    def test_should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
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
        bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
        )

        # Then
        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2
        data_dicts = [dict(zip(headers, line)) for line in data]
        tokens = [booking["Contremarque"] for booking in data_dicts]
        assert sorted(tokens) == sorted([cayenne_booking.token, mayotte_booking.token])

    def test_should_output_the_correct_offer_type_depending_wether_offer_educational_or_not(self, app: fixture):
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        booking_1 = bookings_factories.IndividualBookingFactory(
            stock__offer__venue=venue,
        )

        booking_2 = bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
        )

        # When
        beginning_period = datetime.fromisoformat("2021-10-15")
        ending_period = datetime.fromisoformat("2032-02-15")
        bookings_csv = booking_repository.get_export(
            user=pro,
            booking_period=(beginning_period, ending_period),
        )

        # Then
        expected_type = {
            booking_1.stock.offer.name: "offre grand public",
            booking_2.stock.offer.name: "offre grand public",
        }

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert len(data) == 2
        data_dicts = [dict(zip(headers, line)) for line in data]
        for data_dict in data_dicts:
            offer_name = data_dict["Nom de l’offre"]
            assert data_dict["Type d'offre"] == expected_type[offer_name]

    def test_should_return_only_bookings_for_requested_offer_type(self, app: fixture):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.IndividualBookingFactory(
            dateCreated=default_booking_date,
            stock__offer__venue__managingOfferer=user_offerer.offerer,
        )

        # When
        individual_bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
            offer_type=OfferType.INDIVIDUAL_OR_DUO,
        )
        all_bookings_csv = booking_repository.get_export(
            user=user_offerer.user,
            booking_period=(one_year_before_booking, one_year_after_booking),
        )

        # Then
        headers, *individual_bookings_data = csv.reader(StringIO(individual_bookings_csv), delimiter=";")
        assert len(individual_bookings_data) == 1
        individual_bookings_data_dict = dict(zip(headers, individual_bookings_data[0]))
        assert individual_bookings_data_dict["Type d'offre"] == "offre grand public"
        headers, *all_bookings_data = csv.reader(StringIO(all_bookings_csv), delimiter=";")
        assert len(all_bookings_data) == 1

    class BookingStatusInCsvReportTest:
        @freeze_time("2021-12-15 09:00:00")
        def test_should_output_the_correct_status_for_individual_bookings_before_cancellationLimitDate(self, app):
            # Given
            date_created = datetime.utcnow() - timedelta(hours=6)

            pro = users_factories.ProFactory()
            offerer = offerers_factories.OffererFactory()
            offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)

            bookings_factories.CancelledIndividualBookingFactory(
                stock__offer__venue=venue,
                dateCreated=date_created,
            )
            bookings_factories.IndividualBookingFactory(
                stock__offer__venue=venue,
                dateCreated=date_created,
            )

            # When
            beginning_period = datetime.fromisoformat("2021-10-15")
            ending_period = datetime.fromisoformat("2032-02-15")
            bookings_csv = booking_repository.get_export(
                user=pro,
                booking_period=(beginning_period, ending_period),
            )

            # Then
            headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
            assert len(data) == 2
            pos_cm = headers.index("Statut de la contremarque")
            assert sorted([line[pos_cm] for line in data]) == ["annulé", "réservé"]

        @freeze_time("2021-12-15 09:00:00")
        def test_should_output_the_correct_status_for_individual_bookings_things_after_cancellationLimitDate(self, app):
            # Given
            date_created = datetime.utcnow() - timedelta(days=10)

            pro = users_factories.ProFactory()
            offerer = offerers_factories.OffererFactory()
            offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)

            bookings_factories.CancelledIndividualBookingFactory(
                stock__offer__venue=venue,
                dateCreated=date_created,
            )
            bookings_factories.IndividualBookingFactory(
                stock__offer__venue=venue,
                dateCreated=date_created,
            )
            bookings_factories.UsedIndividualBookingFactory(
                stock__offer__venue=venue,
                dateCreated=date_created,
            )
            bookings_factories.UsedIndividualBookingFactory(
                status=BookingStatus.REIMBURSED,
                stock__offer__venue=venue,
                dateCreated=date_created,
            )

            # When
            beginning_period = datetime.fromisoformat("2021-10-15")
            ending_period = datetime.fromisoformat("2032-02-15")
            bookings_csv = booking_repository.get_export(
                user=pro,
                booking_period=(beginning_period, ending_period),
            )

            # Then
            headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
            assert len(data) == 4
            pos_cm = headers.index("Statut de la contremarque")
            assert sorted([line[pos_cm] for line in data]) == ["annulé", "remboursé", "réservé", "validé"]

        @freeze_time("2021-12-15 09:00:00")
        def test_should_output_the_correct_status_for_individual_bookings_events_after_cancellationLimitDate(self, app):
            # Given
            date_created = datetime.utcnow() - timedelta(days=10)
            event_date = datetime.utcnow() + timedelta(days=2)

            pro = users_factories.ProFactory()
            offerer = offerers_factories.OffererFactory()
            offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)
            event_stock = offers_factories.EventStockFactory(beginningDatetime=event_date, offer__venue=venue)
            bookings_factories.CancelledIndividualBookingFactory(
                stock=event_stock,
                dateCreated=date_created,
            )
            bookings_factories.IndividualBookingFactory(
                stock=event_stock,
                dateCreated=date_created,
            )
            bookings_factories.UsedIndividualBookingFactory(
                stock=event_stock,
                dateCreated=date_created,
            )
            bookings_factories.UsedIndividualBookingFactory(
                status=BookingStatus.REIMBURSED,
                stock=event_stock,
                dateCreated=date_created,
            )

            # When
            beginning_period = datetime.fromisoformat("2021-10-15")
            ending_period = datetime.fromisoformat("2032-02-15")
            bookings_csv = booking_repository.get_export(
                user=pro,
                booking_period=(beginning_period, ending_period),
            )

            # Then
            headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
            assert len(data) == 4
            pos_cm = headers.index("Statut de la contremarque")
            assert sorted([line[pos_cm] for line in data]) == ["annulé", "confirmé", "remboursé", "validé"]


class GetExcelReportTest:
    def test_should_return_excel_export_according_to_booking_atrributes(self):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        headers = [
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
            "Type d'offre",
        ]

        # When
        bookings_excel = booking_repository.get_export(
            user=pro,
            booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365)),
            export_type=BookingExportType.EXCEL,
        )
        wb = openpyxl.load_workbook(BytesIO(bookings_excel))
        sheet = wb.active

        # Then
        # Headers
        for i in range(1, len(headers)):
            assert sheet.cell(row=1, column=i).value == headers[i - 1]
        # Lieu
        assert sheet.cell(row=2, column=1).value == venue.name
        # Nom de l’offre
        assert sheet.cell(row=2, column=2).value == offer.name
        # Date de l'évènement
        assert sheet.cell(row=2, column=3).value == "None"
        # ISBN
        assert sheet.cell(row=2, column=4).value == ((offer.extraData or {}).get("isbn") or None)
        # Nom et prénom du bénéficiaire
        assert sheet.cell(row=2, column=5).value == " ".join((beneficiary.lastName, beneficiary.firstName))
        # Email du bénéficiaire
        assert sheet.cell(row=2, column=6).value == beneficiary.email
        # Téléphone du bénéficiaire
        assert sheet.cell(row=2, column=7).value == (beneficiary.phoneNumber or None)
        # Date et heure de réservation
        assert sheet.cell(row=2, column=8).value == str(booking.dateCreated.astimezone(tz.gettz("Europe/Paris")))
        # Date et heure de validation
        assert sheet.cell(row=2, column=9).value == str(booking.dateUsed.astimezone(tz.gettz("Europe/Paris")))
        # Contremarque
        assert sheet.cell(row=2, column=10).value == booking.token
        # Prix de la réservation
        assert sheet.cell(row=2, column=11).value == booking.amount
        # Statut de la contremarque
        assert sheet.cell(row=2, column=12).value == booking_repository.BOOKING_STATUS_LABELS[booking.status]
        # Date et heure de remboursement
        assert sheet.cell(row=2, column=13).value == "None"
        # Type d'offre
        assert sheet.cell(row=2, column=14).value == "offre grand public"


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


class GetLegacyActiveBookingsQuantityForVenueTest:
    def test_return_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(quantity=2)
        venue = booking.venue
        bookings_factories.IndividualBookingFactory(stock__offer__venue=venue)

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 3

    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offerers_factories.VenueFactory()

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

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
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1

    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        venue = booking.venue
        another_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.IndividualBookingFactory(stock__offer__venue=another_venue)

        # When
        active_bookings_quantity = booking_repository.get_active_bookings_quantity_for_venue(venue.id)

        # Then
        assert active_bookings_quantity == 1


class GetLegacyValidatedBookingsQuantityForVenueTest:
    def test_return_used_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory(quantity=2)
        venue = booking.venue
        bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 3

    def test_return_confirmed_bookings_quantity_for_venue(self):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = bookings_factories.IndividualBookingFactory(cancellation_limit_date=yesterday, quantity=2)
        venue = booking.venue

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 2

    def test_return_0_when_no_bookings_exist(self):
        # Given
        venue = offerers_factories.VenueFactory()

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 0

    def test_excludes_unused_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory()
        venue = booking.venue
        bookings_factories.IndividualBookingFactory(stock__offer__venue=venue)
        bookings_factories.CancelledIndividualBookingFactory(stock__offer__venue=venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

        # Then
        assert validated_bookings_quantity == 1

    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.UsedIndividualBookingFactory()
        venue = booking.venue
        another_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=another_venue)

        # When
        validated_bookings_quantity = booking_repository.get_validated_bookings_quantity_for_venue(venue.id)

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

    create_deposit(user, "test", EligibilityType.AGE18)

    current_deposit_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
    current_deposit_booking_2 = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
    bookings_factories.IndividualBookingFactory(individualBooking__user=user, individualBooking__deposit=None, amount=0)

    previous_deposit_id = user.deposits[0].id
    current_deposit_id = user.deposit.id

    with assert_num_queries(1):
        previous_deposit_bookings = get_bookings_from_deposit(previous_deposit_id)

    assert previous_deposit_bookings == [previous_deposit_booking]

    with assert_num_queries(1):
        current_deposit_bookings = get_bookings_from_deposit(current_deposit_id)

    assert set(current_deposit_bookings) == {current_deposit_booking, current_deposit_booking_2}


class SoonExpiringBookingsTest:
    def test_get_soon_expiring_bookings(self):
        stock = offers_factories.ThingStockFactory()

        bookings_factories.UsedBookingFactory(stock=stock)
        bookings_factories.CancelledBookingFactory(stock=stock)
        booking = bookings_factories.IndividualBookingFactory(stock=stock)

        creation_date = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(stock=stock, dateCreated=creation_date)

        remaining_days = (booking.expirationDate.date() - date.today()).days

        bookings = set(booking_repository.get_soon_expiring_bookings(remaining_days))
        assert {booking.id for booking in bookings} == {booking.id}

    def test_no_unexpected_queries(self):
        stocks = offers_factories.ThingStockFactory.create_batch(5)
        bookings = [bookings_factories.IndividualBookingFactory(stock=stock) for stock in stocks]

        remaining_days = (bookings[0].expirationDate.date() - date.today()).days
        with assert_num_queries(1):
            list(booking_repository.get_soon_expiring_bookings(remaining_days))


@freeze_time("2020-10-15 09:00:00")
class GetTomorrowEventOfferTest:
    def test_find_tomorrow_event_offer(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=tomorrow,
            )
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 1

    def should_not_select_given_before_tomorrow_booking_event(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=yesterday,
            )
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 0

    def should_not_select_given_after_tomorrow_booking_event(self):
        after_tomorrow = datetime.utcnow() + timedelta(days=2)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=after_tomorrow,
            )
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 0

    def should_not_select_given_not_booking_event(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(stock__beginningDatetime=tomorrow)

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 0

    def should_do_only_one_query(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=tomorrow,
            )
        )

        with assert_num_queries(1):
            bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 1

    def should_not_select_digital_event(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=tomorrow,
                offer__url="http://digitaloffer.pass",
            )
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 0

    @pytest.mark.parametrize(
        "offer_url",
        [
            None,
            "",
        ],
    )
    def should_select_not_digital_event(self, offer_url):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=tomorrow,
                offer__url=offer_url,
            )
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 1

    def should_not_select_cancelled_booking(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        bookings_factories.IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=tomorrow,
            ),
            status=BookingStatus.CANCELLED,
        )

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 0

    def should_select_several_bookings_given_one_stock_with_several_bookings(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        bookings_factories.IndividualBookingFactory(stock=stock)
        bookings_factories.IndividualBookingFactory(stock=stock)

        bookings = booking_repository.find_individual_bookings_event_happening_tomorrow_query()

        assert len(bookings) == 2
