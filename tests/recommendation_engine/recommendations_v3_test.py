from models.discovery_view import DiscoveryView
from recommendations_engine.recommendations import create_recommendations_for_discovery_v3
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_mediation, \
    create_offerer, create_recommendation, \
    create_user, create_venue, create_iris, create_iris_venue
from tests.model_creators.specific_creators import \
    create_offer_with_thing_product, create_stock_from_offer
from tests.test_utils import POLYGON_TEST
from utils.human_ids import humanize


class CreateRecommendationsForDiscoveryTest:
    @clean_database
    def test_does_not_put_mediation_ids_of_inactive_mediations(self, app):
        # Given
        seen_recommendation_ids = []
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock_from_offer(offer1, price=0)
        mediation1 = create_mediation(offer1, is_active=False)
        offer2 = create_offer_with_thing_product(venue)
        stock2 = create_stock_from_offer(offer2, price=0)
        mediation2 = create_mediation(offer2, is_active=False)
        mediation3 = create_mediation(offer2, is_active=True)

        iris = create_iris(POLYGON_TEST)
        repository.save(user, stock1, mediation1, stock2, mediation2, mediation3)
        iris_venue = create_iris_venue(iris, venue)
        repository.save(iris_venue)

        DiscoveryView.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery_v3(seen_recommendation_ids=seen_recommendation_ids,
                                                                  user_iris_id=iris.id,
                                                                  user=user)

        # Then
        mediations = list(map(lambda x: x.mediationId, recommendations))
        assert len(recommendations) == 1
        assert mediation3.id in mediations
        assert humanize(mediation2.id) not in mediations
        assert humanize(mediation1.id) not in mediations

    @clean_database
    def test_should_include_recommendations_on_offers_previously_displayed_in_search_results(
            self, app):
        # Given
        seen_recommendation_ids = []
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thumb_count=0)
        stock1 = create_stock_from_offer(offer1, price=0)
        mediation1 = create_mediation(offer1, is_active=True)
        offer2 = create_offer_with_thing_product(venue, thumb_count=0)
        stock2 = create_stock_from_offer(offer2, price=0)
        mediation2 = create_mediation(offer2, is_active=True)

        recommendation = create_recommendation(offer=offer2, user=user, mediation=mediation2, search="bla")

        iris = create_iris(POLYGON_TEST)
        repository.save(user, stock1, mediation1, stock2, mediation2, recommendation)
        iris_venue = create_iris_venue(iris, venue)
        repository.save(iris_venue)

        DiscoveryView.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery_v3(seen_recommendation_ids=seen_recommendation_ids,
                                                                  user_iris_id=iris.id,
                                                                  user=user)

        # Then
        assert len(recommendations) == 2
