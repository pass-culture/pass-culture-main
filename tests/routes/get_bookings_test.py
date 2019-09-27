from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_venue, create_offerer, \
    create_user, create_booking, create_favorite
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def expect_all_bookings_of_given_user(self, app):
            # Given
            user1 = create_user(email='user1+plus@email.fr')
            user2 = create_user(email='user2+plus@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, offer=offer, price=0)
            booking1 = create_booking(user1, stock, venue=venue, token='ABCDEF')
            booking2 = create_booking(user2, stock, venue=venue, token='GHIJK')
            favorite1 = create_favorite(offer=offer, user=user1)
            favorite2 = create_favorite(offer=offer, user=user2)

            PcObject.save(booking1, booking2, favorite1, favorite2)

            # When
            response = TestClient(app.test_client()).with_auth(user1.email).get('/bookings')

            # Then
            response_json = response.json
            assert response.status_code == 200
            assert len(response_json[0]['user']['favorites']) == 1
