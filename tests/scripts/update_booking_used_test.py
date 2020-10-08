from datetime import datetime

from freezegun import freeze_time

from pcapi.models import BookingSQLEntity
from pcapi.repository import repository
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence
import pytest
from pcapi.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit
from pcapi.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


class UpdateBookingUsedTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_booking_used_when_booking_is_on_thing_product(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(beginning_datetime=None, offer=offer)
        booking = create_booking(user=user, is_used=False, stock=stock)
        repository.save(user, deposit, booking, stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert not updated_booking.isUsed
        assert not updated_booking.dateUsed

    @freeze_time('2019-10-13')
    @pytest.mark.usefixtures("db_session")
    def test_update_booking_used_when_event_date_is_3_days_before(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2019, 10, 9, 10, 20, 00), offer=offer)
        booking = create_booking(user=user, is_used=False, stock=stock)
        repository.save(user, deposit, booking, stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert updated_booking.isUsed
        assert updated_booking.dateUsed == datetime(2019, 10, 13)

    @freeze_time('2019-10-10')
    @pytest.mark.usefixtures("db_session")
    def test_update_booking_used_when_event_date_is_only_1_day_before(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2019, 10, 9, 10, 20, 00), offer=offer)
        booking = create_booking(user=user, is_used=False, stock=stock)
        repository.save(user, deposit, booking, stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert not updated_booking.isUsed
        assert updated_booking.dateUsed is None

    @pytest.mark.usefixtures("db_session")
    def test_does_not_update_booking_if_already_used(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2019, 10, 9, 10, 20, 00), offer=offer)
        booking_date = datetime(2019, 10, 12, 12, 20, 0)
        booking = create_booking(user=user, date_used=booking_date, is_used=True, stock=stock)
        repository.save(user, deposit, booking, stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert updated_booking.isUsed
        assert updated_booking.dateUsed == booking_date
