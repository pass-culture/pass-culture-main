import secrets

from datetime import datetime, timedelta
import pytest

from models import PcObject, Venue
from models.db import db
from tests.conftest import clean_database
from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, req_with_auth, create_user, create_venue, \
    create_offerer, create_user_offerer, create_n_mixed_offers_with_same_venue, create_thing, create_event, \
    create_thing_offer, create_event_offer, create_recommendation


def insert_offers_for(user, n, siren='123456789'):
    offerer = create_offerer(siren=siren)
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    offers = create_n_mixed_offers_with_same_venue(venue, n=n)

    PcObject.check_and_save(user_offerer)
    PcObject.check_and_save(*offers)


@clean_database
@pytest.mark.standalone
def test_get_offers_are_paginated_by_chunks_of_10(app):
    # Given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20)

    # when
    response = req_with_auth(email='user@test.com', password='azerty123').get(API_URL + '/offers')

    # then
    offers = response.json()
    assert response.status_code == 200
    assert len(offers) == 10


@clean_database
@pytest.mark.standalone
def test_get_offers_is_paginated_by_default_on_page_1(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20)
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    offers = auth_request.get(API_URL + '/offers').json()
    first_id = dehumanize(offers[0]['id'])

    # when
    response = auth_request.get(API_URL + '/offers?page=1')

    # then
    result = response.json()
    assert response.status_code == 200
    assert dehumanize(result[0]['id']) == first_id


@clean_database
@pytest.mark.standalone
def test_get_offers_returns_offers_sorted_by_id_desc(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20)
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    response_1 = auth_request.get(API_URL + '/offers?page=1')

    # when
    response_2 = auth_request.get(API_URL + '/offers?page=2')

    # then
    offers_1 = response_1.json()
    offers_2 = response_2.json()
    assert offers_1[-1]['dateCreated'] > offers_2[0]['dateCreated']


@clean_database
@pytest.mark.standalone
def test_get_offers_is_filtered_by_given_venue_id(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20, siren='123456789')
    insert_offers_for(user, 20, siren='987654321')
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    venue_id = Venue.query.first().id

    # when
    response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id))

    # then
    offers = response.json()
    assert response.status_code == 200
    for offer in offers:
        assert offer['venueId'] == humanize(venue_id)


@clean_database
@pytest.mark.standalone
def test_get_offers_can_be_filtered_and_paginated_at_the_same_time(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20, siren='987654321')
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    venue_id = Venue.query.first().id

    # when
    response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=2')

    # then
    offers = response.json()
    assert response.status_code == 200
    for offer in offers:
        assert offer['venueId'] == humanize(venue_id)


@clean_database
@pytest.mark.standalone
def test_get_offers_can_be_searched_and_filtered_and_paginated_at_the_same_time(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20, siren='987654321')
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    venue_id = Venue.query.first().id

    # when
    response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=1&search=Event')

    # then
    offers = response.json()
    assert response.status_code == 200
    assert len(offers) == 10
    for offer in offers:
        assert offer['venueId'] == humanize(venue_id)
        assert 'event' in offer['event']['name'].lower()


@clean_database
@pytest.mark.standalone
def test_get_offers_can_be_searched_using_multiple_search_terms(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    insert_offers_for(user, 20, siren='987654321')
    auth_request = req_with_auth(email='user@test.com', password='azerty123')
    venue_id = Venue.query.first().id

    # when
    response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=1&search=Event Offer')

    # then
    offers = response.json()
    assert response.status_code == 200
    assert len(offers) == 10
    assert len([o for o in offers if 'event' in o]) > 0
    assert len([o for o in offers if 'thing' in o]) > 0


@clean_database
@pytest.mark.standalone
def test_create_thing_offer(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    thing = create_thing()
    PcObject.check_and_save(user_offerer, venue, thing)

    data = {
        'venueId': humanize(venue.id),
        'thingId': humanize(thing.id)
    }
    auth_request = req_with_auth(email='user@test.com', password='azerty123')

    # when
    response = auth_request.post(API_URL + '/offers', json=data)

    # then
    assert response.status_code == 201


@clean_database
@pytest.mark.standalone
def test_create_thing_offer_returns_bad_request_if_thing_is_physical_and_venue_is_virtual(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer, is_virtual=True)
    thing = create_thing(url=None)
    PcObject.check_and_save(user_offerer, venue, thing)

    data = {
        'venueId': humanize(venue.id),
        'thingId': humanize(thing.id)
    }
    auth_request = req_with_auth(email='user@test.com', password='azerty123')

    # when
    response = auth_request.post(API_URL + '/offers', json=data)

    # then
    assert response.status_code == 400
    assert response.json() == {
        'global':
            ['Offer.venue is virtual but Offer.thing does not have an URL']
    }


@clean_database
@pytest.mark.standalone
def test_create_event_offer(app):
    # given
    user = create_user(email='user@test.com', password='azerty123')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    event = create_event()
    PcObject.check_and_save(user_offerer, venue, event)

    data = {
        'venueId': humanize(venue.id),
        'eventId': humanize(event.id)
    }
    auth_request = req_with_auth(email='user@test.com', password='azerty123')

    # when
    response = auth_request.post(API_URL + '/offers', json=data)

    # then
    assert response.status_code == 201


@clean_database
@pytest.mark.standalone
def test_get_offers_doesnt_show_anything_to_user_offerer_when_not_validated(app):
    # Given
    user = create_user(password='azerty123')
    offerer = create_offerer()
    venue = create_venue(offerer)
    user_offerer = create_user_offerer(user, offerer, validation_token=secrets.token_urlsafe(20))
    offer = create_thing_offer(venue)
    PcObject.check_and_save(user_offerer, offer)
    auth_request = req_with_auth(email=user.email, password='azerty123')
    # When
    response = auth_request.get(API_URL + '/offers')

    # Then
    assert response.json() == []


@pytest.mark.standalone
@clean_database
def test_patch_offer_returns_200_and_expires_recos(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user_offerer = create_user_offerer(user, offerer)
    recommendation = create_recommendation(offer, user, valid_until_date=datetime.utcnow() + timedelta(days=7))
    PcObject.check_and_save(offer)
    PcObject.check_and_save(user, venue, offerer, recommendation, user_offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    data = {'eventId': 'AE', 'isActive': False}

    # when
    response = auth_request.patch(API_URL + '/offers/%s' % humanize(offer.id), json=data)

    # then
    db.session.refresh(offer)
    assert response.status_code == 200
    assert response.json()['id'] == humanize(offer.id)
    assert response.json()['isActive'] == offer.isActive
    assert offer.isActive == data['isActive']
    # only isActive can be modified
    assert offer.eventId != data['eventId']
    assert response.json()['eventId'] != offer.eventId
    db.session.refresh(recommendation)
    assert recommendation.validUntilDate > datetime.now()


@clean_database
@pytest.mark.standalone
def test_patch_offer_returns_400_if_user_is_not_attached_to_offerer_of_offer(app):
    # given
    current_user = create_user(email='bobby@test.com', password='p@55sw0rd')
    other_user = create_user(email='jimmy@test.com', password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user_offerer = create_user_offerer(other_user, offerer)
    PcObject.check_and_save(offer)
    PcObject.check_and_save(other_user, current_user, venue, offerer, user_offerer)

    auth_request = req_with_auth(email=current_user.email, password='p@55sw0rd')

    # when
    response = auth_request.patch(API_URL + '/offers/%s' % humanize(offer.id), json={})

    # then
    assert response.status_code == 400


@clean_database
@pytest.mark.standalone
def test_patch_offer_returns_404_if_offer_does_not_exist(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.patch(API_URL + '/offers/ADFGA', json={})

    # then
    assert response.status_code == 404
