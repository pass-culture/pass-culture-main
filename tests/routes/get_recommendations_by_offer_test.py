import pytest

import pcapi.core.recommendations.factories as recommendations_factories
from pcapi.core import testing
from pcapi.repository import repository
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import create_user, create_offerer, create_venue, create_recommendation, \
    create_mediation
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.utils.human_ids import humanize

RECOMMENDATION_URL = '/recommendations'


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_mediation_id_is_not_given(self, app, assert_num_queries):
            recommendation = recommendations_factories.RecommendationFactory(
                user__email='test@example.com',
                mediation=None,
            )

            offer = recommendation.offer

            # When
            n_queries = testing.AUTHENTICATION_QUERIES
            n_queries += 2  # fetch data: select offer and recommendation
            n_queries += 6  # serializer: mediation, product, stock, venue, offerer, bookings
            client = TestClient(app.test_client()).with_auth(email='test@example.com')
            with assert_num_queries(n_queries):
                path = '/recommendations/offers/{}'.format(humanize(offer.id))
                response = client.get(path)

            # Then
            assert response.status_code == 200
            assert response.json['id'] == humanize(recommendation.id)
            assert response.json['offerId'] == humanize(offer.id)

        @pytest.mark.usefixtures("db_session")
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
            repository.save(recommendation1, recommendation2)

            # When
            path = '/recommendations/offers/{}?mediationId={}'.format(
                humanize(offer.id),
                humanize(recommendation1.mediationId)
            )
            response = TestClient(app.test_client()) \
                .with_auth(email='user@test.com') \
                .get(path)

            # Then
            assert response.status_code == 200
            assert response.json['id'] == humanize(recommendation1.id)
            assert response.json['offerId'] == humanize(offer.id)
            assert response.json['mediationId'] == humanize(mediation1.id)
            assert response.json['offer']['offerType']['proLabel'] == 'Spectacle vivant'

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_recommendation_is_not_found(self, app):
            # Given
            user = create_user(email='user@test.com')
            repository.save(user)

            # When
            path = '/recommendations/offers/AE'
            response = TestClient(app.test_client()) \
                .with_auth(email='user@test.com') \
                .get(path)

            # Then
            assert response.status_code == 404
