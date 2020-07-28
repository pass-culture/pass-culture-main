import pytest
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import API_URL, create_booking, \
    create_favorite, create_mediation, create_offerer, create_stock, create_user, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product

from repository import repository
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
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)
            repository.save(user, favorite)
            url = f'{API_URL}/favorites/{humanize(favorite.id)}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(url)

            # Then
            assert response.status_code == 200
            response_content = response.json
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
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)
            stock = create_stock(offer=offer, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking, favorite)
            url = f'{API_URL}/favorites/{humanize(favorite.id)}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(url)

            # Then
            assert response.status_code == 200
            response_content = response.json
            assert 'offer' in response_content
            assert 'venue' in response_content['offer']
            assert humanize(booking.id) in response_content['firstMatchingBooking']["id"]
            assert 'validationToken' not in response_content['offer']['venue']

    class Returns401:
        def when_user_is_not_logged_in(self, app):
            # Given
            url = f'{API_URL}/favorites/ABCD'

            # When
            response = TestClient(app.test_client()) \
                .get(url)

            # Then
            assert response.status_code == 401

    class Returns404:
        @clean_database
        def when_user_is_logged_in_but_has_no_favorite(self, app):
            # Given
            url = f'{API_URL}/favorites/ABCD'
            user = create_user()
            repository.save(user)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(url)

            # Then
            assert response.status_code == 404
