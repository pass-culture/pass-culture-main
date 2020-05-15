from datetime import datetime, timedelta
from unittest.mock import patch

from shapely.geometry import Polygon

from models import Feature, DiscoveryViewV3, ThingType
from models.feature import FeatureToggle
from repository import repository, discovery_view_v3_queries
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_mediation, \
    create_iris, create_iris_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_with_thing_offer, \
    create_stock_from_offer, create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence
from tests.test_utils import POLYGON_TEST
from utils.human_ids import humanize

RECOMMENDATION_URL_V3 = '/recommendations/v3'


class Put:
    class Returns403:
        @clean_database
        def when_feature_is_not_active(self, app):
            # Given
            user = create_user(can_book_free_offers=True, departement_code='973', is_admin=False)
            feature = Feature.query.filter_by(name=FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION).first()
            feature.isActive = False
            repository.save(feature, user)
            reads = [
                {"id": humanize(1), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(2), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(3), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            response = auth_request.put(RECOMMENDATION_URL_V3,
                                        json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 403

    class Returns200:
        @patch('routes.recommendations.create_recommendations_for_discovery_v3')
        @patch('routes.recommendations.current_user')
        @patch('routes.recommendations.serialize_recommendations')
        @patch('routes.recommendations.update_read_recommendations')
        @clean_database
        def when_feature_is_active_and_user_is_geolocated(self, mock_update_read_recommendations,
                                                          mock_serialize_recommendations,
                                                          mock_current_user,
                                                          mock_create_recommendations_for_discovery_v3, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thing_name='Guitar for dummies')
            mediation = create_mediation(offer, is_active=True)

            stock = create_stock_from_offer(offer, price=14)

            user_latitude = 49.894171
            user_longitude = 2.295695
            iris = create_iris(POLYGON_TEST)
            iris_venue = create_iris_venue(iris, venue)

            feature = Feature.query.filter_by(name=FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION).first()
            feature.isActive = True

            repository.save(user, stock, mediation, feature, iris_venue)
            discovery_view_v3_queries.refresh(concurrently=False)

            reads = [
                {"id": humanize(1), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(2), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(3), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}',
                                        json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 200
            mock_update_read_recommendations.assert_called_once()
            mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                 user_iris_id=iris.id,
                                                                                 user_is_geolocated=True,
                                                                                 sent_offers_ids=[],
                                                                                 limit=30)

        @patch('routes.recommendations.create_recommendations_for_discovery_v3')
        @patch('routes.recommendations.current_user')
        @patch('routes.recommendations.serialize_recommendations')
        @clean_database
        def when_feature_is_active_and_user_is_not_located(self, mock_serialize_recommendations,
                                                           mock_current_user,
                                                           mock_create_recommendations_for_discovery_v3, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue)
            create_mediation(offer1)
            stock1 = create_stock_from_offer(offer1, price=0)

            repository.save(user, stock1)

            discovery_view_v3_queries.refresh(concurrently=False)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3,
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 200
            mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                 user_iris_id=None,
                                                                                 user_is_geolocated=False,
                                                                                 sent_offers_ids=[],
                                                                                 limit=30)

        @patch('routes.recommendations.create_recommendations_for_discovery_v3')
        @patch('routes.recommendations.current_user')
        @patch('routes.recommendations.serialize_recommendations')
        @clean_database
        def when_feature_is_active_and_user_is_located_outside_known_iris(self, mock_serialize_recommendations,
                                                                          mock_current_user,
                                                                          mock_create_recommendations_for_discovery_v3,
                                                                          app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            digital_venue = create_venue(offerer, is_virtual=True, siret=None)
            offer = create_offer_with_thing_product(venue, thing_name='Guitar for dummies')
            digital_offer = create_offer_with_thing_product(digital_venue, thing_type=ThingType.JEUX_VIDEO,
                                                            url='https://url.com', is_national=True)
            mediation = create_mediation(offer, is_active=True)
            mediation_of_digital_offer = create_mediation(digital_offer, is_active=True)

            stock = create_stock_from_offer(offer, price=14)
            stock_of_digital_offer = create_stock_from_offer(digital_offer, price=14)

            user_latitude = 0
            user_longitude = 0

            feature = Feature.query.filter_by(name=FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION).first()
            feature.isActive = True

            repository.save(user, stock, stock_of_digital_offer, mediation, mediation_of_digital_offer, feature)
            discovery_view_v3_queries.refresh(concurrently=False)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}',
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 200
            mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                 user_iris_id=None,
                                                                                 user_is_geolocated=True,
                                                                                 sent_offers_ids=[],
                                                                                 limit=30)

        @clean_database
        def test_returns_same_quantity_of_recommendations_in_different_orders(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(user)

            for i in range(0, 10):
                offer_event = create_offer_with_event_product(venue, thumb_count=1)
                event_occurrence = create_event_occurrence(
                    offer_event,
                    beginning_datetime=four_days_from_now
                )
                event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=20)
                offer_thing = create_offer_with_thing_product(venue)
                stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
                create_mediation(offer_thing)
                create_mediation(offer_event)
                repository.save(event_stock, stock_thing)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            discovery_view_v3_queries.refresh(concurrently=False)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            recommendations1 = auth_request.put(
                f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}',
                json={'offersSentInLastCall': []})
            recommendations2 = auth_request.put(
                f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}',
                json={'offersSentInLastCall': []})

            # then
            assert recommendations1.status_code == 200
            assert recommendations2.status_code == 200
            assert len(recommendations1.json) == 20
            assert len(recommendations1.json) == len(recommendations2.json)
            assert any(
                [recommendations1.json[i]['id'] != recommendations2.json[i]['id'] for i in
                 range(0, len(recommendations1.json))])

    class Returns401:
        def when_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).put(
                RECOMMENDATION_URL_V3,
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401
