""" recommendations """
from collections import Counter
from datetime import datetime
from flask import current_app as app

import pytest
from dateutil.parser import parse as parse_date

from repository.clean_database import clean_all_database
from sandboxes.scripts.save_sandbox import save_sandbox
from tests.conftest import clean_database, TestClient
from utils.config import BLOB_SIZE
from tests.test_utils import API_URL, create_user

RECOMMENDATION_URL = API_URL + '/recommendations'

savedCounts = {}


class Put:
    class Returns200:
        def test_00_init(self, app):
            clean_all_database()
            save_sandbox("handmade", "true")

        def test_put_recommendations_returns_a_list_of_recos_starting_with_two_tutos(self, app):
            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            recos = response.json()
            assert recos[0]['mediation']['tutoIndex'] == 0
            assert recos[1]['mediation']['tutoIndex'] == 1
            recos_with_tutos = [
                reco for reco in recos
                if 'mediation' in reco and reco['mediation']['tutoIndex'] is not None
            ]
            assert len(list(recos_with_tutos)) == 2

        def test_put_recommendations_returns_no_duplicate_mediations_in_recos(self):
            # given
            user = create_user(email='test@email.com', password='testpsswd')

            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            recos = response.json()
            assert_no_duplicate_mediations(recos)

        def test_put_recommendations_returns_no_recos_with_mediations_with_stock_past_their_booking_limit(self):
            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            recos = response.json()
            assert_no_mediations_with_stock_past_their_booking_limit(recos)

        def test_put_recommendations_returns_recos_with_venues_in_93_if_event_is_not_national(self):
            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            recos = response.json()
            assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos)

        def test_put_recommendations_returns_at_least_one_reco_with_mediation_and_offer(self):
            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

            # then
            recos = response.json()
            assert len(list(filter(lambda reco: 'mediationId' in reco and 'offerId' in reco, recos))) > 0

        def test_put_recommendations_returns_no_tutos_once_they_are_marked_as_read(self):
            # given
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={})
            recos_before = response.json()
            assert recos_before[0]['mediation']['tutoIndex'] == 0
            assert recos_before[1]['mediation']['tutoIndex'] == 1
            payload = {'dateRead': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}

            # when
            response_patch = TestClient() \
                .with_auth() \
                .patch(API_URL + '/recommendations/' + recos_before[0]['id'], json=payload)

            # then
            assert response_patch.status_code == 200
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={})
            recos_after = response.json()
            assert recos_after[0]['mediation']['tutoIndex'] == 1
            assert 'mediation' not in recos_after[1] or recos_after[1]['mediation']['tutoIndex'] is None

        def test_put_recommendations_does_not_return_already_seen_recos(self):
            # given
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={})
            seen_recommendations_ids = list(map(lambda x: x['id'], response.json()[:20]))

            # when
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={'seenRecommendationIds': seen_recommendations_ids})

            # then
            recommended_ids = [reco['id'] for reco in (response.json())]
            intersection_between_seen_and_recommended = set(seen_recommendations_ids).intersection(set(recommended_ids))
            assert not intersection_between_seen_and_recommended


class Patch:
    class Returns200:
        def test_00_init(self, app):
            clean_all_database()
            save_sandbox("handmade", "true")

        def test_patch_recommendations_returns_is_clicked_true(self):
            # given
            response = TestClient() \
                .with_auth() \
                .put(RECOMMENDATION_URL, json={})
            reco_id = response.json()[0]['id']

            # when
            r_update = TestClient() \
                .with_auth() \
                .patch(API_URL + '/recommendations/' + reco_id, json={'isClicked': True})

            # then
            assert r_update.status_code == 200
            assert r_update.json()['isClicked']


def assert_no_duplicate_mediations(recos):
    mediation_ids = map(lambda recommendation: recommendation['mediationId'], recos)
    ids = list(filter(lambda mediation_id: mediation_id is not None, mediation_ids))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0


def assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos):
    recos_without_tutos = _remove_tutos(recos)
    for reco in recos_without_tutos:
        if not reco['offer']['eventOrThing']['isNational']:
            assert reco['offer']['venue']['departementCode'] == '93'


def _remove_tutos(recos):
    return [r for r in recos if 'mediation' not in r or 'tutoIndex' not in r['mediation']]


def assert_no_mediations_with_stock_past_their_booking_limit(recos):
    recos_without_tutos = _remove_tutos(recos)
    for reco in recos_without_tutos:
        assert not all([
            stock['bookingLimitDatetime'] is not None
            and parse_date(stock['bookingLimitDatetime']) <= datetime.utcnow()
            for stock in reco['offer']['stocks']]
        )


def subtest_recos_with_params(params,
                              expected_status=200,
                              expected_mediation_id=None,
                              expected_offer_id=None,
                              is_tuto=False):
    response = TestClient().with_auth().put(RECOMMENDATION_URL + '?' + params,
                                            json={})
    assert response.status_code == expected_status
    recos = response.json()
    assert len(recos) <= BLOB_SIZE + (2 if expected_mediation_id is None else 3)
    recos_for_tutos = filter(lambda reco: 'mediation' in reco and reco['mediation']['tutoIndex'] is not None, recos)
    assert len(list(recos_for_tutos)) == (1 if is_tuto else 0)

    if expected_mediation_id:
        assert recos[0]['mediationId'] == expected_mediation_id

    if expected_offer_id:
        assert recos[0]['offerId'] == expected_offer_id

    assert_no_mediations_with_stock_past_their_booking_limit(recos)
    assert_no_duplicate_mediations(recos)
    assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos)
    return recos
