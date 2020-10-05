import pytest
from tests.model_creators.generic_creators import create_booking, \
    create_offerer, create_user, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, \
    create_stock_from_offer

from domain.beneficiary.beneficiary import Beneficiary
from domain.booking.booking import Booking
from domain.stock.stock import Stock
from infrastructure.repository.booking import booking_domain_converter
from models import BookingSQLEntity, ThingType
from repository import repository


class BookingDomainConverterTest:
    def test_should_create_new_booking_when_does_not_exist(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        beneficiary = Beneficiary(identifier=1, can_book_free_offers=True, email='tony.stark@example.com',
                                  first_name='Tony', last_name='Stark', department_code='75', wallet_balance=500, reset_password_token='')
        offer = create_offer_with_thing_product(venue=venue)
        stock = Stock(identifier=2, quantity=1, offer=offer, price=0)
        booking = Booking(beneficiary=beneficiary, stock=stock, amount=10, quantity=1, is_used=True, is_cancelled=True)

        # when
        created_booking = booking_domain_converter.to_model(booking)

        # then
        assert created_booking.userId == beneficiary.identifier
        assert created_booking.stockId == stock.identifier
        assert created_booking.amount == 10
        assert created_booking.quantity == 1
        assert created_booking.token is not None
        assert created_booking.id == booking.identifier
        assert created_booking.isCancelled is True
        assert created_booking.isUsed is True

    @pytest.mark.usefixtures("db_session")
    def test_should_update_existing_booking_when_exist(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        book_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=1)
        booking_sql_entity = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue)
        repository.save(booking_sql_entity)
        booking = booking_domain_converter.to_domain(booking_sql_entity)
        booking.isCancelled = False

        # when
        updated_booking = booking_domain_converter.to_model(booking)

        # then
        assert updated_booking.isCancelled is False
