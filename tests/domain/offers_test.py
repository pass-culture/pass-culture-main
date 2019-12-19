from unittest.mock import Mock

from domain.offers import update_is_active_status
from models import Offer
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product

find_thing = Mock()

offer = Offer()


class ChangeOfferStatusTest:
    class ThingOfferTest:
        @clean_database
        def test_activate_offer(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offers = [create_offer_with_event_product(venue, is_active=True),
                      create_offer_with_event_product(venue, is_active=False)]
            status = True

            # when
            updated_offers = update_is_active_status(offers, status)

            # then
            for updated_offer in updated_offers:
                assert updated_offer.isActive

        @clean_database
        def test_deactivate_offer(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offers = [create_offer_with_event_product(venue, is_active=True),
                      create_offer_with_event_product(venue, is_active=False)]
            status = False

            # when
            updated_offers = update_is_active_status(offers, status)

            # then
            for updated_offer in updated_offers:
                assert not updated_offer.isActive

        @clean_database
        def test_deactivate_offer_should_keep_booking_state(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            existing_offer = create_offer_with_event_product(venue, is_active=True)
            stock = create_stock(offer=existing_offer)
            booking = create_booking(user=user, stock=stock)
            offers = [existing_offer]
            status = False

            # when
            updated_offers = update_is_active_status(offers, status)

            # then
            assert any(not updated_offer.isActive for updated_offer in updated_offers)
            assert not booking.isCancelled
