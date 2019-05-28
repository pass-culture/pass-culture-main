import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_offerer, \
    create_user, \
    create_user_offerer, \
    create_venue, create_offer_with_thing_product

@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights(self, app):
            # given
                user = create_user(email='user@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue)

                PcObject.save(user, user_offerer, offer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + '/offers')

            # then
                response_json = response.json()
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "pas encore de stock"
                assert response_json[0]['bookingEmail'] == 'booking.email@test.com'
                assert response_json[0]['stocks'] == []
                assert response_json[0]['productId'] is not None
                assert response_json[0]['product']['offerType'] is not None
                assert response_json[0]['venue'] is not None

