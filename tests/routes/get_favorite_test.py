import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user, create_offerer, create_venue, create_offer_with_thing_product, \
    create_mediation, create_favorite, create_booking, create_stock
from utils.human_ids import humanize


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_logged_in_and_a_favorite_exist(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            favorite = create_favorite(mediation, offer, user)
            PcObject.save(user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + f'/favorites/{humanize(favorite.id)}')

            # Then
            assert response.status_code == 200
            response_content= response.json
            assert 'offer' in response_content
            assert 'venue' in response_content['offer']
            assert 'validationToken' not in response_content['offer']['venue']

        @clean_database
        def when_user_is_logged_in_and_a_favorite_booked_offer_exist(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            favorite = create_favorite(mediation, offer, user)
            stock = create_stock(price=0, offer=offer)
            booking = create_booking(user, stock)

            PcObject.save(booking, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + f'/favorites/{humanize(favorite.id)}')

            # Then
            assert response.status_code == 200
            response_content= response.json
            assert 'offer' in response_content
            assert 'venue' in response_content['offer']
            assert humanize(booking.id) in response_content['firstMatchingBooking']["id"]
            assert 'qrCode' in response_content['firstMatchingBooking']
            assert 'validationToken' not in response_content['offer']['venue']

    class Returns403:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()) \
                .get(API_URL + f'/favorites/ABCD')

            # Then
            assert response.status_code == 401

    class Returns404:
        @clean_database
        def when_user_is_logged_in_but_has_no_favorite(self, app):
            # Given
            user = create_user()
            PcObject.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + '/favorites/ABCD')

            # Then
            assert response.status_code == 404


