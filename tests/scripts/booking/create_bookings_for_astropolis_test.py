from models import BookingSQLEntity
from repository import repository
from scripts.booking.create_bookings_for_astropolis import create_bookings_for_astropolis
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_user, create_offerer, create_venue, create_stock
from tests.model_creators.specific_creators import create_offer_with_thing_product


@clean_database
def test_should_create_bookings_when_offer_one_with_price_0_was_booked_but_not_offer_two_nor_three(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_0)

    repository.save(
        booking,
        stock_for_offer_two,
        stock_for_offer_three,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_for_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_for_beneficiary) == 1
    assert expected_created_booking_for_beneficiary[0].isUsed is True
    assert expected_created_booking_for_beneficiary[0].amount == stock_for_offer_three.price
    assert expected_created_booking_for_beneficiary[0].quantity == 1
    assert expected_created_booking_for_beneficiary[0].stockId == stock_for_offer_three.id
    assert expected_created_booking_for_beneficiary[0].userId == beneficiary.id


@clean_database
def test_should_not_create_bookings_when_offer_one_with_price_5_was_booked_but_not_offer_two_nor_three(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_5 = create_stock(offer=offer_one, price=5)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking_for_beneficiary1 = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_5)
    repository.save(
        booking_for_beneficiary1,
        stock_for_offer_two,
        stock_for_offer_three,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary1 = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary1) == 0


@clean_database
def test_should_not_create_bookings_when_offer_one_with_price_0_and_offer_two_were_booked(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking_on_offer_one_with_price_0 = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_0)
    booking_on_offer_two = create_booking(user=beneficiary, stock=stock_for_offer_two)
    repository.save(
        booking_on_offer_one_with_price_0,
        booking_on_offer_two,
        stock_for_offer_three,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 0


@clean_database
def test_should_not_create_bookings_when_offer_one_with_price_0_and_offer_three_were_booked(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking_on_offer_one_with_price_0 = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_0)
    booking_on_offer_three = create_booking(user=beneficiary, stock=stock_for_offer_three)
    repository.save(
        booking_on_offer_one_with_price_0,
        booking_on_offer_three,
        stock_for_offer_two,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 1
    assert expected_created_booking_beneficiary[0] == booking_on_offer_three


@clean_database
def test_should_not_create_bookings_when_offer_one_with_price_0_was_cancelled(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking = create_booking(user=beneficiary, is_cancelled=True, stock=stock_for_offer_one_with_price_0)
    repository.save(booking, stock_for_offer_two, stock_for_offer_three)

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 0


@clean_database
def test_should_not_create_bookings_when_offer_three_was_already_booked(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5)

    booking = create_booking(user=beneficiary, stock=stock_for_offer_three)
    repository.save(
        booking,
        stock_for_offer_one_with_price_0,
        stock_for_offer_two,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 1
    assert expected_created_booking_beneficiary[0] == booking


@clean_database
def test_should_not_create_bookings_when_offer_three_is_not_bookable(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=5, quantity=0)

    booking = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_0)
    repository.save(
        booking,
        stock_for_offer_one_with_price_0,
        stock_for_offer_two,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 0


@clean_database
def test_should_not_create_bookings_when_beneficiary_does_not_have_enough_money(app):
    # Given
    beneficiary = create_user(first_name='John', last_name='Wick', email='john.wick@example.com')
    create_deposit(user=beneficiary, amount=100)
    offerer = create_offerer()
    venue = create_venue(offerer)

    offer_one = create_offer_with_thing_product(venue)
    offer_two = create_offer_with_thing_product(venue)
    offer_three = create_offer_with_thing_product(venue)

    stock_for_offer_one_with_price_0 = create_stock(offer=offer_one, price=0)
    stock_for_offer_two = create_stock(offer=offer_two, price=2)
    stock_for_offer_three = create_stock(offer=offer_three, price=150)

    booking = create_booking(user=beneficiary, stock=stock_for_offer_one_with_price_0)
    repository.save(
        booking,
        stock_for_offer_one_with_price_0,
        stock_for_offer_two,
    )

    # When
    create_bookings_for_astropolis(
        offer_one_id=offer_one.id,
        offer_two_id=offer_two.id,
        offer_three_id=offer_three.id
    )

    # Then
    expected_created_booking_beneficiary = BookingSQLEntity.query \
        .filter(BookingSQLEntity.userId == beneficiary.id) \
        .filter(BookingSQLEntity.stockId == stock_for_offer_three.id) \
        .all()
    assert len(expected_created_booking_beneficiary) == 0
