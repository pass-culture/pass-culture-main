import pytest

from models import PcObject, Offer
from models.db import db
from tests.conftest import clean_database, TestClient
from utils.human_ids import humanize, dehumanize
from utils.test_utils import req_with_auth, create_user, API_URL, create_venue, create_offerer, create_thing, \
    create_thing_offer


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            thing = create_thing()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue, thing, booking_email='old@email.com')

            PcObject.check_and_save(offer, user)

            json = {'bookingEmail': 'offer@email.com'}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            offer = Offer.query.filter_by(id=offer.id).first()
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_updating_thing_attributes(self, app):
            # Given
            user = create_user()
            thing = create_thing()

            PcObject.check_and_save(thing, user)

            json = {'name': 'New name'}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(thing)
            assert thing.name == 'New name'

@clean_database
@pytest.mark.standalone
def test_things_with_urls_cannot_be_saved_with_type_offline_only(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    PcObject.check_and_save(user, venue)
    thing_json = {'thumbCount': 0, 'type': 'ThingType.JEUX_ABO', 'name': 'Le grand jeu',
                  'mediaUrls': 'http://media.url',
                  'url': 'http://jeux_abo.fr/offre', 'isNational': False, 'venueId': humanize(venue.id)}

    # When
    response = req_with_auth(email=user.email, password='P@55W0rd!').post(API_URL + '/things', json=thing_json)

    # Then
    assert response.status_code == 400
    assert response.json()['url'] == ['Une offre de type Jeux (Abonnements) ne peut pas être numérique']


@clean_database
@pytest.mark.standalone
def test_things_with_invalid_urls_cannot_be_saved(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    PcObject.check_and_save(user, venue)
    thing_json = {'thumbCount': 0, 'type': 'ThingType.JEUX_ABO', 'name': 'Le grand jeu',
                  'mediaUrls': 'http://media.url',
                  'url': 'ftp://invalid.url', 'isNational': False, 'venueId': humanize(venue.id)}

    # When
    response = req_with_auth(email=user.email, password='P@55W0rd!').post(API_URL + '/things', json=thing_json)

    # Then
    assert response.status_code == 400
    assert response.json()['url'] == ["L'URL doit commencer par \"http://\" ou \"https://\""]


@clean_database
@pytest.mark.standalone
def test_things_with_urls_must_have_virtual_venue(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=False)
    PcObject.check_and_save(user, venue)
    thing_json = {'thumbCount': 0, 'type': 'ThingType.JEUX_VIDEO', 'name': 'Les lapins crétins',
                  'mediaUrls': 'http://media.url',
                  'url': 'http://jeux.fr/offre', 'isNational': False, 'venueId': humanize(venue.id)}

    # When
    response = req_with_auth(email=user.email, password='P@55W0rd!').post(API_URL + '/things', json=thing_json)

    # Then
    assert response.status_code == 400
    assert response.json()['venue'] == [
        'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"']


@clean_database
@pytest.mark.standalone
def test_things_with_invalid_urls_cannot_be_modified(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    thing = create_thing()
    PcObject.check_and_save(user, venue, thing)
    thing_json = {'url': 'ftp://invalid.url'}
    auth_request = req_with_auth(email=user.email, password='P@55W0rd!')

    # When
    response = auth_request.patch(API_URL + '/things/%s' % humanize(thing.id), json=thing_json)

    # Then
    assert response.status_code == 400
    assert response.json()['url'] == ["L'URL doit commencer par \"http://\" ou \"https://\""]


@clean_database
@pytest.mark.standalone
def test_post_thing_returns_201_when_creating_new_thing(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    thing = create_thing()
    PcObject.check_and_save(user, venue, thing)
    thing_json = {'thumbCount': 0,
                  'type': 'ThingType.JEUX_VIDEO',
                  'name': 'Les lapins crétins',
                  'mediaUrls': 'http://media.url',
                  'url': 'http://jeux.fr/offre',
                  'isNational': False,
                  'venueId': humanize(venue.id),
                  'bookingEmail': 'offer@email.com'
                  }
    auth_request = req_with_auth(email=user.email, password='P@55W0rd!')

    # When
    response = auth_request.post(API_URL + '/things/', json=thing_json)

    # Then
    assert response.status_code == 201
    thing_id = dehumanize(response.json()['id'])
    offer = Offer.query.filter(Offer.thingId == thing_id).first()
    assert offer.bookingEmail == 'offer@email.com'


@clean_database
@pytest.mark.standalone
def test_post_thing_returns_201_when_creating_new_thing_without_booking_email(app):
    # Given
    user = create_user(password='P@55W0rd!')
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    thing = create_thing()
    PcObject.check_and_save(user, venue, thing)
    thing_json = {'thumbCount': 0,
                  'type': 'ThingType.JEUX_VIDEO',
                  'name': 'Les lapins crétins',
                  'mediaUrls': 'http://media.url',
                  'url': 'http://jeux.fr/offre',
                  'isNational': False,
                  'venueId': humanize(venue.id)
                  }
    auth_request = req_with_auth(email=user.email, password='P@55W0rd!')

    # When
    response = auth_request.post(API_URL + '/things/', json=thing_json)

    # Then
    assert response.status_code == 201
    thing_id = dehumanize(response.json()['id'])
    offer = Offer.query.filter(Offer.thingId == thing_id).first()
    assert offer.bookingEmail == None


