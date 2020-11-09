import pytest

from pcapi.core import testing
import pcapi.core.recommendations.factories as recommendations_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


RECOMMENDATION_URL = '/recommendations'


@pytest.mark.usefixtures("db_session")
class Returns200:
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
        assert response.json['mediationId'] is None

    def when_mediation_id_is_given(self, app):
        recommendation = recommendations_factories.RecommendationFactory(
            user__email='test@example.com',
        )
        offer = recommendation.offer

        # When
        path = '/recommendations/offers/{}?mediationId={}'.format(
            humanize(offer.id),
            humanize(recommendation.mediationId)
        )
        client = TestClient(app.test_client()).with_auth(email='test@example.com')
        response = client.get(path)

        # Then
        assert response.status_code == 200
        assert response.json['id'] == humanize(recommendation.id)
        assert response.json['offerId'] == humanize(offer.id)
        assert response.json['mediationId'] == humanize(recommendation.mediation.id)


@pytest.mark.usefixtures("db_session")
class Returns404:
    def when_recommendation_is_not_found(self, app):
        # Given
        users_factories.UserFactory(email='test@example.com')

        # When
        path = '/recommendations/offers/AE'
        client = TestClient(app.test_client()).with_auth(email='test@example.com')
        response = client.get(path)

        # Then
        assert response.status_code == 404
