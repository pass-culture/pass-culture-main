""" tests routes mediations """
from datetime import datetime, timedelta
from os import path
from pathlib import Path

import pytest

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_user, \
    create_offer_with_event_product, \
    create_mediation, \
    create_offerer, \
    create_user_offerer, \
    create_venue, create_recommendation
from utils.human_ids import humanize


@clean_database
@pytest.mark.standalone
def test_create_mediation_with_thumb_url(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user, offerer)

    PcObject.save(offer)
    PcObject.save(user, venue, offerer, user_offerer)

    auth_request = TestClient().with_auth(email=user.email)

    data = {
        'offerId': humanize(offer.id),
        'offererId': humanize(offerer.id),
        'thumbUrl': 'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    }

    # when
    response = auth_request.post(API_URL + '/mediations', json=data)

    # then
    assert response.status_code == 201


@clean_database
@pytest.mark.standalone
def test_create_mediation_with_thumb_url_returns_400_if_url_is_not_an_image(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user, offerer)
    PcObject.save(user, venue, user_offerer)

    auth_request = TestClient().with_auth(email=user.email)

    data = {
        'offerId': humanize(offer.id),
        'offererId': humanize(offerer.id),
        'thumbUrl': 'https://beta.gouv.fr/'
    }

    # when
    response = auth_request.post(API_URL + '/mediations', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['thumbUrl'] == ["L'adresse saisie n'est pas valide"]


@clean_database
@pytest.mark.standalone
def test_create_mediation_with_thumb_file(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user, offerer)

    PcObject.save(offer)
    PcObject.save(user, venue, offerer, user_offerer)

    auth_request = TestClient().with_auth(email=user.email)

    with open(Path(path.dirname(path.realpath(__file__))) / '..' / '..'
              / 'sandboxes' / 'thumbs' / 'mediations' / 'FranckLepage', 'rb') as thumb_file:
        data = {
            'offerId': humanize(offer.id),
            'offererId': humanize(offerer.id)
        }
        # WE NEED TO GIVE AN EXTENSION TO THE FILE
        # IF WE WANT TO MAKE THE TEST PASS
        files = {'thumb': ('FranckLepage.jpg', thumb_file)}

        # when
        response = auth_request.post(API_URL + '/mediations', json=data, files=files)

    # then
    assert response.status_code == 201


@pytest.mark.standalone
@clean_database
def test_patch_mediation_returns_200(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user, offerer)
    mediation = create_mediation(offer)
    PcObject.save(mediation)
    PcObject.save(user, venue, offerer, user_offerer)

    auth_request = TestClient().with_auth(email=user.email)
    data = {'frontText': 'new front text', 'backText': 'new back text', 'isActive': False}

    # when
    response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation.id), json=data)

    # then
    db.session.refresh(mediation)
    assert response.status_code == 200
    assert response.json()['id'] == humanize(mediation.id)
    assert response.json()['frontText'] == mediation.frontText
    assert response.json()['backText'] == mediation.backText
    assert response.json()['isActive'] == mediation.isActive
    assert response.json()['thumbUrl'] == mediation.thumbUrl
    assert mediation.isActive == data['isActive']
    assert mediation.frontText == data['frontText']
    assert mediation.backText == data['backText']


@clean_database
@pytest.mark.standalone
def test_patch_mediation_returns_403_if_user_is_not_attached_to_offerer_of_mediation(app):
    # given
    current_user = create_user(email='bobby@test.com')
    other_user = create_user(email='jimmy@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(other_user, offerer)
    mediation = create_mediation(offer)
    PcObject.save(mediation)
    PcObject.save(other_user, current_user, venue, offerer, user_offerer)

    auth_request = TestClient().with_auth(email=current_user.email)

    # when
    response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation.id), json={})

    # then
    assert response.status_code == 403


@clean_database
@pytest.mark.standalone
def test_patch_mediation_returns_404_if_mediation_does_not_exist(app):
    # given
    user = create_user()
    PcObject.save(user)
    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.patch(API_URL + '/mediations/ADFGA', json={})

    # then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_get_mediation_returns_200_and_the_mediation_as_json(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user, offerer)
    mediation = create_mediation(offer)
    PcObject.save(mediation)
    PcObject.save(offer)
    PcObject.save(user, venue, offerer, user_offerer)

    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.get(API_URL + '/mediations/%s' % humanize(mediation.id))

    # then
    assert response.status_code == 200
    assert response.json()['id'] == humanize(mediation.id)
    assert response.json()['frontText'] == mediation.frontText
    assert response.json()['backText'] == mediation.backText


@clean_database
@pytest.mark.standalone
def test_get_mediation_returns_404_if_mediation_does_not_exist(app):
    # given
    user = create_user()
    PcObject.save(user)
    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.get(API_URL + '/mediations/AE')

    # then
    assert response.status_code == 404


@pytest.mark.standalone
@clean_database
def test_patch_mediation_make_mediations_invalid_for_all_users_when_deactivating_mediation(app):
    # given
    user_pro = create_user()
    other_user = create_user(email='other@email.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    user_offerer = create_user_offerer(user_pro, offerer)
    mediation1 = create_mediation(offer)
    mediation2 = create_mediation(offer)
    original_validity_date = datetime.utcnow() + timedelta(days=7)
    recommendation1 = create_recommendation(offer, user_pro, mediation1, valid_until_date=original_validity_date)
    recommendation2 = create_recommendation(offer, other_user, mediation1, valid_until_date=original_validity_date)
    other_recommendation = create_recommendation(offer, other_user, mediation2, valid_until_date=original_validity_date)
    PcObject.save(other_user, user_offerer, recommendation1, recommendation2, other_recommendation)

    auth_request = TestClient().with_auth(email=user_pro.email)
    data = {'isActive': False}

    # when
    response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation1.id), json=data)

    # then
    db.session.refresh(mediation1)
    assert response.status_code == 200
    assert response.json()['isActive'] == mediation1.isActive
    assert mediation1.isActive == data['isActive']
    db.session.refresh(recommendation1)
    db.session.refresh(recommendation2)
    db.session.refresh(other_recommendation)
    assert recommendation1.validUntilDate < datetime.utcnow()
    assert recommendation2.validUntilDate < datetime.utcnow()
    assert other_recommendation.validUntilDate == original_validity_date
