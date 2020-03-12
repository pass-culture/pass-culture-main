from datetime import datetime, timedelta
from unittest.mock import patch

from shapely.geometry import Polygon

from models import Feature, DiscoveryView, Recommendation, Mediation
from models.feature import FeatureToggle
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_mediation, \
    create_recommendation, create_booking, create_iris, create_iris_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_with_thing_offer, \
    create_stock_from_offer, create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence
from tests.test_utils import POLYGON_TEST
from utils.human_ids import humanize
from utils.tutorials import upsert_tuto_mediations

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
        @patch('routes.recommendations.update_read_recommendations')
        @clean_database
        def when_feature_is_active(self, mock_update_read_recommendations, app):
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
            DiscoveryView.refresh(concurrently=False)

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
            recommendations = response.json
            stocks = recommendations[0]['offer']['stocks']
            assert all('isBookable' in stock for stock in stocks)

        @clean_database
        def when_user_is_not_located(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue)
            create_mediation(offer1)
            stock1 = create_stock_from_offer(offer1, price=0)

            repository.save(user, stock1)

            DiscoveryView.refresh(concurrently=False)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3,
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            response_json = response.json
            assert len(response_json) == 0

        @clean_database
        def when_a_recommendation_is_requested(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue)
            offer2 = create_offer_with_event_product(venue)
            offer3 = create_offer_with_thing_product(venue)
            offer4 = create_offer_with_thing_product(venue)
            now = datetime.utcnow()
            event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                                       end_datetime=now + timedelta(hours=74))
            create_mediation(offer1)
            create_mediation(offer2)
            create_mediation(offer3)
            create_mediation(offer4)
            stock1 = create_stock_from_offer(offer1, price=0)
            stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10, soft_deleted=False,
                                                        booking_limit_date=now + timedelta(days=3))
            stock3 = create_stock_from_offer(offer3, price=0)
            stock4 = create_stock_from_offer(offer4, price=0)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock1, stock2, stock3, stock4)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            DiscoveryView.refresh(concurrently=False)

            offer1_id = offer1.id
            offer2_id = offer2.id
            offer3_id = offer3.id
            offer4_id = offer4.id

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}&offerId={humanize(offer1.id)}',
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            response_json = response.json
            assert len(response_json) == 4
            offer_ids = set(map(lambda x: x['offer']['id'], response_json))
            assert response_json[0]['offer']['id'] == humanize(offer1_id)
            assert humanize(offer1_id) in offer_ids
            assert humanize(offer2_id) in offer_ids
            assert humanize(offer3_id) in offer_ids
            assert humanize(offer4_id) in offer_ids

        @clean_database
        def when_a_recommendation_with_an_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            repository.save(user, stock_thing, mediation)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock_thing, mediation)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}&offerId={humanize(offer_thing.id)}&mediationId={humanize(mediation.id)}' ,
                                        json={'seenRecommendationIds': []})
            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['mediationId'] == humanize(mediation.id)

        @clean_database
        def when_a_recommendation_with_an_offer_and_no_mediation_is_requested(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock_thing, mediation)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            mediation_id = mediation.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}&offerId={humanize(offer_thing.id)}',
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['mediationId'] == humanize(mediation_id)

        @clean_database
        def when_a_recommendation_with_no_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock_thing, mediation)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            offer_thing_id = offer_thing.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}&mediationId={humanize(mediation.id)}',
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['offerId'] == humanize(offer_thing_id)

        @clean_database
        def when_tutos_are_not_already_read(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user = create_user()
            event_occurrence1 = create_event_occurrence(offer)
            event_occurrence2 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            stock2 = create_stock_from_event_occurrence(event_occurrence2)
            thing_offer1 = create_offer_with_thing_product(venue)
            thing_offer2 = create_offer_with_thing_product(venue)
            stock3 = create_stock_from_offer(thing_offer1)
            stock4 = create_stock_from_offer(thing_offer2)
            create_mediation(thing_offer1)
            create_mediation(thing_offer2)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock1, stock2, stock3, stock4, user)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            DiscoveryView.refresh(concurrently=False)

            upsert_tuto_mediations()

            # when
            auth_request = TestClient(app.test_client()).with_auth(user.email)
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}', json={})

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert recommendations[0]['mediation']['tutoIndex'] == 0
            assert recommendations[1]['mediation']['tutoIndex'] == 1

        @clean_database
        def when_tutos_are_already_read(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user = create_user()
            event_occurrence1 = create_event_occurrence(offer)
            event_occurrence2 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            stock2 = create_stock_from_event_occurrence(event_occurrence2)
            thing_offer1 = create_offer_with_thing_product(venue)
            thing_offer2 = create_offer_with_thing_product(venue)
            stock3 = create_stock_from_offer(thing_offer1)
            stock4 = create_stock_from_offer(thing_offer2)

            user_latitude = 49.894171
            user_longitude = 2.295695
            venue_polygon = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                                     (2.795697, 47.894173), (2.795697, 50.994169)])

            iris = create_iris(venue_polygon)
            repository.save(user, stock1, stock2, stock3, stock4, user)
            iris_venue = create_iris_venue(iris, venue)
            repository.save(iris_venue)

            upsert_tuto_mediations()
            tuto_mediation0 = Mediation.query.filter_by(tutoIndex=0).one()
            tuto_mediation1 = Mediation.query.filter_by(tutoIndex=1).one()
            tuto_recommendation0 = create_recommendation(user=user, mediation=tuto_mediation0)
            tuto_recommendation1 = create_recommendation(user=user, mediation=tuto_mediation1)
            repository.save(tuto_recommendation0, tuto_recommendation1)

            humanized_tuto_recommendation0_id = humanize(tuto_recommendation0.id)
            humanized_tuto_recommendation1_id = humanize(tuto_recommendation1.id)
            reads = [
                {
                    "id": humanized_tuto_recommendation0_id,
                    "dateRead": "2018-12-17T15:59:11.689Z"
                },
                {
                    "id": humanized_tuto_recommendation1_id,
                    "dateRead": "2018-12-17T15:59:15.689Z"
                }
            ]
            data = {'readRecommendations': reads}
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}', json=data)

            # then
            assert response.status_code == 200
            recommendations = response.json
            recommendation_ids = [r['id'] for r in recommendations]
            assert humanized_tuto_recommendation0_id not in recommendation_ids
            assert humanized_tuto_recommendation1_id not in recommendation_ids

        @clean_database
        def test_returns_same_quantity_of_recommendations_in_different_orders(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(user)

            for i in range(0, 10):
                offer_event = create_offer_with_event_product(venue, thumb_count=1)
                event_occurrence = create_event_occurrence(
                    offer_event,
                    beginning_datetime=four_days_from_now,
                    end_datetime=eight_days_from_now
                )
                event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
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

            DiscoveryView.refresh(concurrently=False)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            recommendations1 = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}', json={'seenRecommendationIds': []})
            recommendations2 = auth_request.put(f'{RECOMMENDATION_URL_V3}?longitude={user_longitude}&latitude={user_latitude}', json={'seenRecommendationIds': []})

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

    class Returns404:
        @clean_database
        def when_given_mediation_does_not_match_given_offer(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing_1 = create_offer_with_thing_product(venue, thumb_count=1)
            offer_thing_2 = create_offer_with_thing_product(venue, thumb_count=1)
            stock_thing_1 = create_stock_with_thing_offer(offerer, venue, offer_thing_1, price=0)
            stock_thing_2 = create_stock_with_thing_offer(offerer, venue, offer_thing_2, price=0)
            mediation_1 = create_mediation(offer_thing_1)
            mediation_2 = create_mediation(offer_thing_2)
            repository.save(user, stock_thing_1, stock_thing_2, mediation_1, mediation_2)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        "?offerId=" + humanize(offer_thing_1.id) +
                                        "?mediationId=" + humanize(mediation_2.id),
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_known(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_with_thing = create_offer_with_thing_product(venue, thumb_count=1)
            stock_with_thing = create_stock_with_thing_offer(offerer, venue, offer_with_thing, price=0)
            mediation = create_mediation(offer_with_thing)
            repository.save(user, stock_with_thing, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        "?offerId=ABCDE" +
                                        "&mediationId=" + humanize(mediation.id),
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_mediation_is_unknown(self, app):
            # given
            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        "?mediationId=ABCDE",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_known_and_mediation_is_unknown(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            repository.save(user, stock_thing, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        "?offerId=" + humanize(offer_thing.id) +
                                        "&mediationId=ABCDE",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_unknown(self, app):
            # given
            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        "?offerId=ABCDE" +
                                        "&mediationId=ABCDE",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_venue_of_given_offer_is_not_validated(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            offer1 = create_offer_with_thing_product(venue, thumb_count=1)
            stock1 = create_stock_from_offer(offer1, price=0)
            repository.save(user, stock1)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            data = {'seenRecommendationIds': []}
            # when
            response = auth_request.put(RECOMMENDATION_URL_V3 +
                                        '?offerId=%s' % humanize(offer1.id),
                                        json=data)

            # then
            assert response.status_code == 404
