from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_offer_with_event_product, \
    create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_venue
from utils.human_ids import humanize

RECOMMENDATION_URL = API_URL + '/recommendations'


class Get:
    class Returns200:
        @clean_database
        def when_mediation_id_is_not_given(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user = create_user(email='user@test.com')
            recommendation = create_recommendation(offer, user)
            PcObject.save(recommendation)

            # When
            path = '/recommendations/offers/{}'.format(humanize(offer.id))
            response = TestClient() \
                .with_auth(email='user@test.com') \
                .get(API_URL + path)

            # Then
            assert response.status_code == 200
            assert response.json()['id'] == humanize(recommendation.id)
            assert response.json()['offerId'] == humanize(offer.id)

        @clean_database
        def when_mediation_id_is_given(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            mediation1 = create_mediation(offer)
            mediation2 = create_mediation(offer)
            user = create_user(email='user@test.com')
            recommendation1 = create_recommendation(offer, user, mediation=mediation1)
            recommendation2 = create_recommendation(offer, user, mediation=mediation2)
            PcObject.save(recommendation1, recommendation2)

            # When
            path = '/recommendations/offers/{}?mediationId={}'.format(
                humanize(offer.id),
                humanize(recommendation1.mediationId)
            )
            response = TestClient() \
                .with_auth(email='user@test.com') \
                .get(API_URL + path)

            # Then
            assert response.status_code == 200
            assert response.json()['id'] == humanize(recommendation1.id)
            assert response.json()['offerId'] == humanize(offer.id)
            assert response.json()['mediationId'] == humanize(mediation1.id)
            assert response.json()['offer']['product']['offerType']['proLabel'] == 'Spectacle vivant'

    class Returns404:
        @clean_database
        def when_recommendation_is_not_found(self, app):
            # Given
            user = create_user(email='user@test.com')
            PcObject.save(user)

            # When
            path = '/recommendations/offers/AE'
            response = TestClient() \
                .with_auth(email='user@test.com') \
                .get(API_URL + path)

            # Then
            assert response.status_code == 404
            assert response.json()['global'] == ["Offre ou médiation introuvable"]
