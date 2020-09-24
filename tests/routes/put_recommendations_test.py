from datetime import datetime, timedelta
from unittest.mock import patch

from models import ThingType
from models.recommendation import Recommendation
from repository import repository, discovery_view_queries, discovery_view_v3_queries
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_booking, \
    create_mediation, create_offerer, create_recommendation, \
    create_user, create_venue, create_iris_venue, create_iris
from tests.model_creators.specific_creators import create_event_occurrence, \
    create_offer_with_event_product, \
    create_offer_with_thing_product, create_stock_from_event_occurrence, \
    create_stock_from_offer, create_stock_with_thing_offer
from tests.test_utils import POLYGON_TEST
from utils.human_ids import humanize

RECOMMENDATION_URL = '/recommendations'


class Put:
    class Returns401:
        @clean_database
        def when_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).put(
                RECOMMENDATION_URL,
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401

    class Returns404:
        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_given_mediation_does_not_match_given_offer(self, mock_geolocation_feature, app):
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
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing_1.id) +
                                        "?mediationId=" + humanize(mediation_2.id),
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 404

        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_offer_is_unknown_and_mediation_is_known(self, mock_geolocation_feature, app):
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
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=ABCDE" +
                                        "&mediationId=" + humanize(mediation.id),
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 404

        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_mediation_is_unknown(self, mock_geolocation_feature, app):
            # given
            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?mediationId=ABCDE",
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 404

        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_offer_is_known_and_mediation_is_unknown(self, mock_geolocation_feature, app):
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
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing.id) +
                                        "&mediationId=ABCDE",
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 404

        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_offer_is_unknown_and_mediation_is_unknown(self, mock_geolocation_feature, app):
            # given
            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=ABCDE" +
                                        "&mediationId=ABCDE",
                                        json={'offersSentInLastCall': []})

            # then
            assert response.status_code == 404

        @patch('routes.recommendations.feature_queries.is_active', return_value=False)
        @clean_database
        def when_venue_of_given_offer_is_not_validated(self, mock_geolocation_feature, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            offer1 = create_offer_with_thing_product(venue, thumb_count=1)
            stock1 = create_stock_from_offer(offer1, price=0)
            repository.save(user, stock1)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            data = {'offersSentInLastCall': []}
            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        '?offerId=%s' % humanize(offer1.id),
                                        json=data)

            # then
            assert response.status_code == 404

    class Returns200:
        class WhenGeolocationFeatureIsDeactivated:
            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @patch('routes.recommendations.create_recommendations_for_discovery')
            @patch('routes.recommendations.create_recommendations_for_discovery_v3')
            @clean_database
            def when_updating_read_recommendations(self, mock_create_recommendations_for_discovery_v3,
                                                   mock_create_recommendations_for_discovery, mock_geolocation_feature,
                                                   app):
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
                recommendation1 = create_recommendation(offer, user)
                recommendation2 = create_recommendation(thing_offer1, user)
                recommendation3 = create_recommendation(thing_offer2, user)
                repository.save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                reads = [
                    {"id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689000Z"},
                    {"id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689000Z"},
                    {"id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689000Z"},
                ]
                data = {'readRecommendations': reads}
                # when
                response = auth_request.put(RECOMMENDATION_URL,
                                            json=data)

                # then
                assert response.status_code == 200
                mock_create_recommendations_for_discovery.assert_called_once()
                mock_create_recommendations_for_discovery_v3.assert_not_called()
                assert any(reco.dateRead is not None for reco in Recommendation.query.all())

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_user_has_no_offer_in_his_department(self, mock_geolocation_feature, app):
                # given
                user = create_user(can_book_free_offers=True, departement_code='973', is_admin=False)
                offerer = create_offerer()
                venue29 = create_venue(offerer, siret=offerer.siren + '98765', postal_code='29000',
                                       departement_code='29')
                venue34 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000',
                                       departement_code='34')
                venue93 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000',
                                       departement_code='93')
                venue67 = create_venue(offerer, siret=offerer.siren + '56789', postal_code='67000',
                                       departement_code='67')
                thing_offer1 = create_offer_with_thing_product(venue93, thing_name='thing 93', url=None,
                                                               is_national=False)
                thing_offer2 = create_offer_with_thing_product(venue67, thing_name='thing 67', url=None,
                                                               is_national=False)
                thing_offer3 = create_offer_with_thing_product(venue29, thing_name='thing 29', url=None,
                                                               is_national=False)
                thing_offer4 = create_offer_with_thing_product(venue34, thing_name='thing 34', url=None,
                                                               is_national=False)
                stock1 = create_stock_from_offer(thing_offer1)
                stock2 = create_stock_from_offer(thing_offer2)
                stock3 = create_stock_from_offer(thing_offer3)
                stock4 = create_stock_from_offer(thing_offer4)
                repository.save(user, stock1, stock2, stock3, stock4)

                # when
                response = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={'readRecommendations': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_user_has_one_offer_in_his_department(self, mock_geolocation_feature, app):
                # given
                user = create_user(can_book_free_offers=True, departement_code='93', is_admin=False)
                offerer = create_offerer()
                venue93 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000',
                                       departement_code='93')
                venue67 = create_venue(offerer, siret=offerer.siren + '56789', postal_code='67000',
                                       departement_code='67')
                thing_offer1 = create_offer_with_thing_product(venue93, thing_name='thing 93', url=None,
                                                               is_national=False)
                thing_offer2 = create_offer_with_thing_product(venue67, thing_name='thing 67', url=None,
                                                               is_national=False)
                stock1 = create_stock_from_offer(thing_offer1)
                stock2 = create_stock_from_offer(thing_offer2)
                create_mediation(thing_offer1)
                create_mediation(thing_offer2)
                repository.save(user, stock1, stock2)
                discovery_view_queries.refresh(concurrently=False)

                # when
                response = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={'readRecommendations': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 1
                recommendation_response = response.json[0]
                assert 'offer' in recommendation_response
                assert 'venue' in recommendation_response['offer']
                assert 'validationToken' not in recommendation_response['offer']['venue']
                assert 'managingOfferer' in recommendation_response['offer']['venue']
                assert 'validationToken' not in recommendation_response['offer']['venue']['managingOfferer']

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_soft_deleted_stocks(self, mock_geolocation_feature, app):
                # Given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                event_offer = create_offer_with_event_product(venue)
                now = datetime.utcnow()
                four_days_from_now = now + timedelta(days=4)
                event_occurrence1 = create_event_occurrence(event_offer,
                                                            beginning_datetime=four_days_from_now)
                event_occurrence2 = create_event_occurrence(event_offer,
                                                            beginning_datetime=four_days_from_now)
                soft_deleted_event_stock = create_stock_from_event_occurrence(event_occurrence1, soft_deleted=True)
                event_stock = create_stock_from_event_occurrence(event_occurrence2, soft_deleted=False)
                thing_offer1 = create_offer_with_thing_product(venue)
                thing_offer2 = create_offer_with_thing_product(venue)
                soft_deleted_thing_stock = create_stock_from_offer(thing_offer1, soft_deleted=True)
                thing_stock = create_stock_from_offer(thing_offer2, soft_deleted=False)
                create_mediation(thing_offer1)
                create_mediation(thing_offer2)
                create_mediation(event_offer)
                repository.save(user, event_stock, soft_deleted_event_stock, thing_stock, soft_deleted_thing_stock)
                discovery_view_queries.refresh(concurrently=False)

                event_offer_id = event_offer.id
                thing_offer2_id = thing_offer2.id

                # When
                response = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={})

                # Then
                recommendations = response.json
                assert len(recommendations) == 2
                offer_ids = [r['offerId'] for r in recommendations]
                assert humanize(event_offer_id) in offer_ids
                assert humanize(thing_offer2_id) in offer_ids

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_no_stocks(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_event_product(venue)
                repository.save(user, offer)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_a_thumb_count_for_thing_and_no_mediation(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, thumb_count=1)
                stock = create_stock_from_offer(offer, price=0)
                repository.save(user, stock)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_no_thumb_count_for_thing_and_no_mediation(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, thumb_count=0)
                stock = create_stock_from_offer(offer, price=0)
                repository.save(user, stock)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_no_thumb_count_for_thing_and_a_mediation(
                    self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, thumb_count=0)
                stock = create_stock_from_offer(offer, price=0)
                mediation = create_mediation(offer)
                repository.save(user, stock, mediation)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 1

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_no_thumb_count_for_event_and_no_mediation(self, mock_geolocation_feature, app):
                # given
                now = datetime.utcnow()
                four_days_from_now = now + timedelta(days=4)

                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_event_product(venue)
                event_occurrence = create_event_occurrence(
                    offer,
                    beginning_datetime=four_days_from_now
                )
                stock = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=20)
                repository.save(user, stock)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_no_thumb_count_for_event_and_have_mediation(
                    self, mock_geolocation_feature, app):
                # given
                now = datetime.utcnow()
                four_days_from_now = now + timedelta(days=4)

                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_event_product(venue)
                event_occurrence = create_event_occurrence(
                    offer,
                    beginning_datetime=four_days_from_now
                )
                mediation = create_mediation(offer)
                stock = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=20)
                repository.save(user, stock, mediation)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 1

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_a_thumb_count_for_event_and_no_mediation(
                    self, mock_geolocation_feature, app):
                # given
                now = datetime.utcnow()
                four_days_from_now = now + timedelta(days=4)

                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_event_product(venue, thumb_count=1)
                event_occurrence = create_event_occurrence(
                    offer,
                    beginning_datetime=four_days_from_now
                )
                stock = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=20)
                repository.save(user, stock)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 0

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_non_validated_venues(self, mock_geolocation_feature, app):
                # Given
                offerer = create_offerer()
                venue_not_validated = create_venue(offerer, siret=None, comment='random reason')
                venue_not_validated.generate_validation_token()
                venue_validated = create_venue(offerer, siret=None, comment='random reason')
                offer_venue_not_validated = create_offer_with_thing_product(venue_not_validated, thumb_count=1)
                offer_venue_validated = create_offer_with_thing_product(venue_validated, thumb_count=1)
                stock_venue_not_validated = create_stock_from_offer(offer_venue_not_validated)
                stock_venue_validated = create_stock_from_offer(offer_venue_validated)
                user = create_user()
                create_mediation(offer_venue_not_validated)
                create_mediation(offer_venue_validated)
                repository.save(stock_venue_not_validated, stock_venue_validated, user)
                discovery_view_queries.refresh(concurrently=False)

                venue_validated_id = venue_validated.id
                venue_not_validated_id = venue_not_validated.id
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # Then
                assert response.status_code == 200
                recommendations = response.json
                venue_ids = set(map(lambda x: x['offer']['venue']['id'], recommendations))
                assert humanize(venue_validated_id) in venue_ids
                assert humanize(venue_not_validated_id) not in venue_ids

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_offers_have_active_mediations(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer1 = create_offer_with_thing_product(venue, thumb_count=0)
                stock1 = create_stock_from_offer(offer1, price=0)
                mediation1 = create_mediation(offer1, is_active=False)
                offer2 = create_offer_with_thing_product(venue, thumb_count=0)
                stock2 = create_stock_from_offer(offer2, price=0)
                mediation2 = create_mediation(offer2, is_active=False)
                mediation3 = create_mediation(offer2, is_active=True)
                repository.save(user, stock1, mediation1, stock2, mediation2, mediation3)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)
                mediation3_id = mediation3.id
                mediation2_id = mediation2.id
                mediation1_id = mediation1.id

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                json = response.json
                mediation_ids = list(map(lambda x: x['mediationId'], json))
                assert humanize(mediation3_id) in mediation_ids
                assert humanize(mediation2_id) not in mediation_ids
                assert humanize(mediation1_id) not in mediation_ids

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_a_recommendation_is_requested(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer1 = create_offer_with_thing_product(venue)
                offer2 = create_offer_with_event_product(venue)
                offer3 = create_offer_with_thing_product(venue)
                offer4 = create_offer_with_thing_product(venue)
                now = datetime.utcnow()
                event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72))
                create_mediation(offer1)
                create_mediation(offer2)
                create_mediation(offer3)
                create_mediation(offer4)
                stock1 = create_stock_from_offer(offer1, price=0)
                stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=10, soft_deleted=False,
                                                            booking_limit_date=now + timedelta(days=3))
                stock3 = create_stock_from_offer(offer3, price=0)
                stock4 = create_stock_from_offer(offer4, price=0)
                repository.save(user, stock1, stock2, stock3, stock4)
                discovery_view_queries.refresh(concurrently=False)

                offer1_id = offer1.id
                offer2_id = offer2.id
                offer3_id = offer3.id
                offer4_id = offer4.id

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL +
                                            "?offerId=" + humanize(offer1.id),
                                            json={'offersSentInLastCall': []})

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

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def test_returns_two_recommendations_with_one_event_and_one_thing(self, mock_geolocation_feature, app):
                # given
                now = datetime.utcnow()
                four_days_from_now = now + timedelta(days=4)
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer_event = create_offer_with_event_product(venue)
                event_occurrence = create_event_occurrence(
                    offer_event,
                    beginning_datetime=four_days_from_now
                )
                event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, quantity=20)
                offer_thing = create_offer_with_thing_product(venue)
                stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
                create_mediation(offer_thing)
                create_mediation(offer_event)
                repository.save(user, event_stock, stock_thing)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                assert len(response.json) == 2

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def test_discovery_recommendations_should_not_include_search_recommendations(self, mock_geolocation_feature,
                                                                                         app):
                # Given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                venue_outside_dept = create_venue(offerer, postal_code='29100', siret='12345678912341')
                offer1 = create_offer_with_thing_product(venue, thumb_count=0)
                stock1 = create_stock_from_offer(offer1, price=0)
                mediation1 = create_mediation(offer1, is_active=True)
                offer2 = create_offer_with_thing_product(venue_outside_dept, thumb_count=0)
                stock2 = create_stock_from_offer(offer2, price=0)
                mediation2 = create_mediation(offer2, is_active=True)
                recommendation = create_recommendation(offer=offer2, user=user, mediation=mediation2, search="bla")
                repository.save(user, stock1, mediation1, stock2, mediation2, recommendation)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # When
                recommendations_req = auth_request.put(RECOMMENDATION_URL +
                                                       "?page=1", json={})

                # Then
                assert recommendations_req.status_code == 200
                recommendations = recommendations_req.json
                assert len(recommendations) == 1
                assert recommendations[0]['search'] is None

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_a_recommendation_with_an_offer_and_a_mediation_is_requested(self, mock_geolocation_feature, app):
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
                response = auth_request.put(RECOMMENDATION_URL +
                                            "?offerId=" + humanize(offer_thing.id) +
                                            "&mediationId=" + humanize(mediation.id), json={'offersSentInLastCall': []})
                # then
                assert response.status_code == 200
                recos = response.json
                assert recos[0]['mediationId'] == humanize(mediation.id)

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_a_recommendation_with_an_offer_and_no_mediation_is_requested(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
                stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
                mediation = create_mediation(offer_thing)
                repository.save(user, stock_thing, mediation)

                mediation_id = mediation.id
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL +
                                            "?offerId=" + humanize(offer_thing.id), json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                recos = response.json
                assert recos[0]['mediationId'] == humanize(mediation_id)

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_a_recommendation_with_no_offer_and_a_mediation_is_requested(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer_thing = create_offer_with_thing_product(venue, thumb_count=1)
                stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
                mediation = create_mediation(offer_thing)
                repository.save(user, stock_thing, mediation)

                offer_thing_id = offer_thing.id
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(RECOMMENDATION_URL +
                                            "?mediationId=" + humanize(mediation.id),
                                            json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                recos = response.json
                assert recos[0]['offerId'] == humanize(offer_thing_id)

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def test_returns_new_recommendation_with_active_mediation_for_already_existing_but_invalid_recommendations(
                    self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer1 = create_offer_with_thing_product(venue, thumb_count=0)
                stock1 = create_stock_from_offer(offer1, price=0)
                inactive_mediation = create_mediation(offer1, is_active=False)
                active_mediation = create_mediation(offer1, is_active=True)
                invalid_recommendation = create_recommendation(offer=offer1, user=user, mediation=inactive_mediation)
                repository.save(user, stock1, inactive_mediation, active_mediation, invalid_recommendation)
                discovery_view_queries.refresh(concurrently=False)

                active_mediation_id = active_mediation.id
                inactive_mediation_id = inactive_mediation.id
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                data = {'offersSentInLastCall': []}

                # when
                response = auth_request.put(RECOMMENDATION_URL, json=data)

                # then
                assert response.status_code == 200
                json = response.json
                mediation_ids = list(map(lambda x: x['mediationId'], json))
                assert humanize(active_mediation_id) in mediation_ids
                assert humanize(inactive_mediation_id) not in mediation_ids

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_stock_has_past_booking_limit_date(self, mock_geolocation_feature, app):
                # Given
                one_day_ago = datetime.utcnow() - timedelta(days=1)
                three_days_ago = datetime.utcnow() - timedelta(days=3)
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue)
                user = create_user()
                stock = create_stock_from_offer(offer, booking_limit_datetime=one_day_ago)
                recommendation = create_recommendation(offer, user, date_read=three_days_ago)

                repository.save(stock, recommendation)

                # When
                recommendations = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={})

                # Then
                assert recommendations.status_code == 200
                assert not recommendations.json

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_user_has_already_seen_offer_sent_in_last_call(self, mock_geolocation_feature, app):
                # given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
                offer = create_offer_with_thing_product(venue)
                mediation = create_mediation(offer, is_active=True)
                stock = create_stock_from_offer(offer)
                recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)

                repository.save(stock, recommendation)

                # when
                response = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={'offersSentInLastCall': [humanize(recommendation.id)]})

                # then
                assert response.status_code == 200
                assert response.json == []

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def test_returns_same_quantity_of_recommendations_in_different_orders(self, mock_geolocation_feature, app):
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

                discovery_view_queries.refresh(concurrently=False)
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                recommendations1 = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})
                recommendations2 = auth_request.put(RECOMMENDATION_URL, json={'offersSentInLastCall': []})

                # then
                assert recommendations1.status_code == 200
                assert recommendations2.status_code == 200
                assert len(recommendations1.json) == 20
                assert len(recommendations1.json) == len(recommendations2.json)
                assert any(
                    [recommendations1.json[i]['id'] != recommendations2.json[i]['id'] for i in
                     range(0, len(recommendations1.json))])

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def test_returns_stocks_with_isBookable_property(self, mock_geolocation_feature, app):
                # Given
                expired_booking_limit_date = datetime(1970, 1, 1)

                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, thing_name='Guitar for dummies')
                mediation = create_mediation(offer, is_active=True)

                create_stock_from_offer(offer, price=14)
                create_stock_from_offer(offer, price=26, booking_limit_datetime=expired_booking_limit_date)

                recommendation = create_recommendation(offer=offer, user=user, mediation=mediation)
                repository.save(user, recommendation)
                discovery_view_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # When
                recommendations_req = auth_request.put(RECOMMENDATION_URL, json={})

                # Then
                assert recommendations_req.status_code == 200
                recommendations = recommendations_req.json
                assert len(recommendations) == 1
                recommendation = recommendations[0]
                assert recommendation['offer']['name'] == 'Guitar for dummies'
                stocks_response = recommendation['offer']['stocks']
                assert len(stocks_response) == 2
                assert all('isBookable' in stocks_response[i] for i in range(0, len(stocks_response)))

            @patch('routes.recommendations.feature_queries.is_active', return_value=False)
            @clean_database
            def when_user_has_bookings_on_recommended_offers(self, mock_geolocation_feature, app):
                # given
                user = create_user(can_book_free_offers=True, departement_code='93', is_admin=False)
                offerer = create_offerer()
                venue = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
                offer = create_offer_with_thing_product(venue, thing_name='thing 93', url=None, is_national=False)
                stock = create_stock_from_offer(offer, price=0)
                booking = create_booking(user=user, stock=stock, venue=venue)
                create_mediation(offer)
                repository.save(booking)
                discovery_view_queries.refresh(concurrently=False)

                # when
                response = TestClient(app.test_client()).with_auth(user.email) \
                    .put(RECOMMENDATION_URL, json={})

                # then
                assert response.status_code == 200
                assert response.json == []

        class WhenGeolocationFeatureIsActivated:
            @patch('routes.recommendations.feature_queries.is_active', return_value=True)
            @patch('routes.recommendations.create_recommendations_for_discovery_v3')
            @patch('routes.recommendations.create_recommendations_for_discovery')
            @patch('routes.recommendations.current_user')
            @patch('routes.recommendations.serialize_recommendations')
            @patch('routes.recommendations.update_read_recommendations')
            @clean_database
            def when_user_is_geolocated(self, mock_update_read_recommendations,
                                                              mock_serialize_recommendations,
                                                              mock_current_user,
                                                              mock_create_recommendations_for_discovery,
                                                              mock_create_recommendations_for_discovery_v3,
                                                              mock_geolocation_feature,
                                                              app):
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

                repository.save(user, stock, mediation, iris_venue)
                discovery_view_v3_queries.refresh(concurrently=False)

                reads = [
                    {"id": humanize(1), "dateRead": "2018-12-17T15:59:11.689000Z"},
                    {"id": humanize(2), "dateRead": "2018-12-17T15:59:15.689000Z"},
                    {"id": humanize(3), "dateRead": "2018-12-17T15:59:21.689000Z"},
                ]
                data = {'readRecommendations': reads}
                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # When
                response = auth_request.put(f'{RECOMMENDATION_URL}?longitude={user_longitude}&latitude={user_latitude}',
                                            json=data, headers={'origin': 'http://localhost:3000'})

                # Then
                assert response.status_code == 200
                mock_update_read_recommendations.assert_called_once()
                mock_create_recommendations_for_discovery.assert_not_called()
                mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                     user_iris_id=iris.id,
                                                                                     user_is_geolocated=True,
                                                                                     sent_offers_ids=[],
                                                                                     limit=30)

            @patch('routes.recommendations.feature_queries.is_active', return_value=True)
            @patch('routes.recommendations.create_recommendations_for_discovery_v3')
            @patch('routes.recommendations.current_user')
            @patch('routes.recommendations.serialize_recommendations')
            @clean_database
            def when_user_is_not_located(self, mock_serialize_recommendations,
                                                               mock_current_user,
                                                               mock_create_recommendations_for_discovery_v3,
                                                               mock_geolocation_feature,
                                                               app):
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
                response = auth_request.put(RECOMMENDATION_URL,
                                            json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                     user_iris_id=None,
                                                                                     user_is_geolocated=False,
                                                                                     sent_offers_ids=[],
                                                                                     limit=30)

            @patch('routes.recommendations.feature_queries.is_active', return_value=True)
            @patch('routes.recommendations.create_recommendations_for_discovery_v3')
            @patch('routes.recommendations.current_user')
            @patch('routes.recommendations.serialize_recommendations')
            @clean_database
            def when_user_is_located_outside_known_iris(self, mock_serialize_recommendations,
                                                                              mock_current_user,
                                                                              mock_create_recommendations_for_discovery_v3,
                                                                              mock_geolocation_feature,
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

                repository.save(user, stock, stock_of_digital_offer, mediation, mediation_of_digital_offer)
                discovery_view_v3_queries.refresh(concurrently=False)

                auth_request = TestClient(app.test_client()).with_auth(user.email)

                # when
                response = auth_request.put(f'{RECOMMENDATION_URL}?longitude={user_longitude}&latitude={user_latitude}',
                                            json={'offersSentInLastCall': []})

                # then
                assert response.status_code == 200
                mock_create_recommendations_for_discovery_v3.assert_called_once_with(user=mock_current_user,
                                                                                     user_iris_id=None,
                                                                                     user_is_geolocated=True,
                                                                                     sent_offers_ids=[],
                                                                                     limit=30)
