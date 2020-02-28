from datetime import datetime, timedelta

from freezegun import freeze_time

from models.db import db
from repository import repository
from scripts.validate_bookings_associated_to_outdated_stocks import validate_bookings_associated_to_outdated_stocks
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit
from tests.model_creators.specific_creators import create_offer_with_event_product


@freeze_time('2019-10-01')
@clean_database
def test_when_booking_is_associated_to_sold_out_stock_should_update_stocks_and_bookings(app):
    # Given
    user = create_user()
    create_deposit(user)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    stock1 = create_stock(offer=offer,
                          end_datetime=datetime(2019, 9, 15),
                          available=10)
    stock2 = create_stock(offer=offer,
                          end_datetime=datetime(2019, 9, 20),
                          available=10)
    booking1 = create_booking(user=user, is_used=False, stock=stock1)
    booking2 = create_booking(user=user, is_used=False, stock=stock1)
    booking3 = create_booking(user=user, is_used=False, stock=stock2)
    repository.save(booking1, booking2, booking3)
    stock1.available = 0
    stock2.available = 0
    repository.save(stock1, stock2)

    # When
    validate_bookings_associated_to_outdated_stocks()

    # Then
    db.session.refresh(stock1)
    db.session.refresh(stock2)
    db.session.refresh(booking1)
    db.session.refresh(booking2)
    db.session.refresh(booking3)
    assert stock1.available == 2
    assert stock2.available == 1
    assert booking1.isUsed is True
    assert booking1.dateUsed == datetime(2019, 9, 17)
    assert booking2.isUsed is True
    assert booking2.dateUsed == datetime(2019, 9, 17)
    assert booking3.isUsed is True
    assert booking3.dateUsed == datetime(2019, 9, 22)


@freeze_time('2019-10-01')
@clean_database
def test_when_booking_is_associated_to_sold_out_stock_should_update_stocks_availability_with_total_number_of_bookings(app):
    # Given
    user = create_user()
    create_deposit(user)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    stock = create_stock(offer=offer,
                         end_datetime=datetime(2019, 9, 15),
                         available=10)
    booking1 = create_booking(user=user, is_used=False, stock=stock)
    booking2 = create_booking(user=user, is_used=False, stock=stock)
    booking3 = create_booking(user=user, is_used=False, is_cancelled=True, stock=stock)
    repository.save(booking1, booking2, booking3)
    stock.available = 0
    repository.save(stock)

    # When
    validate_bookings_associated_to_outdated_stocks()

    # Then
    db.session.refresh(stock)
    assert stock.available == 3


@freeze_time('2019-10-01')
@clean_database
def test_when_booking_is_associated_to_sold_out_stock_should_update_stocks_availability_with_duo_offer(app):
    # Given
    user = create_user()
    create_deposit(user)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    stock = create_stock(offer=offer,
                         end_datetime=datetime(2019, 9, 15),
                         available=10)
    booking1 = create_booking(user=user, is_used=False, stock=stock)
    booking2 = create_booking(user=user, is_used=False, quantity=2, stock=stock)
    booking3 = create_booking(user=user, is_used=False, stock=stock)
    repository.save(booking1, booking2, booking3)
    stock.available = 0
    repository.save(stock)

    # When
    validate_bookings_associated_to_outdated_stocks()

    # Then
    db.session.refresh(stock)
    assert stock.available == 4


@freeze_time('2019-10-01')
@clean_database
def test_when_booking_is_associated_to_enough_stock_should_not_update_anything(app):
    # Given
    user = create_user()
    create_deposit(user)

    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    end_datetime = datetime(2019, 9, 15)
    end_datetime_plus_two_days = end_datetime + timedelta(hours=48)
    stock = create_stock(offer=offer,
                         end_datetime=end_datetime,
                         available=10)
    booking1 = create_booking(user=user,
                              is_used=True,
                              date_used=end_datetime_plus_two_days,
                              stock=stock)
    booking2 = create_booking(user=user,
                              is_used=True,
                              date_used=end_datetime_plus_two_days,
                              stock=stock)
    repository.save(booking1, booking2)

    # When
    validate_bookings_associated_to_outdated_stocks()

    # Then
    db.session.refresh(stock)
    db.session.refresh(booking1)
    db.session.refresh(booking2)
    assert stock.available == 10
    assert booking1.isUsed is True
    assert booking1.dateUsed == end_datetime_plus_two_days
    assert booking2.isUsed is True
    assert booking2.dateUsed == end_datetime_plus_two_days
