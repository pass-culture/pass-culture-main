import pytest
from unittest.mock import patch

from domain.booking.booking import Booking
from domain.booking.booking_exceptions import BookingDoesntExist
from domain.stock.stock import Stock
from infrastructure.repository.booking import booking_domain_converter
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from models import ThingType
from repository import repository
from tests.conftest import clean_database
from tests.domain_creators.generic_creators import create_domain_beneficiary
from tests.model_creators.generic_creators import create_booking, \
    create_offerer, create_user, \
    create_venue, create_stock, create_deposit
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer

from models import BookingSQLEntity, StockSQLEntity

class BookingSQLRepositoryTest:
    class GetExpensesByUserIdTest:
        def setup_method(self):
            self.booking_sql_repository = BookingSQLRepository()

        @clean_database
        @patch('infrastructure.repository.booking.booking_sql_repository.get_expenses')
        def test_compute_expenses_without_cancelled_bookings(self, get_expenses_mock, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            book_offer = create_offer_with_thing_product(
                venue_online, thing_type=ThingType.LIVRE_EDITION)
            book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
            booking_sql_entity1 = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue_online)
            booking_sql_entity2 = create_booking(user=user, is_used=True, stock=book_stock, venue=venue_online)
            booking_sql_entity3 = create_booking(user=user, stock=book_stock, venue=venue_online)
            repository.save(booking_sql_entity1, booking_sql_entity2, booking_sql_entity3)

            expected_expenses = {'expenses': 'dict'}
            get_expenses_mock.return_value = expected_expenses

            # when
            expenses = self.booking_sql_repository.get_expenses_by_user_id(user.id)

            # then
            assert expenses == expected_expenses

            args, kargs = get_expenses_mock.call_args
            (bookings,) = args
            assert len(bookings) == 2
            assert booking_sql_entity1 not in bookings
            assert booking_sql_entity2 in bookings
            assert booking_sql_entity3 in bookings

    class SaveTest:
        def setup_method(self):
            self.booking_sql_repository = BookingSQLRepository()

        @clean_database
        def test_should_create_booking_on_save_when_booking_does_not_exist(self, app):
            # given
            user_sql_entity = create_user(idx=4)
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            offer = create_offer_with_thing_product(
                venue_online, thing_type=ThingType.LIVRE_EDITION, is_digital=True)
            stock_sql_entity = create_stock(offer=offer, quantity=200, price=0, idx=23)

            user = create_domain_beneficiary(identifier=4)
            stock = Stock(
                identifier=23,
                quantity=200,
                offer=offer,
                price=0
            )

            booking_to_save = Booking(beneficiary=user, stock=stock, amount=0, quantity=1)
            repository.save(offer, user_sql_entity, stock_sql_entity)

            # when
            booking_saved = self.booking_sql_repository.save(booking_to_save)

            # then
            assert booking_saved.beneficiary.identifier == booking_to_save.beneficiary.identifier
            assert booking_saved.stock.identifier == booking_to_save.stock.identifier
            assert booking_saved.identifier is not None

        @clean_database
        def test_should_return_saved_booking_with_updated_user_wallet_balance_on_save(self, app):
            # given
            user_sql_entity = create_user(idx=4)
            deposit = create_deposit(user=user_sql_entity)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(
                venue, thing_type=ThingType.LIVRE_EDITION)
            stock_sql_entity = create_stock(offer=offer, price=20, idx=23)

            user = create_domain_beneficiary(identifier=4)
            stock = Stock(
                identifier=23,
                quantity=None,
                offer=offer,
                price=20
            )

            booking_to_save = Booking(beneficiary=user, stock=stock, amount=20, quantity=1)
            repository.save(deposit, offer, user_sql_entity, stock_sql_entity)

            # when
            booking_saved = self.booking_sql_repository.save(booking_to_save)

            # then
            assert booking_saved.beneficiary.wallet_balance == deposit.amount - stock.price

    class FindNotCancelledBookingByTest:
        def setup_method(self):
            self.booking_sql_repository = BookingSQLRepository()

        @clean_database
        def test_returns_booking_by_offer_id_and_user_id_when_not_cancelled(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
            book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
            booking_sql_entity1 = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue_online)
            booking_sql_entity2 = create_booking(user=user, is_cancelled=False, stock=book_stock, venue=venue_online)
            repository.save(booking_sql_entity1, booking_sql_entity2)

            # when
            found_booking = self.booking_sql_repository.find_not_cancelled_booking_by(
                offer_id=book_offer.id,
                user_id=user.id
            )

            # then
            assert found_booking.identifier == booking_sql_entity2.id

    class FindBookingByIdTest:
        def setup_method(self):
            self.booking_sql_repository = BookingSQLRepository()

        @clean_database
        def should_return_booking_matching_identifier(self, app) -> None:
            # given
            user = create_user()
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
            book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
            booking_sql_entity = create_booking(user=user, stock=book_stock, venue=venue_online)
            repository.save(booking_sql_entity)

            # when
            found_booking = self.booking_sql_repository.find_booking_by_id_and_beneficiary_id(
                booking_id=booking_sql_entity.id,
                beneficiary_id=user.id
            )

            # then
            assert found_booking.identifier == booking_sql_entity.id

        @clean_database
        def should_raise_exception_when_no_booking_is_found(self, app) -> None:
            # given
            user = create_user()
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
            book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
            booking_sql_entity = create_booking(user=user, stock=book_stock, venue=venue_online)
            repository.save(booking_sql_entity)

            # when
            with pytest.raises(BookingDoesntExist) as error:
                self.booking_sql_repository.find_booking_by_id_and_beneficiary_id(
                    booking_id=543,
                    beneficiary_id=user.id
                )

            # then
            assert error.value.errors['bookingId'] == ['bookingId ne correspond à aucune réservation']

        @clean_database
        def should_raise_exception_when_booking_does_not_belong_to_beneficiary(self, app) -> None:
            # given
            user = create_user()
            user2 = create_user(email='notowner@example.com')
            offerer = create_offerer()
            venue_online = create_venue(offerer, siret=None, is_virtual=True)
            book_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.LIVRE_EDITION)
            book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
            booking_sql_entity = create_booking(user=user, stock=book_stock, venue=venue_online)
            repository.save(booking_sql_entity, user2)

            # when
            with pytest.raises(BookingDoesntExist) as error:
                self.booking_sql_repository.find_booking_by_id_and_beneficiary_id(
                    booking_id=booking_sql_entity.id,
                    beneficiary_id=user2.id
                )

            # then
            assert error.value.errors['bookingId'] == ['bookingId ne correspond à aucune réservation']
