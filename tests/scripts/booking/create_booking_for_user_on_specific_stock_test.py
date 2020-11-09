from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Booking
from pcapi.models import ThingType
from pcapi.repository import repository
from pcapi.scripts.booking.create_booking_for_user_on_specific_stock import (
    create_booking_for_user_on_specific_stock_bypassing_capping_limits,
)


class CreateBookingForUserOnSpecificStockBypassingCappingLimitsTest:
    @pytest.mark.usefixtures("db_session")
    @patch('pcapi.scripts.booking.create_booking_for_user_on_specific_stock.redis')
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
        assert Booking.query.filter_by(stockId=new_stock.id, userId=user.id).one() is not None
        mocked_redis.add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=new_offer.id)
