import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_favorite, create_mediation, \
    API_URL
from tests.model_creators.specific_creators import create_offer_with_thing_product


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_logged_in_but_has_no_favorites(self, app):
            # Given
            user = create_user()
            PcObject.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + '/favorites')

            # Then
            assert response.status_code == 200
            assert response.json == []

        @clean_database
        def when_user_is_logged_in_and_has_two_favorite_offers(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer1 = create_offer_with_thing_product(venue, thumb_count=0)
            mediation1 = create_mediation(offer1, is_active=True)
            favorite1 = create_favorite(mediation1, offer1, user)
            offer2 = create_offer_with_thing_product(venue, thumb_count=0)
            mediation2 = create_mediation(offer2, is_active=True)
            favorite2 = create_favorite(mediation2, offer2, user)
            PcObject.save(user, favorite1, favorite2)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + '/favorites')

            # Then
            assert response.status_code == 200
            assert len(response.json) == 2
            first_favorite = response.json[0]
            assert 'offer' in first_favorite
            assert 'venue' in first_favorite['offer']
            assert 'validationToken' not in first_favorite['offer']['venue']

    class Returns401:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()) \
                .get(API_URL + '/favorites')

            # Then
            assert response.status_code == 401
