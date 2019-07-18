from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_event_occurrence, \
    create_offer_with_event_product, \
    create_offerer, \
    create_stock_from_event_occurrence, \
    create_user, \
    create_user_offerer, \
    create_venue

DEACTIVATE_OFFERS_URL = '/offers/deactivate'

class Put:
    class Returns401:
        def when_deactivate_and_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).put(
                DEACTIVATE_OFFERS_URL,
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401

    class Returns200:
        @clean_database
        def test_deactivate_all_user_offer(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence1 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1, soft_deleted=True)
            PcObject.save(
                stock1,
                user_offerer
            )

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
            .put(
                DEACTIVATE_OFFERS_URL,
                headers={'origin': 'http://localhost:3000'}
            )

            # Then
            assert response.status_code == 200
