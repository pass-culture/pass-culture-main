from unittest.mock import MagicMock, patch

from models import ThingType, BookingSQLEntity
from repository import repository
from scripts.booking.create_booking_for_user_on_specific_stock import create_booking_for_user_on_specific_stock, \
    create_booking_for_user_on_specific_stock_bypassing_capping_limits
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_stock, create_venue, create_offerer, \
    create_booking, create_deposit
from tests.model_creators.specific_creators import create_offer_with_thing_product
from use_cases.book_an_offer import BookingInformation


class CreateBookingForUserOnSpecificStockTest:
    def test_should_call_book_an_offer_use_case_with_expected_parameters(self):
        # Given
        book_an_offer_mock = MagicMock()
        book_an_offer_mock.execute = MagicMock()

        user_id = 12
        stock_id = 15

        # When
        create_booking_for_user_on_specific_stock(
            user_id,
            stock_id,
            book_an_offer_mock,
        )

        # Then
        book_an_offer_mock.execute.assert_called_once()
        use_case_parameters = book_an_offer_mock.execute.call_args[0][0]
        assert isinstance(use_case_parameters, BookingInformation)
        assert use_case_parameters.user_id == user_id
        assert use_case_parameters.stock_id == stock_id
        assert use_case_parameters.quantity == 1


class CreateBookingForUserOnSpecificStockBypassingCappingLimitsTest:
    @clean_database
    @patch('scripts.booking.create_booking_for_user_on_specific_stock.redis')
    def should_book_an_offer_even_if_physical_offer_capping_is_exeeded(self, mocked_redis, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        old_offer = create_offer_with_thing_product(venue, thing_type=ThingType.INSTRUMENT)
        old_stock = create_stock(offer=old_offer, price=200)
        old_booking = create_booking(user, stock=old_stock, amount=old_stock.price)
        new_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION)
        new_stock = create_stock(offer=new_offer, price=10)

        repository.save(old_booking, new_stock)

        # When
        create_booking_for_user_on_specific_stock_bypassing_capping_limits(user.id, new_stock.id)

        # Then
        assert BookingSQLEntity.query.filter_by(stockId=new_stock.id, userId=user.id).one() is not None
        mocked_redis.add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=new_offer.id)
