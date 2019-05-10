from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from domain.expenses import SUBVENTION_PHYSICAL_THINGS, SUBVENTION_DIGITAL_THINGS
from models.api_errors import ResourceGoneError, ForbiddenError
from models import ApiErrors, Booking, Stock, Offer, ThingType, Product
from utils.human_ids import humanize
from tests.test_utils import create_booking_for_thing, create_product_with_Thing_type
from validation.bookings import check_expenses_limits, check_booking_is_cancellable, check_booking_is_usable


@pytest.mark.standalone
class CheckExpenseLimitsTest:
    def test_raises_an_error_when_physical_limit_is_reached(self):
        # given
        expenses = {
            'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 190},
            'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 10}
        }
        booking = Booking(from_dict={'stockId': humanize(123), 'amount': 11, 'quantity': 1})
        stock = create_booking_for_thing(url='http://on.line', type=ThingType.LIVRE_EDITION).stock
        mocked_query = Mock(return_value=stock)

        # when
        with pytest.raises(ApiErrors) as api_errors:
            check_expenses_limits(expenses, booking, find_stock=mocked_query)

        # then
        assert api_errors.value.errors['global'] == ['La limite de %s € pour les biens culturels ne vous permet pas ' \
                                                     'de réserver' % SUBVENTION_PHYSICAL_THINGS]

    @pytest.mark.standalone
    def test_check_expenses_limits_raises_an_error_when_digital_limit_is_reached(self):
        # given
        expenses = {
            'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 10},
            'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 190}
        }
        booking = Booking(from_dict={'stockId': humanize(123), 'amount': 11, 'quantity': 1})
        stock = create_booking_for_thing(url='http://on.line', type=ThingType.JEUX_VIDEO).stock
        mocked_query = Mock(return_value=stock)

        # when
        with pytest.raises(ApiErrors) as api_errors:
            check_expenses_limits(expenses, booking, find_stock=mocked_query)

        # then
        assert api_errors.value.errors['global'] == ['La limite de %s € pour les offres numériques ne vous permet pas ' \
                                                     'de réserver' % SUBVENTION_DIGITAL_THINGS]

    @pytest.mark.standalone
    def test_does_not_raise_an_error_when_actual_expenses_are_lower_than_max(self):
        # given
        expenses = {
            'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 90},
            'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 90}
        }
        booking = Booking(from_dict={'stockId': humanize(123), 'amount': 11, 'quantity': 1})
        mocked_query = Mock()

        # when
        try:
            check_expenses_limits(expenses, booking, find_stock=mocked_query)
        except ApiErrors:
            # then
            pytest.fail('Booking for events must not raise any exceptions')


@pytest.mark.standalone
class CheckBookingIsCancellableTest:
    def test_raises_api_error_when_offerer_cancellation_and_used_booking(self):
        # Given
        booking = Booking()
        booking.isUsed = True

        # When
        with pytest.raises(ApiErrors) as e:
            check_booking_is_cancellable(booking, is_user_cancellation=False)

        # Then
        assert e.value.errors['booking'] == ["Impossible d\'annuler une réservation consommée"]

    def test_raises_api_error_when_user_cancellation_and_event_in_less_than_72h(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        with pytest.raises(ApiErrors) as e:
            check_booking_is_cancellable(booking, is_user_cancellation=True)

        # Then
        assert e.value.errors['booking'] == [
            "Impossible d\'annuler une réservation moins de 72h avant le début de l'évènement"]

    def test_does_not_raise_api_error_when_user_cancellation_and_event_in_more_than_72h(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=73)

        # When
        check_output = check_booking_is_cancellable(booking, is_user_cancellation=False)

        # Then
        assert check_output is None

    def test_does_not_raise_api_error_when_offerer_cancellation_and_event_in_less_than_72h(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        check_output = check_booking_is_cancellable(booking, is_user_cancellation=False)

        # Then
        assert check_output is None

    def test_does_not_raise_api_error_when_offerer_cancellation_not_used_and_thing(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.stock = Stock()
        booking.stock.offer = Offer()
        booking.stock.offer.product = create_product_with_Thing_type()

        # When
        check_output = check_booking_is_cancellable(booking, is_user_cancellation=False)

        # Then
        assert check_output is None


class CheckBookingIsUsableTest:
    def test_raises_resource_gone_error_if_is_used(self):
        # Given
        booking = Booking()
        booking.isUsed = True
        booking.stock = Stock()

        # When
        with pytest.raises(ResourceGoneError) as e:
            check_booking_is_usable(booking)
        assert e.value.errors['booking'] == [
            'Cette réservation a déjà été validée']

    def test_raises_resource_gone_error_if_is_cancelled(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = True
        booking.stock = Stock()

        # When
        with pytest.raises(ResourceGoneError) as e:
            check_booking_is_usable(booking)
        assert e.value.errors['booking'] == [
            'Cette réservation a été annulée']

    def test_raises_resource_gone_error_if_stock_beginning_datetime_in_more_than_72_hours(self):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = in_four_days

        # When
        with pytest.raises(ForbiddenError) as e:
            check_booking_is_usable(booking)
        assert e.value.errors['beginningDatetime'] == [
            'Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l\'évènement']

    def test_does_not_raise_error_if_not_cancelled_nor_used_and_no_beginning_datetime(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = None

        # When
        try:
            check_booking_is_usable(booking)
        except ApiErrors:
            pytest.fail(
                'Bookings which are not used nor cancelled and do not have a beginning datetime should be usable')

    def test_does_not_raise_error_if_not_cancelled_nor_used_and_beginning_datetime_in_less_than_72_hours(self):
        # Given
        in_two_days = datetime.utcnow() + timedelta(days=2)
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = False
        booking.stock = Stock()
        booking.stock.beginningDatetime = in_two_days

        # When
        try:
            check_booking_is_usable(booking)
        except ApiErrors:
            pytest.fail(
                'Bookings which are not used nor cancelled and do not have a beginning datetime should be usable')
