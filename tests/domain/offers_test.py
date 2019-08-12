from unittest.mock import Mock

from domain.offers import update_is_active_status
from models import Offer
from tests.conftest import clean_database
from tests.test_utils import create_offer_with_event_product, \
    create_offerer, \
    create_venue

find_thing = Mock()

offer = Offer()

class ChangeOfferStatusTest:
    class ThingOfferTest:
        @clean_database
        def test_activate_offer(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offers = [create_offer_with_event_product(venue, is_active=True), create_offer_with_event_product(venue, is_active=False)]

            # when
            updated_offers = update_is_active_status(offers, True)

            # then
            for offer in updated_offers:
                assert offer.isActive == True

        @clean_database
        def test_deactivate_offer(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offers = [create_offer_with_event_product(venue, is_active=True), create_offer_with_event_product(venue, is_active=False)]

            # when
            updated_offers = update_is_active_status(offers, False)

            # then
            for offer in updated_offers:
                assert offer.isActive == False
