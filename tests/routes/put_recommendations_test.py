from datetime import datetime, timedelta
from unittest.mock import patch

from models import PcObject
from models.mediation import Mediation
from models.recommendation import Recommendation
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_event_occurrence, \
    create_offer_with_event_product, \
    create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_event_occurrence, \
    create_stock_from_offer, \
    create_offer_with_thing_product, \
    create_user, \
    create_venue, \
    create_stock_with_thing_offer, create_booking
from utils.human_ids import humanize
from utils.tutorials import upsert_tuto_mediations

RECOMMENDATION_URL = '/recommendations'


class Put:
    class Returns401:
        def when_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).put(
                RECOMMENDATION_URL,
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401

    class Returns404:
        @clean_database
        def when_given_mediation_does_not_match_given_offer(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing_1 = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            offer_thing_2 = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing_1 = create_stock_with_thing_offer(offerer, venue, offer_thing_1, price=0)
            stock_thing_2 = create_stock_with_thing_offer(offerer, venue, offer_thing_2, price=0)
            mediation_1 = create_mediation(offer_thing_1)
            mediation_2 = create_mediation(offer_thing_2)
            PcObject.save(user, stock_thing_1, stock_thing_2, mediation_1, mediation_2)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing_1.id) +
                                        "?mediationId=" + humanize(mediation_2.id),
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_known(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_with_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_with_thing = create_stock_with_thing_offer(offerer, venue, offer_with_thing, price=0)
            mediation = create_mediation(offer_with_thing)
            PcObject.save(user, stock_with_thing, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=ABCDE" +
                                        "&mediationId=" + humanize(mediation.id) +
                                        "&page=1" +
                                        "&seed=0.5",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_mediation_is_unknown(self, app):
            # given
            user = create_user(email='user1@user.fr')
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?mediationId=ABCDE" +
                                        "&page=1" +
                                        "&seed=0.5",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_known_and_mediation_is_unknown(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.save(user, stock_thing, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing.id) +
                                        "&mediationId=ABCDE" +
                                        '&page=1' +
                                        '&seed=0.5',
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_unknown(self, app):
            # given
            user = create_user(email='user1@user.fr')
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=ABCDE" +
                                        "&mediationId=ABCDE" +
                                        '&page=1' +
                                        '&seed=0.5',
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_venue_of_given_offer_is_not_validated(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            offer1 = create_offer_with_thing_product(venue, thumb_count=1)
            stock1 = create_stock_from_offer(offer1, price=0)
            PcObject.save(user, stock1)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            data = {'seenRecommendationIds': []}
            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        '?offerId=%s' % humanize(offer1.id) +
                                        '&page=1' +
                                        '&seed=0.5',
                                        json=data)

            # then
            assert response.status_code == 404

    class Returns200:
        @clean_database
        def when_read_recommendations_are_given(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user = create_user(email='test@email.com')
            event_occurrence1 = create_event_occurrence(offer)
            event_occurrence2 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1, soft_deleted=True)
            stock2 = create_stock_from_event_occurrence(event_occurrence2, soft_deleted=False)
            thing_offer1 = create_offer_with_thing_product(venue)
            thing_offer2 = create_offer_with_thing_product(venue)
            stock3 = create_stock_from_offer(thing_offer1, soft_deleted=True)
            stock4 = create_stock_from_offer(thing_offer2, soft_deleted=False)
            recommendation1 = create_recommendation(offer, user)
            recommendation2 = create_recommendation(thing_offer1, user)
            recommendation3 = create_recommendation(thing_offer2, user)
            PcObject.save(
                stock1, stock2, stock3, stock4,
                recommendation1, recommendation2, recommendation3
            )

            read_recommendation_data = [
                {
                    "dateRead": "2018-12-17T15:59:11.689000Z",
                    "id": humanize(recommendation1.id)
                },
                {
                    "dateRead": "2018-12-17T15:59:14.689000Z",
                    "id": humanize(recommendation2.id)
                }
            ]

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .put('{}/read'.format(RECOMMENDATION_URL), json=read_recommendation_data)

            # Then
            read_recommendation_date_reads = [r['dateRead'] for r in response.json]
            assert len(read_recommendation_date_reads) == 2
            assert {"2018-12-17T15:59:11.689000Z", "2018-12-17T15:59:14.689000Z"} == set(read_recommendation_date_reads)

        @clean_database
        def when_updating_read_recommendations(self, app):
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
            PcObject.save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            reads = [
                {"id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1" +
                                        "&seed=0.5",
                                        json=data)

            # then
            assert response.status_code == 200

            assert any(reco.dateRead is not None for reco in Recommendation.query.all())

        @clean_database
        def when_user_has_no_offer_in_his_department(self, app):
            # given
            user = create_user(departement_code='973', can_book_free_offers=True, is_admin=False)
            offerer = create_offerer()
            venue29 = create_venue(offerer, siret=offerer.siren + '98765', postal_code='29000', departement_code='29')
            venue34 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
            venue93 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            venue67 = create_venue(offerer, siret=offerer.siren + '56789', postal_code='67000', departement_code='67')
            thing_offer1 = create_offer_with_thing_product(venue93, thing_name='thing 93', url=None, is_national=False)
            thing_offer2 = create_offer_with_thing_product(venue67, thing_name='thing 67', url=None, is_national=False)
            thing_offer3 = create_offer_with_thing_product(venue29, thing_name='thing 29', url=None, is_national=False)
            thing_offer4 = create_offer_with_thing_product(venue34, thing_name='thing 34', url=None, is_national=False)
            stock1 = create_stock_from_offer(thing_offer1)
            stock2 = create_stock_from_offer(thing_offer2)
            stock3 = create_stock_from_offer(thing_offer3)
            stock4 = create_stock_from_offer(thing_offer4)
            PcObject.save(user, stock1, stock2, stock3, stock4)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1" +
                     "&seed=0.5",
                     json={'readRecommendations': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_user_has_one_offer_in_his_department(self, app):
            # given
            user = create_user(departement_code='93', can_book_free_offers=True, is_admin=False)
            offerer = create_offerer()
            venue93 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            venue67 = create_venue(offerer, siret=offerer.siren + '56789', postal_code='67000', departement_code='67')
            thing_offer1 = create_offer_with_thing_product(venue93, thing_name='thing 93', url=None, is_national=False)
            thing_offer2 = create_offer_with_thing_product(venue67, thing_name='thing 67', url=None, is_national=False)
            stock1 = create_stock_from_offer(thing_offer1)
            stock2 = create_stock_from_offer(thing_offer2)
            create_mediation(thing_offer1)
            create_mediation(thing_offer2)
            PcObject.save(user, stock1, stock2)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1"
                     "&seed=0.5", json={'readRecommendations': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 1
            recommendation_response = response.json[0]
            assert 'offer' in recommendation_response
            assert 'venue' in recommendation_response['offer']
            assert 'validationToken' not in recommendation_response['offer']['venue']
            assert 'managingOfferer' in recommendation_response['offer']['venue']
            assert 'validationToken' not in recommendation_response['offer']['venue']['managingOfferer']

        @clean_database
        def when_offers_have_soft_deleted_stocks(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            event_offer = create_offer_with_event_product(venue)
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            event_occurrence1 = create_event_occurrence(event_offer,
                                                        beginning_datetime=four_days_from_now,
                                                        end_datetime=eight_days_from_now)
            event_occurrence2 = create_event_occurrence(event_offer,
                                                        beginning_datetime=four_days_from_now,
                                                        end_datetime=eight_days_from_now)
            soft_deleted_event_stock = create_stock_from_event_occurrence(event_occurrence1,
                                                                          soft_deleted=True)
            event_stock = create_stock_from_event_occurrence(event_occurrence2,
                                                             soft_deleted=False)
            thing_offer1 = create_offer_with_thing_product(venue)
            thing_offer2 = create_offer_with_thing_product(venue)
            soft_deleted_thing_stock = create_stock_from_offer(thing_offer1, soft_deleted=True)
            thing_stock = create_stock_from_offer(thing_offer2, soft_deleted=False)
            create_mediation(thing_offer1)
            create_mediation(thing_offer2)
            create_mediation(event_offer)
            PcObject.save(user, event_stock, soft_deleted_event_stock, thing_stock, soft_deleted_thing_stock)
            event_offer_id = event_offer.id
            thing_offer2_id = thing_offer2.id

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1"
                     "&seed=0.5", json={})

            # Then
            recommendations = response.json
            assert len(recommendations) == 2
            offer_ids = [r['offerId'] for r in recommendations]
            assert humanize(event_offer_id) in offer_ids
            assert humanize(thing_offer2_id) in offer_ids

        @clean_database
        def when_offers_have_no_stocks(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            PcObject.save(user, offer)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_offers_have_a_thumb_count_for_thing_and_no_mediation(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thumb_count=1)
            stock = create_stock_from_offer(offer, price=0)
            PcObject.save(user, stock)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_offers_have_no_thumb_count_for_thing_and_no_mediation(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            stock = create_stock_from_offer(offer, price=0)
            PcObject.save(user, stock)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_offers_have_no_thumb_count_for_thing_and_a_mediation(
                self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            stock = create_stock_from_offer(offer, price=0)
            mediation = create_mediation(offer)
            PcObject.save(user, stock, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 1

        @clean_database
        def when_offers_have_no_thumb_count_for_event_and_no_mediation(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)

            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(
                offer,
                beginning_datetime=four_days_from_now,
                end_datetime=eight_days_from_now
            )
            stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
            PcObject.save(user, stock)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_offers_have_no_thumb_count_for_event_and_no_mediation(
                self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)

            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(
                offer,
                beginning_datetime=four_days_from_now,
                end_datetime=eight_days_from_now
            )
            mediation = create_mediation(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
            PcObject.save(user, stock, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 1

        @clean_database
        def when_offers_have_a_thumb_count_for_event_and_no_mediation(
                self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)

            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, thumb_count=1, dominant_color=b'123')
            event_occurrence = create_event_occurrence(
                offer,
                beginning_datetime=four_days_from_now,
                end_datetime=eight_days_from_now
            )
            stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
            PcObject.save(user, stock)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_offers_have_non_validated_venues(self, app):
            # Given
            offerer = create_offerer()
            venue_not_validated = create_venue(offerer, siret=None, comment='random reason')
            venue_not_validated.generate_validation_token()
            venue_validated = create_venue(offerer, siret=None, comment='random reason')
            offer_venue_not_validated = create_offer_with_thing_product(venue_not_validated, thumb_count=1)
            offer_venue_validated = create_offer_with_thing_product(venue_validated, thumb_count=1)
            stock_venue_not_validated = create_stock_from_offer(offer_venue_not_validated)
            stock_venue_validated = create_stock_from_offer(offer_venue_validated)
            user = create_user(email='test@email.com')
            create_mediation(offer_venue_not_validated)
            create_mediation(offer_venue_validated)
            PcObject.save(stock_venue_not_validated, stock_venue_validated, user)
            venue_validated_id = venue_validated.id
            venue_not_validated_id = venue_not_validated.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # Then
            assert response.status_code == 200
            recommendations = response.json
            venue_ids = set(map(lambda x: x['offer']['venue']['id'], recommendations))
            assert humanize(venue_validated_id) in venue_ids
            assert humanize(venue_not_validated_id) not in venue_ids

        @clean_database
        def when_offers_have_active_mediations(self, app):
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
            PcObject.save(user, stock1, mediation1, stock2, mediation2, mediation3)
            auth_request = TestClient(app.test_client()).with_auth(user.email)
            mediation3_id = mediation3.id
            mediation2_id = mediation2.id
            mediation1_id = mediation1.id

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            json = response.json
            mediation_ids = list(map(lambda x: x['mediationId'], json))
            assert humanize(mediation3_id) in mediation_ids
            assert humanize(mediation2_id) not in mediation_ids
            assert humanize(mediation1_id) not in mediation_ids

        @clean_database
        def when_a_recommendation_is_requested(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
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
            PcObject.save(user, stock1, stock2, stock3, stock4)
            offer1_id = offer1.id
            offer2_id = offer2.id
            offer3_id = offer3.id
            offer4_id = offer4.id

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer1.id) +
                                        "&page=1" +
                                        "&seed=0.5",
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
        def test_returns_two_recommendations_with_one_event_and_one_thing(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_event = create_offer_with_event_product(venue)
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
            PcObject.save(user, event_stock, stock_thing)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1"
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json) == 2

        @clean_database
        def test_discovery_recommendations_should_not_include_search_recommendations(self, app):
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

            PcObject.save(user, stock1, mediation1, stock2, mediation2, recommendation)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            recommendations_req = auth_request.put(RECOMMENDATION_URL +
                                                   "?page=1"
                                                   "&seed=0.5", json={})

            # Then
            assert recommendations_req.status_code == 200
            recommendations = recommendations_req.json
            assert len(recommendations) == 1
            assert recommendations[0]['search'] is None

        @clean_database
        def when_a_recommendation_with_an_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.save(user, stock_thing, mediation)
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing.id) +
                                        "&mediationId=" + humanize(mediation.id) +
                                        "&page=1" +
                                        "&seed=0.5", json={'seenRecommendationIds': []})
            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['mediationId'] == humanize(mediation.id)

        @clean_database
        def when_a_recommendation_with_an_offer_and_no_mediation_is_requested(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.save(user, stock_thing, mediation)
            mediation_id = mediation.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" + humanize(offer_thing.id) +
                                        "&page=1" +
                                        "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['mediationId'] == humanize(mediation_id)

        @clean_database
        def when_a_recommendation_with_no_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.save(user, stock_thing, mediation)
            offer_thing_id = offer_thing.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?mediationId=" + humanize(mediation.id) +
                                        "&page=1" +
                                        "&seed=0.5",
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json
            assert recos[0]['offerId'] == humanize(offer_thing_id)

        @clean_database
        def test_returns_new_recommendation_with_active_mediation_for_already_existing_but_invalid_recommendations(
                self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, thumb_count=0)
            stock1 = create_stock_from_offer(offer1, price=0)
            inactive_mediation = create_mediation(offer1, is_active=False)
            active_mediation = create_mediation(offer1, is_active=True)
            invalid_recommendation = create_recommendation(offer1, user, inactive_mediation,
                                                           valid_until_date=datetime.utcnow() - timedelta(hours=2))
            PcObject.save(user, stock1, inactive_mediation, active_mediation, invalid_recommendation)
            active_mediation_id = active_mediation.id
            inactive_mediation_id = inactive_mediation.id
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            data = {'seenRecommendationIds': []}

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1" +
                                        "&seed=0.5", json=data)

            # then
            assert response.status_code == 200
            json = response.json
            mediation_ids = list(map(lambda x: x['mediationId'], json))
            assert humanize(active_mediation_id) in mediation_ids
            assert humanize(inactive_mediation_id) not in mediation_ids

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
            PcObject.save(stock1, stock2, stock3, stock4, user)
            upsert_tuto_mediations()

            # when
            auth_request = TestClient(app.test_client()).with_auth(user.email)
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1" +
                                        "&seed=0.5", json={})

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
            PcObject.save(stock1, stock2, stock3, stock4, user)
            upsert_tuto_mediations()
            tuto_mediation0 = Mediation.query.filter_by(tutoIndex=0).one()
            tuto_mediation1 = Mediation.query.filter_by(tutoIndex=1).one()
            tuto_recommendation0 = create_recommendation(user=user, mediation=tuto_mediation0)
            tuto_recommendation1 = create_recommendation(user=user, mediation=tuto_mediation1)
            PcObject.save(tuto_recommendation0, tuto_recommendation1)
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
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?page=1" +
                                        "&seed=0.5", json=data)

            # then
            assert response.status_code == 200
            recommendations = response.json
            recommendation_ids = [r['id'] for r in recommendations]
            assert humanized_tuto_recommendation0_id not in recommendation_ids
            assert humanized_tuto_recommendation1_id not in recommendation_ids

        @clean_database
        def when_stock_has_past_booking_limit_date(self, app):
            # Given
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            user = create_user()
            stock = create_stock_from_offer(offer, booking_limit_datetime=one_day_ago)
            recommendation = create_recommendation(offer, user, date_read=three_days_ago)

            PcObject.save(stock, recommendation)

            # When
            recommendations = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1" +
                     "&seed=0.5",
                     json={})

            # Then
            assert recommendations.status_code == 200
            assert not recommendations.json

        @clean_database
        def when_user_has_already_seen_recommendation(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue)
            mediation = create_mediation(offer, is_active=True)
            stock = create_stock_from_offer(offer)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1" +
                     "&seed=0.5", json={'seenRecommendationIds': [humanize(recommendation.id)]})

            # then
            assert response.status_code == 200
            assert response.json == []

        @clean_database
        def test_returns_same_quantity_of_recommendations_in_different_orders(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.save(user)

            for i in range(0, 10):
                offer_event = create_offer_with_event_product(venue, thumb_count=1, dominant_color=b'123')
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
                PcObject.save(event_stock, stock_thing)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            recommendations1 = auth_request.put(RECOMMENDATION_URL +
                                                "?page=1" +
                                                "&seed=0.5", json={'seenRecommendationIds': []})
            recommendations2 = auth_request.put(RECOMMENDATION_URL +
                                                "?page=1" +
                                                "&seed=0.5", json={'seenRecommendationIds': []})

            # then
            assert recommendations1.status_code == 200
            assert recommendations2.status_code == 200
            assert len(recommendations1.json) == 20
            assert len(recommendations1.json) == len(recommendations2.json)
            assert any(
                [recommendations1.json[i]['id'] != recommendations2.json[i]['id'] for i in
                 range(0, len(recommendations1.json))])

        @clean_database
        def test_returns_stocks_with_isBookable_property(self, app):
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
            PcObject.save(user, recommendation)

            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            recommendations_req = auth_request.put(RECOMMENDATION_URL +
                                                   "?page=1" +
                                                   "&seed=0.5", json={})

            # Then
            assert recommendations_req.status_code == 200
            recommendations = recommendations_req.json
            assert len(recommendations) == 1
            recommendation = recommendations[0]
            assert recommendation['offer']['name'] == 'Guitar for dummies'
            stocks_response = recommendation['offer']['stocks']
            assert len(stocks_response) == 2
            assert all('isBookable' in stocks_response[i] for i in range(0, len(stocks_response)))

        @clean_database
        def when_user_has_bookings_on_recommended_offers(self, app):
            # given
            user = create_user(departement_code='93', can_book_free_offers=True, is_admin=False)
            offerer = create_offerer()
            venue = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            offer = create_offer_with_thing_product(venue, thing_name='thing 93', url=None, is_national=False)
            stock = create_stock_from_offer(offer, price=0)
            booking = create_booking(user, stock, venue)
            create_mediation(offer)
            PcObject.save(booking)
            booking_id = booking.id

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1" +
                     "&seed=0.5", json={'readRecommendations': []})

            # then
            assert response.status_code == 200
            assert response.json == []

        @clean_database
        @patch('routes.recommendations.create_recommendations_for_discovery')
        def test_should_create_recommendations_using_pagination_params(self, create_recommendations_for_discovery, app):
            # given
            user = create_user(departement_code='93', can_book_free_offers=True, is_admin=False)
            offerer = create_offerer()
            venue = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            offer = create_offer_with_thing_product(venue, thing_name='thing 93', url=None, is_national=False)
            stock = create_stock_from_offer(offer, price=0)
            booking = create_booking(user, stock, venue)
            create_mediation(offer)
            PcObject.save(booking)

            # when
            TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL +
                     "?page=1" +
                     "&seed=0.5", json={'readRecommendations': []})

            # then
            args = create_recommendations_for_discovery.call_args
            assert args[1]['limit'] == 30
            assert args[1]['pagination_params'] == {'page': 1, 'seed': 0.5}

        @clean_database
        @patch('routes.recommendations.create_recommendations_for_discovery')
        @patch('routes.recommendations.random.random', return_value=0.5)
        def test_should_create_recommendations_using_default_pagination_params_when_not_provided(self,
                                                                                                 mock_random,
                                                                                                 create_recommendations_for_discovery,
                                                                                                 app):
            # given
            user = create_user(departement_code='93', can_book_free_offers=True, is_admin=False)
            offerer = create_offerer()
            venue = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            offer = create_offer_with_thing_product(venue, thing_name='thing 93', url=None, is_national=False)
            stock = create_stock_from_offer(offer, price=0)
            booking = create_booking(user, stock, venue)
            create_mediation(offer)
            PcObject.save(booking)

            # when
            TestClient(app.test_client()).with_auth(user.email) \
                .put(RECOMMENDATION_URL, json={'readRecommendations': []})

            # then
            args = create_recommendations_for_discovery.call_args
            print(args[1])
            assert args[1]['limit'] == 30
            assert args[1]['pagination_params'] == {'page': 1, 'seed': 0.5}
