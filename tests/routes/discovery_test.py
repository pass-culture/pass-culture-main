from datetime import datetime, timedelta

import pytest

from models import PcObject
from models.db import db
from models.mediation import Mediation, upsertTutoMediations
from tests.conftest import clean_database, TestClient
from utils.human_ids import humanize
from tests.test_utils import API_URL, \
    create_event_occurrence, \
    create_offer_with_event_product, \
    create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_event_occurrence, \
    create_stock_from_offer, \
    create_offer_with_thing_product, \
    create_user, \
    create_venue, \
    create_stock_with_thing_offer

RECOMMENDATION_URL = API_URL + '/recommendations'


@pytest.mark.standalone
class Put:
    class Returns401:
        def when_not_logged_in(self):
            # when
            response = TestClient().put(
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
            PcObject.check_and_save(user, stock_thing_1, stock_thing_2, mediation_1, mediation_2)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        humanize(offer_thing_1.id) +
                                        "?mediationId=" +
                                        humanize(mediation_2.id), json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_known(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.check_and_save(user, stock_thing, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        "ABCDE" +
                                        "?mediationId=" +
                                        humanize(mediation.id), json={'seenRecommendationIds': []})

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
            PcObject.check_and_save(user, stock_thing, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        humanize(offer_thing.id) +
                                        "?mediationId=" +
                                        "ABCDE", json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 404

        @clean_database
        def when_offer_is_unknown_and_mediation_is_unknown(self, app):
            # given
            user = create_user(email='user1@user.fr')
            PcObject.check_and_save(user)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        "ABCDE" +
                                        "?mediationId=" +
                                        "ABCDE", json={'seenRecommendationIds': []})

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
            PcObject.check_and_save(user, stock1)
            auth_request = TestClient().with_auth(user.email)

            data = {'seenRecommendationIds': []}
            # when
            response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id), json=data)

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
            PcObject.check_and_save(
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
            response = TestClient().with_auth('test@email.com') \
                .put('{}/read'.format(RECOMMENDATION_URL), json=read_recommendation_data)

            # Then
            read_recommendation_date_reads = [r['dateRead'] for r in response.json()]
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
            PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

            auth_request = TestClient().with_auth(user.email)

            reads = [
                {"id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            # when
            response = auth_request.put(RECOMMENDATION_URL, json=data)

            # then
            assert response.status_code == 200
            previous_date_reads = set([r['dateRead'] for r in reads])
            next_date_reads = set([r['dateRead'] for r in response.json()])
            assert previous_date_reads.issubset(next_date_reads)

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
            PcObject.check_and_save(user, stock1, stock2, stock3, stock4)

            # when
            response = TestClient().with_auth(user.email) \
                .put(RECOMMENDATION_URL, json={'readRecommendations': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 0

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
            PcObject.check_and_save(user, stock1, stock2)

            # when
            response = TestClient().with_auth(user.email) \
                .put(RECOMMENDATION_URL, json={'readRecommendations': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 1

        @clean_database
        def when_offers_have_soft_deleted_stocks(self, app):
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
            PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

            # When
            response = TestClient().with_auth('test@email.com').put(RECOMMENDATION_URL, json={})

            # Then
            recommendation_ids = [r['id'] for r in (response.json())]
            assert humanize(recommendation1.id) in recommendation_ids
            assert humanize(recommendation2.id) not in recommendation_ids
            assert humanize(recommendation3.id) in recommendation_ids

        @clean_database
        def when_offers_have_no_stocks(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            PcObject.check_and_save(user, offer)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 0

        @clean_database
        def when_offers_have_a_thumb_count_for_thing_and_no_mediation(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thumb_count=1)
            stock = create_stock_from_offer(offer, price=0)
            PcObject.check_and_save(user, stock)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 1

        @clean_database
        def when_offers_have_no_thumb_count_for_thing_and_no_mediation(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            stock = create_stock_from_offer(offer, price=0)
            PcObject.check_and_save(user, stock)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 0

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
            PcObject.check_and_save(user, stock, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 1

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
            PcObject.check_and_save(user, stock)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 0

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
            PcObject.check_and_save(user, stock, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 1

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
            PcObject.check_and_save(user, stock)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 1

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
            PcObject.check_and_save(stock_venue_not_validated, stock_venue_validated, user)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # Then
            assert response.status_code == 200
            recommendations = response.json()
            venue_ids = set(map(lambda x: x['offer']['venue']['id'], recommendations))
            assert humanize(venue_validated.id) in venue_ids
            assert humanize(venue_not_validated.id) not in venue_ids

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
            PcObject.check_and_save(user, stock1, mediation1, stock2, mediation2, mediation3)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            json = response.json()
            mediation_ids = list(map(lambda x: x['mediationId'], json))
            assert humanize(mediation3.id) in mediation_ids
            assert humanize(mediation2.id) not in mediation_ids
            assert humanize(mediation1.id) not in mediation_ids

        @clean_database
        def when_a_recommendation_is_requested(self, app):
            # given
            user = create_user(email='weird.bug@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, thumb_count=1)
            offer2 = create_offer_with_event_product(venue, thumb_count=1)
            offer3 = create_offer_with_thing_product(venue, thumb_count=1)
            offer4 = create_offer_with_thing_product(venue, thumb_count=1)
            now = datetime.utcnow()
            event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                                       end_datetime=now + timedelta(hours=74))
            mediation = create_mediation(offer2)
            stock1 = create_stock_from_offer(offer1, price=0)
            stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10, soft_deleted=False,
                                                        booking_limit_date=now + timedelta(days=3))
            stock3 = create_stock_from_offer(offer3, price=0)
            stock4 = create_stock_from_offer(offer4, price=0)
            recommendation_offer3 = create_recommendation(offer3, user)
            recommendation_offer4 = create_recommendation(offer4, user, date_read=now - timedelta(days=1))
            PcObject.check_and_save(user, stock1, stock2, stock3, stock4, mediation,
                                    recommendation_offer3, recommendation_offer4)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id),
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            response_json = response.json()
            assert len(response_json) == 4
            offer_ids = set(map(lambda x: x['offer']['id'], response_json))
            recommendation_ids = set(map(lambda x: x['id'], response_json))
            assert response_json[0]['offer']['id'] == humanize(offer1.id)
            assert humanize(offer1.id) in offer_ids
            assert humanize(offer2.id) in offer_ids
            assert humanize(offer3.id) in offer_ids
            assert humanize(recommendation_offer4.id) in recommendation_ids
            assert humanize(recommendation_offer3.id) in recommendation_ids

        @clean_database
        def when_existing_recommendations_are_invalid(self, app):
            # given
            now = datetime.utcnow()
            fifteen_min_ago = now - timedelta(minutes=15)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, thumb_count=1)
            offer2 = create_offer_with_event_product(venue, thumb_count=1)
            offer3 = create_offer_with_thing_product(venue, thumb_count=1)
            offer4 = create_offer_with_thing_product(venue, thumb_count=1)
            event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                                       end_datetime=now + timedelta(hours=74))
            mediation = create_mediation(offer2)
            stock1 = create_stock_from_offer(offer1, price=0)
            stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10, soft_deleted=False,
                                                        booking_limit_date=now + timedelta(days=3))
            stock3 = create_stock_from_offer(offer3, price=0)
            stock4 = create_stock_from_offer(offer4, price=0)
            recommendation_offer1 = create_recommendation(offer1, user, valid_until_date=fifteen_min_ago)
            recommendation_offer2 = create_recommendation(offer2, user, valid_until_date=fifteen_min_ago)
            recommendation_offer3 = create_recommendation(offer3, user, valid_until_date=fifteen_min_ago)
            recommendation_offer4 = create_recommendation(offer4, user, date_read=now - timedelta(days=1),
                                                          valid_until_date=fifteen_min_ago)
            PcObject.check_and_save(stock1, stock2, stock3, stock4, mediation, recommendation_offer3,
                                    recommendation_offer4, recommendation_offer1, recommendation_offer2)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id),
                                        json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            response_json = response.json()
            assert len(response_json) == 4
            recommendation_ids = set(map(lambda x: x['id'], response_json))
            assert humanize(recommendation_offer1.id) not in recommendation_ids
            assert humanize(recommendation_offer2.id) not in recommendation_ids
            assert humanize(recommendation_offer3.id) not in recommendation_ids
            assert humanize(recommendation_offer4.id) not in recommendation_ids

        @clean_database
        def test_returns_two_recommendations_with_one_event_and_one_thing(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_event = create_offer_with_event_product(venue, thumb_count=1, dominant_color=b'123')
            event_occurrence = create_event_occurrence(
                offer_event,
                beginning_datetime=four_days_from_now,
                end_datetime=eight_days_from_now
            )
            event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            PcObject.check_and_save(user, event_stock, stock_thing)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            assert len(response.json()) == 2

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

            PcObject.check_and_save(user, stock1, mediation1, stock2, mediation2, recommendation)
            db.session.refresh(offer2)
            db.session.refresh(recommendation)
            auth_request = TestClient().with_auth(user.email)

            # When
            recommendations_req = auth_request.put(RECOMMENDATION_URL, json={})

            # Then
            assert recommendations_req.status_code == 200
            recommendations = recommendations_req.json()
            assert len(recommendations) == 1
            assert recommendations[0]['id'] != recommendation.id
            assert recommendations[0]['offerId'] != offer2.id

        @clean_database
        def when_a_recommendation_with_an_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.check_and_save(user, stock_thing, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        humanize(offer_thing.id) +
                                        "&mediationId=" +
                                        humanize(mediation.id), json={'seenRecommendationIds': []})
            # then
            assert response.status_code == 200
            recos = response.json()
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
            PcObject.check_and_save(user, stock_thing, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?offerId=" +
                                        humanize(offer_thing.id), json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json()
            assert recos[0]['mediationId'] == humanize(mediation.id)

        @clean_database
        def when_a_recommendation_with_no_offer_and_a_mediation_is_requested(self, app):
            # given
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
            stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
            mediation = create_mediation(offer_thing)
            PcObject.check_and_save(user, stock_thing, mediation)
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL +
                                        "?mediationId=" +
                                        humanize(mediation.id), json={'seenRecommendationIds': []})

            # then
            assert response.status_code == 200
            recos = response.json()
            assert recos[0]['offerId'] == humanize(offer_thing.id)

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
            PcObject.check_and_save(user, stock1, inactive_mediation, active_mediation, invalid_recommendation)
            auth_request = TestClient().with_auth(user.email)

            data = {'seenRecommendationIds': []}
            # when
            response = auth_request.put(RECOMMENDATION_URL, json=data)

            # then
            assert response.status_code == 200
            json = response.json()
            mediation_ids = list(map(lambda x: x['mediationId'], json))
            assert humanize(active_mediation.id) in mediation_ids
            assert humanize(inactive_mediation.id) not in mediation_ids

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
            PcObject.check_and_save(stock1, stock2, stock3, stock4, user)
            upsertTutoMediations()

            # when
            auth_request = TestClient().with_auth(user.email)
            response = auth_request.put(RECOMMENDATION_URL, json={})

            # then
            assert response.status_code == 200
            recommendations = response.json()
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
            PcObject.check_and_save(stock1, stock2, stock3, stock4, user)
            upsertTutoMediations()
            tuto_mediation0 = Mediation.query.filter_by(tutoIndex=0).one()
            tuto_mediation1 = Mediation.query.filter_by(tutoIndex=1).one()
            tuto_recommendation0 = create_recommendation(
                mediation=tuto_mediation0,
                user=user
            )
            tuto_recommendation1 = create_recommendation(
                mediation=tuto_mediation1,
                user=user
            )
            PcObject.check_and_save(tuto_recommendation0, tuto_recommendation1)
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
            auth_request = TestClient().with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_URL, json=data)

            # then
            assert response.status_code == 200
            recommendations = response.json()
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

            PcObject.check_and_save(stock, recommendation)

            # When
            recommendations = TestClient().with_auth(user.email).put(RECOMMENDATION_URL,
                                                                     json={})

            # Then
            assert recommendations.status_code == 200
            assert not recommendations.json()

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
            PcObject.check_and_save(stock, recommendation)

            # when
            response = TestClient().with_auth(user.email)\
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': [humanize(recommendation.id)]})

            # then
            assert response.status_code == 200
            assert response.json() == []

        @clean_database
        def test_returns_same_quantity_of_recommendations_in_different_orders(self, app):
            # given
            now = datetime.utcnow()
            four_days_from_now = now + timedelta(days=4)
            eight_days_from_now = now + timedelta(days=8)
            user = create_user(email='user1@user.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user)

            for i in range(0, 10):
                offer_event = create_offer_with_event_product(venue, thumb_count=1, dominant_color=b'123')
                event_occurrence = create_event_occurrence(
                    offer_event,
                    beginning_datetime=four_days_from_now,
                    end_datetime=eight_days_from_now
                )
                event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
                offer_thing = create_offer_with_thing_product(venue, thumb_count=1, dominant_color=b'123')
                stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
                PcObject.check_and_save(event_stock, stock_thing)

            auth_request = TestClient().with_auth(user.email)

            # when
            recommendations1 = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})
            recommendations2 = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            assert recommendations1.status_code == 200
            assert recommendations2.status_code == 200
            assert len(recommendations1.json()) == 20
            assert len(recommendations1.json()) == len(recommendations2.json())
            assert any(
                [recommendations1.json()[i]['id'] != recommendations2.json()[i]['id'] for i in
                 range(0, len(recommendations1.json()))])
