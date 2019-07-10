from models import PcObject, ThingType, Favorite
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, API_URL, create_offerer, create_venue, create_offer_with_thing_product, \
    create_mediation, create_recommendation
from utils.human_ids import humanize


class Post:
    class Returns401:
        @clean_database
        def when_offer_id_is_not_received(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.save(user)

            json = {
                'mediationId': 'DA',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).post(
                f'{API_URL}/offers/favorites',
                json=json)

            # Then
            assert response.status_code == 401
            assert response.json['global'] == ["Les paramères offerId et mediationId sont obligatoires"]

        @clean_database
        def when_mediation_id_is_not_received(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.save(user)

            json = {
                'offerId': 'BA',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).post(
                f'{API_URL}/offers/favorites',
                json=json)

            # Then
            assert response.status_code == 401
            assert response.json['global'] == ["Les paramères offerId et mediationId sont obligatoires"]

    class Returns404:
        @clean_database
        def when_offer_is_not_found(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            PcObject.save(recommendation, user)

            json = {
                'offerId': 'ABCD',
                'mediationId': humanize(mediation.id),
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).post(
                f'{API_URL}/offers/favorites',
                json=json)

            # Then
            assert response.status_code == 404

        @clean_database
        def when_mediation_is_not_found(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            PcObject.save(recommendation, user)

            json = {
                'offerId': humanize(offer.id),
                'mediationId': 'ABCD',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).post(
                f'{API_URL}/offers/favorites',
                json=json)

            # Then
            assert response.status_code == 404


    class Returns201:
        @clean_database
        def when_offer_is_add_as_favorite_for_current_user(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            PcObject.save(recommendation, user)

            json = {
                'offerId': humanize(offer.id),
                'mediationId': humanize(mediation.id),
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).post(
                f'{API_URL}/offers/favorites',
                json=json)

            # Then
            assert response.status_code == 201

            favorite = Favorite.query.one()
            assert favorite.offerId == offer.id
            assert favorite.mediationId == mediation.id
            assert favorite.userId == user.id
