from models import PcObject, Favorite
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_recommendation, \
    create_favorite, create_mediation, API_URL
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


class Delete:
    class Returns204:
        @clean_database
        def when_favorite_exists_with_offerId(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(
                offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = None
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation)
            favorite = create_favorite(mediation, offer, user)
            PcObject.save(recommendation, user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).delete(
                f'{API_URL}/favorites/{humanize(offer.id)}')

            # Then
            assert response.status_code == 200
            assert 'id' in response.json
            deleted_favorite = Favorite.query.first()
            assert deleted_favorite is None

    class Returns404:
        @clean_database
        def when_expected_parameters_are_not_given(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            favorite = create_favorite(mediation, offer, user)
            PcObject.save(recommendation, user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).delete(
                f'{API_URL}/favorites/1')

            # Then
            assert response.status_code == 404

        @clean_database
        def when_favorite_does_not_exist(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            favorite = create_favorite(mediation, offer, user)
            PcObject.save(recommendation, user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).delete(
                f'{API_URL}/favorites/ABCD/ABCD')

            # Then
            assert response.status_code == 404
            deleted_favorite = Favorite.query.first()
            assert deleted_favorite == favorite
